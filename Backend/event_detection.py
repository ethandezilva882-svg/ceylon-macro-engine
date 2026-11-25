"""
Backend/event_detection.py

Macro event detection (fills the macro_events table). The detect_* functions
are pure (DataFrames in, list of event dicts out) so they can be unit tested.
run_detection() is the DB wrapper and is idempotent: re-running never
duplicates an event already stored for the same (date, event_type).

Thresholds (from the schema doc):
- RATE_HIKE / RATE_CUT: SDFR moves by >= 50 bps in one decision
- LKR_DEPRECIATION: USD/LKR rises >= 5% within a 30-day window
- INFLATION_SPIKE: month-on-month CCPI change >= 5%

INFLATION_NORMALISATION is deliberately not implemented: it has no precise
definition yet and inflation_data only holds ~16 months of history.

Run manually with: python -m Backend.event_detection
"""

import pandas as pd

RATE_MOVE_BPS = 50
FX_DEPRECIATION_PCT = 5.0
FX_WINDOW_DAYS = 30
CPI_MOM_SPIKE_PCT = 5.0
SOURCE = "Detected from CBSL data"


def _d(value):
    return pd.Timestamp(value).date()


def detect_rate_events(rates_df: pd.DataFrame) -> list[dict]:
    if rates_df.empty:
        return []
    df = rates_df.sort_values("date").reset_index(drop=True)
    events = []
    for i in range(1, len(df)):
        prev_rate = float(df.loc[i - 1, "sdfr"])
        cur_rate = float(df.loc[i, "sdfr"])
        change_bps = round((cur_rate - prev_rate) * 100)
        if abs(change_bps) < RATE_MOVE_BPS:
            continue
        hike = change_bps > 0
        verb = "raised" if hike else "cut"
        events.append({
            "date": _d(df.loc[i, "date"]),
            "event_type": "RATE_HIKE" if hike else "RATE_CUT",
            "title": f"CBSL {verb} SDFR by {abs(change_bps)} bps to {cur_rate:.2f}%",
            "description": (
                f"CBSL {verb} the Standing Deposit Facility Rate from "
                f"{prev_rate:.2f}% to {cur_rate:.2f}% ({abs(change_bps)} basis points)."
            ),
            "impact": "neutral",
            "source": SOURCE,
        })
    return events


def detect_fx_events(exchange_df: pd.DataFrame) -> list[dict]:
    """exchange_df: columns date, rate (LKR per 1 USD). A rising rate means LKR weakened."""
    if exchange_df.empty:
        return []
    df = exchange_df.sort_values("date").reset_index(drop=True)
    dates = pd.to_datetime(df["date"])
    rates = df["rate"].astype(float)
    events = []
    last_event = None
    for i in range(len(df)):
        cutoff = dates[i] - pd.Timedelta(days=FX_WINDOW_DAYS)
        j = int(dates.searchsorted(cutoff, side="left"))
        if j >= i:
            continue
        base = rates[j]
        if base <= 0:
            continue
        pct = (rates[i] - base) / base * 100
        cooled_down = last_event is None or (dates[i] - last_event).days > FX_WINDOW_DAYS
        if pct >= FX_DEPRECIATION_PCT and cooled_down:
            events.append({
                "date": dates[i].date(),
                "event_type": "LKR_DEPRECIATION",
                "title": f"LKR weakened {pct:.1f}% against USD in 30 days",
                "description": (
                    f"USD/LKR rose from {base:.2f} to {rates[i]:.2f} "
                    f"({pct:.1f}%) within a {FX_WINDOW_DAYS}-day window."
                ),
                "impact": "negative",
                "source": SOURCE,
            })
            last_event = dates[i]
    return events


def detect_inflation_events(inflation_df: pd.DataFrame) -> list[dict]:
    """inflation_df: columns date, ccpi (index level). Uses month-on-month change."""
    if inflation_df.empty:
        return []
    df = inflation_df.dropna(subset=["ccpi"]).sort_values("date").reset_index(drop=True)
    events = []
    for i in range(1, len(df)):
        prev_val = float(df.loc[i - 1, "ccpi"])
        cur_val = float(df.loc[i, "ccpi"])
        if prev_val <= 0:
            continue
        mom = (cur_val - prev_val) / prev_val * 100
        if mom >= CPI_MOM_SPIKE_PCT:
            events.append({
                "date": _d(df.loc[i, "date"]),
                "event_type": "INFLATION_SPIKE",
                "title": f"CCPI jumped {mom:.1f}% month-on-month",
                "description": (
                    f"The Colombo CPI index rose from {prev_val:.1f} to {cur_val:.1f} "
                    f"in one month ({mom:.1f}%)."
                ),
                "impact": "negative",
                "source": SOURCE,
            })
    return events


def run_detection() -> int:
    from Backend.database import SessionLocal
    from Backend.models import CbslRate, InflationData, ExchangeRate, MacroEvent

    db = SessionLocal()
    try:
        rates_df = pd.DataFrame(
            [{"date": r.date, "sdfr": float(r.sdfr)}
             for r in db.query(CbslRate).order_by(CbslRate.date)]
        )
        fx_df = pd.DataFrame(
            [{"date": r.date, "rate": float(r.rate)}
             for r in db.query(ExchangeRate).filter(ExchangeRate.currency == "USD").order_by(ExchangeRate.date)]
        )
        infl_df = pd.DataFrame(
            [{"date": r.date, "ccpi": float(r.ccpi) if r.ccpi is not None else None}
             for r in db.query(InflationData).order_by(InflationData.date)]
        )

        detected = (
            detect_rate_events(rates_df)
            + detect_fx_events(fx_df)
            + detect_inflation_events(infl_df)
        )

        existing = {(e.date, e.event_type) for e in db.query(MacroEvent).all()}
        inserted = 0
        for ev in detected:
            if (ev["date"], ev["event_type"]) in existing:
                continue
            db.add(MacroEvent(**ev))
            existing.add((ev["date"], ev["event_type"]))
            inserted += 1
        db.commit()
        print(f"Detected {len(detected)} events, inserted {inserted} new, {len(detected) - inserted} already stored.")
        return inserted
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_detection()
