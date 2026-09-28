"""
Unit tests for Backend/correlation.py.

These are pure-function tests on synthetic DataFrames. No database, no
network. They check the math and the edge cases, not real-world meaning
(the real dataset is too thin for that).
"""

import pandas as pd
import pytest

from Backend.correlation import compute_lkr_vs_inflation, compute_rate_vs_inflation

# Deliberately non-periodic so a wrong lag visibly lowers the correlation.
RATE_PATTERN = [5, 5, 7, 7, 7, 12, 12, 9, 9, 9, 6, 6, 8, 8, 14, 14, 14, 10, 10, 7, 7, 11, 11, 11]


def month_starts(start: str, n: int) -> pd.DatetimeIndex:
    return pd.date_range(start, periods=n, freq="MS")


def rates_frame(values, start="2020-01-01") -> pd.DataFrame:
    return pd.DataFrame({"date": month_starts(start, len(values)), "sdfr": values})


def inflation_frame(values, start="2020-01-01") -> pd.DataFrame:
    return pd.DataFrame({"date": month_starts(start, len(values)), "ccpi_yoy": values})


def exchange_frame(dates, rates) -> pd.DataFrame:
    return pd.DataFrame({"date": pd.to_datetime(dates), "rate": rates})


# ---------------------------------------------------------------------------
# compute_rate_vs_inflation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lag", [0, 3, 6, 12])
def test_rate_vs_inflation_recovers_the_true_lag(lag):
    """Inflation is a linear function of the rate `lag` months earlier,
    so the matching lag must give a perfect correlation."""
    n = len(RATE_PATTERN)
    rates = rates_frame(RATE_PATTERN, "2020-01-01")
    inflation_start = (pd.Timestamp("2020-01-01") + pd.DateOffset(months=lag)).strftime("%Y-%m-%d")
    inflation = inflation_frame([2 * r + 1 for r in RATE_PATTERN], inflation_start)

    result = compute_rate_vs_inflation(rates, inflation, lag_months=lag)

    assert result["correlation"] == 1.0
    assert result["sample_size"] == n
    assert result["lag_months"] == lag


def test_rate_vs_inflation_wrong_lag_gives_weaker_correlation():
    lag = 6
    rates = rates_frame(RATE_PATTERN, "2020-01-01")
    inflation = inflation_frame([2 * r + 1 for r in RATE_PATTERN], "2020-07-01")

    right = compute_rate_vs_inflation(rates, inflation, lag_months=lag)
    wrong = compute_rate_vs_inflation(rates, inflation, lag_months=lag - 3)

    assert right["correlation"] == 1.0
    assert wrong["correlation"] is not None
    assert wrong["correlation"] < 0.99


def test_rate_vs_inflation_lag_shifts_the_month_labels():
    rates = rates_frame([5, 6, 7, 8], "2020-01-01")  # Jan..Apr
    inflation = inflation_frame([1, 2, 3, 4, 5, 6], "2020-01-01")  # Jan..Jun

    result = compute_rate_vs_inflation(rates, inflation, lag_months=2)

    assert [p["month"] for p in result["points"]] == ["2020-03", "2020-04", "2020-05", "2020-06"]
    # rate from Jan lines up with inflation in Mar, and so on
    assert [p["rate"] for p in result["points"]] == [5.0, 6.0, 7.0, 8.0]
    assert [p["inflation"] for p in result["points"]] == [3.0, 4.0, 5.0, 6.0]


def test_rate_vs_inflation_takes_last_decision_in_month_and_forward_fills_gaps():
    rates = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-15", "2020-01-28", "2020-04-10"]),
            "sdfr": [5.0, 6.0, 9.0],
        }
    )
    inflation = inflation_frame([1, 2, 3, 4], "2020-01-01")  # Jan..Apr

    result = compute_rate_vs_inflation(rates, inflation, lag_months=0)

    assert [p["month"] for p in result["points"]] == ["2020-01", "2020-02", "2020-03", "2020-04"]
    # Jan uses the later (28th) decision, Feb and Mar carry it forward, Apr is the new one
    assert [p["rate"] for p in result["points"]] == [6.0, 6.0, 6.0, 9.0]


def test_rate_vs_inflation_negative_relationship_gives_negative_correlation():
    rates = rates_frame(RATE_PATTERN, "2020-01-01")
    inflation = inflation_frame([-2 * r + 50 for r in RATE_PATTERN], "2020-01-01")

    result = compute_rate_vs_inflation(rates, inflation, lag_months=0)

    assert result["correlation"] == -1.0


def test_rate_vs_inflation_constant_rate_returns_none_correlation():
    """A flat series has zero variance, so Pearson is NaN. Must come back as None, not NaN."""
    rates = rates_frame([10.0] * 6, "2020-01-01")
    inflation = inflation_frame([1, 3, 2, 5, 4, 6], "2020-01-01")

    result = compute_rate_vs_inflation(rates, inflation, lag_months=0)

    assert result["correlation"] is None
    assert result["sample_size"] == 6


def test_rate_vs_inflation_ignores_null_inflation_months():
    rates = rates_frame([5, 6, 7, 8, 9], "2020-01-01")
    inflation = inflation_frame([1.0, None, 3.0, 4.0, 5.5], "2020-01-01")

    result = compute_rate_vs_inflation(rates, inflation, lag_months=0)

    assert result["sample_size"] == 4
    assert "2020-02" not in [p["month"] for p in result["points"]]


@pytest.mark.parametrize("which", ["rates", "inflation"])
def test_rate_vs_inflation_empty_input(which):
    empty_rates = pd.DataFrame(columns=["date", "sdfr"])
    empty_inflation = pd.DataFrame(columns=["date", "ccpi_yoy"])
    rates = empty_rates if which == "rates" else rates_frame([5, 6, 7])
    inflation = empty_inflation if which == "inflation" else inflation_frame([1, 2, 3])

    result = compute_rate_vs_inflation(rates, inflation, lag_months=4)

    assert result == {"correlation": None, "sample_size": 0, "lag_months": 4, "points": []}


def test_rate_vs_inflation_single_overlapping_month_returns_none():
    rates = rates_frame([5, 6, 7], "2020-01-01")  # Jan..Mar
    inflation = inflation_frame([1, 2, 3], "2020-03-01")  # Mar..May

    result = compute_rate_vs_inflation(rates, inflation, lag_months=0)

    assert result["correlation"] is None
    assert result["sample_size"] == 1
    assert result["points"] == []


def test_rate_vs_inflation_no_overlap_returns_zero_sample():
    rates = rates_frame([5, 6, 7], "2020-01-01")
    inflation = inflation_frame([1, 2, 3], "2022-01-01")

    result = compute_rate_vs_inflation(rates, inflation, lag_months=0)

    assert result["correlation"] is None
    assert result["sample_size"] == 0


def test_rate_vs_inflation_result_shape():
    result = compute_rate_vs_inflation(
        rates_frame(RATE_PATTERN), inflation_frame([2 * r + 1 for r in RATE_PATTERN]), lag_months=0
    )

    assert set(result) == {"correlation", "sample_size", "lag_months", "points"}
    assert set(result["points"][0]) == {"month", "rate", "inflation"}
    assert isinstance(result["points"][0]["month"], str)


# ---------------------------------------------------------------------------
# compute_lkr_vs_inflation
# ---------------------------------------------------------------------------

FX_MONTHLY = [300, 306, 306, 318, 330, 330, 345, 350, 360, 360, 375, 390]  # Jan..Dec 2023


def fx_and_inflation_12_months():
    exchange = exchange_frame(month_starts("2023-01-01", 12), FX_MONTHLY)
    pct = pd.Series(FX_MONTHLY).pct_change().dropna() * 100
    # inflation exists for Feb..Dec, perfectly linear in the monthly FX change
    inflation = inflation_frame([3 * p + 2 for p in pct], "2023-02-01")
    return exchange, inflation


def test_lkr_vs_inflation_full_window_perfect_correlation():
    exchange, inflation = fx_and_inflation_12_months()

    result = compute_lkr_vs_inflation(exchange, inflation, window_days=365)

    assert result["correlation"] == 1.0
    assert result["sample_size"] == 11  # first month has no pct change, so Jan drops out
    assert result["points"][0]["month"] == "2023-02"


def test_lkr_vs_inflation_window_cutoff_drops_older_months():
    exchange, inflation = fx_and_inflation_12_months()

    result = compute_lkr_vs_inflation(exchange, inflation, window_days=90)

    # latest month is Dec 1, cutoff is Dec 1 minus 90 days = Sep 2, so Oct, Nov, Dec survive
    assert [p["month"] for p in result["points"]] == ["2023-10", "2023-11", "2023-12"]
    assert result["sample_size"] == 3
    assert result["window_days"] == 90


def test_lkr_vs_inflation_window_too_small_returns_none():
    exchange, inflation = fx_and_inflation_12_months()

    result = compute_lkr_vs_inflation(exchange, inflation, window_days=10)

    assert result["correlation"] is None
    assert result["sample_size"] == 1
    assert result["points"] == []


def test_lkr_vs_inflation_uses_monthly_average_of_daily_rates():
    exchange = exchange_frame(
        ["2023-01-05", "2023-01-25", "2023-02-10", "2023-03-10"],
        [300, 310, 315, 330],
    )  # Jan avg 305, Feb 315, Mar 330
    inflation = inflation_frame([5.0, 8.0], "2023-02-01")

    result = compute_lkr_vs_inflation(exchange, inflation, window_days=365)

    assert result["sample_size"] == 2
    assert result["points"][0]["fx_change_pct"] == pytest.approx((315 - 305) / 305 * 100)
    assert result["points"][1]["fx_change_pct"] == pytest.approx((330 - 315) / 315 * 100)


def test_lkr_vs_inflation_pegged_fx_returns_none_correlation():
    """A perfectly flat rate (a peg) means 0.0 change every month, zero variance, Pearson is NaN."""
    exchange = exchange_frame(month_starts("2023-01-01", 5), [100, 100, 100, 100, 100])
    inflation = inflation_frame([1, 3, 2, 6], "2023-02-01")

    result = compute_lkr_vs_inflation(exchange, inflation, window_days=365)

    assert result["correlation"] is None
    assert result["sample_size"] == 4


@pytest.mark.parametrize("which", ["exchange", "inflation"])
def test_lkr_vs_inflation_empty_input(which):
    empty_fx = pd.DataFrame(columns=["date", "rate"])
    empty_inflation = pd.DataFrame(columns=["date", "ccpi_yoy"])
    good_fx, good_inflation = fx_and_inflation_12_months()
    exchange = empty_fx if which == "exchange" else good_fx
    inflation = empty_inflation if which == "inflation" else good_inflation

    result = compute_lkr_vs_inflation(exchange, inflation, window_days=90)

    assert result == {"correlation": None, "sample_size": 0, "window_days": 90, "points": []}


def test_lkr_vs_inflation_no_overlap_returns_zero_sample():
    exchange = exchange_frame(month_starts("2023-01-01", 6), [300, 310, 320, 330, 340, 350])
    inflation = inflation_frame([1, 2, 3], "2025-01-01")

    result = compute_lkr_vs_inflation(exchange, inflation, window_days=90)

    assert result["correlation"] is None
    assert result["sample_size"] == 0


def test_lkr_vs_inflation_result_shape():
    exchange, inflation = fx_and_inflation_12_months()

    result = compute_lkr_vs_inflation(exchange, inflation, window_days=365)

    assert set(result) == {"correlation", "sample_size", "window_days", "points"}
    assert set(result["points"][0]) == {"month", "fx_change_pct", "inflation"}
