import pandas as pd

from Backend.correlation import compute_rate_vs_inflation, compute_lkr_vs_inflation


def test_rate_vs_inflation_empty_input():
    result = compute_rate_vs_inflation(pd.DataFrame(), pd.DataFrame(), lag_months=6)
    assert result["correlation"] is None
    assert result["sample_size"] == 0
    assert result["lag_months"] == 6


def test_rate_vs_inflation_perfect_lag_alignment():
    # Inflation at month M+3 equals the rate at month M, so correlation is exactly 1.
    rates = pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=12, freq="MS"),
        "sdfr": list(range(1, 13)),
    })
    inflation = pd.DataFrame({
        "date": pd.date_range("2020-04-01", periods=12, freq="MS"),
        "ccpi_yoy": list(range(1, 13)),
    })
    result = compute_rate_vs_inflation(rates, inflation, lag_months=3)
    assert result["sample_size"] == 12
    assert result["correlation"] == 1.0


def test_rate_vs_inflation_too_few_points_returns_none():
    rates = pd.DataFrame({"date": ["2020-01-01"], "sdfr": [5.0]})
    inflation = pd.DataFrame({"date": ["2020-01-01"], "ccpi_yoy": [3.0]})
    result = compute_rate_vs_inflation(rates, inflation, lag_months=0)
    assert result["correlation"] is None


def test_lkr_vs_inflation_empty_input():
    result = compute_lkr_vs_inflation(pd.DataFrame(), pd.DataFrame(), window_days=90)
    assert result["correlation"] is None
    assert result["sample_size"] == 0


def _lkr_frames():
    exchange = pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=12, freq="MS"),
        "rate": [300 + i * i for i in range(12)],
    })
    inflation = pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=12, freq="MS"),
        "ccpi_yoy": [i * 1.5 for i in range(12)],
    })
    return exchange, inflation


def test_lkr_vs_inflation_window_limits_sample():
    exchange, inflation = _lkr_frames()
    narrow = compute_lkr_vs_inflation(exchange, inflation, window_days=90)
    wide = compute_lkr_vs_inflation(exchange, inflation, window_days=3650)
    assert narrow["sample_size"] == 3
    assert wide["sample_size"] == 11
    assert wide["correlation"] is not None
