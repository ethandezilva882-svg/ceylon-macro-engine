"""
Backend/correlation.py

Pure correlation computation functions for t2-4. Kept separate from the
router/DB layer so these can be unit tested directly on plain DataFrames.

Design choices:
- rate_vs_inflation defaults to SDFR (deposit facility rate) vs CCPI YoY.
- Rates are recorded irregularly, so they are resampled to monthly by
  taking the last known value each month and forward-filling gaps.
- lag_months shifts the rate series forward relative to inflation:
  tests whether rate at month M correlates with inflation at month M+lag.
- lkr_vs_inflation resamples exchange rate to monthly average, takes
  month-over-month percent change, correlates against CCPI YoY.
  window_days restricts to the trailing N days of history.
- Correlation is Pearson's r via pandas .corr(). No p-value since scipy
  isn't installed.
"""

import pandas as pd


def compute_rate_vs_inflation(
    rates_df: pd.DataFrame,
    inflation_df: pd.DataFrame,
    lag_months: int = 6,
    rate_col: str = "sdfr",
    inflation_col: str = "ccpi_yoy",
) -> dict:
    if rates_df.empty or inflation_df.empty:
        return {"correlation": None, "sample_size": 0, "lag_months": lag_months, "points": []}

    rates = rates_df[["date", rate_col]].copy()
    rates["date"] = pd.to_datetime(rates["date"])
    rates["month"] = rates["date"].dt.to_period("M")
    rate_monthly = rates.groupby("month")[rate_col].last()

    full_range = pd.period_range(rate_monthly.index.min(), rate_monthly.index.max(), freq="M")
    rate_monthly = rate_monthly.reindex(full_range).ffill()

    inflation = inflation_df[["date", inflation_col]].copy()
    inflation["date"] = pd.to_datetime(inflation["date"])
    inflation["month"] = inflation["date"].dt.to_period("M")
    inflation_monthly = inflation.set_index("month")[inflation_col].dropna()

    shifted_rate = rate_monthly.copy()
    shifted_rate.index = shifted_rate.index + lag_months

    merged = pd.concat(
        [shifted_rate.rename("rate"), inflation_monthly.rename("inflation")],
        axis=1,
    ).dropna()

    if len(merged) < 2:
        return {"correlation": None, "sample_size": len(merged), "lag_months": lag_months, "points": []}

    correlation = merged["rate"].corr(merged["inflation"])

    points = [
        {"month": str(idx), "rate": float(row["rate"]), "inflation": float(row["inflation"])}
        for idx, row in merged.iterrows()
    ]

    return {
        "correlation": round(float(correlation), 4) if pd.notna(correlation) else None,
        "sample_size": len(merged),
        "lag_months": lag_months,
        "points": points,
    }


def compute_lkr_vs_inflation(
    exchange_df: pd.DataFrame,
    inflation_df: pd.DataFrame,
    window_days: int = 90,
    inflation_col: str = "ccpi_yoy",
) -> dict:
    if exchange_df.empty or inflation_df.empty:
        return {"correlation": None, "sample_size": 0, "window_days": window_days, "points": []}

    exchange = exchange_df[["date", "rate"]].copy()
    exchange["date"] = pd.to_datetime(exchange["date"])
    exchange["month"] = exchange["date"].dt.to_period("M")
    monthly_avg = exchange.groupby("month")["rate"].mean()
    monthly_pct_change = monthly_avg.pct_change().dropna() * 100

    inflation = inflation_df[["date", inflation_col]].copy()
    inflation["date"] = pd.to_datetime(inflation["date"])
    inflation["month"] = inflation["date"].dt.to_period("M")
    inflation_monthly = inflation.set_index("month")[inflation_col].dropna()

    merged = pd.concat(
        [monthly_pct_change.rename("fx_change_pct"), inflation_monthly.rename("inflation")],
        axis=1,
    ).dropna()

    if merged.empty:
        return {"correlation": None, "sample_size": 0, "window_days": window_days, "points": []}

    latest_month = merged.index.max()
    cutoff = latest_month.to_timestamp() - pd.Timedelta(days=window_days)
    merged = merged[merged.index.to_timestamp() >= cutoff]

    if len(merged) < 2:
        return {"correlation": None, "sample_size": len(merged), "window_days": window_days, "points": []}

    correlation = merged["fx_change_pct"].corr(merged["inflation"])

    points = [
        {"month": str(idx), "fx_change_pct": float(row["fx_change_pct"]), "inflation": float(row["inflation"])}
        for idx, row in merged.iterrows()
    ]

    return {
        "correlation": round(float(correlation), 4) if pd.notna(correlation) else None,
        "sample_size": len(merged),
        "window_days": window_days,
        "points": points,
    }
