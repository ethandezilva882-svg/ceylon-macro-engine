import pandas as pd

from Backend.event_detection import (
    detect_rate_events,
    detect_fx_events,
    detect_inflation_events,
)


def test_rate_hike_detected():
    df = pd.DataFrame({"date": ["2022-04-01", "2022-04-08"], "sdfr": [13.5, 14.5]})
    events = detect_rate_events(df)
    assert len(events) == 1
    assert events[0]["event_type"] == "RATE_HIKE"
    assert "100 bps" in events[0]["title"]


def test_rate_cut_detected():
    df = pd.DataFrame({"date": ["2023-03-01", "2023-06-01"], "sdfr": [15.5, 14.5]})
    events = detect_rate_events(df)
    assert [e["event_type"] for e in events] == ["RATE_CUT"]


def test_small_rate_move_ignored():
    df = pd.DataFrame({"date": ["2023-03-01", "2023-06-01"], "sdfr": [10.0, 10.25]})
    assert detect_rate_events(df) == []


def test_rate_events_empty_input():
    assert detect_rate_events(pd.DataFrame()) == []


def test_fx_depreciation_detected_once_with_cooldown():
    dates = pd.date_range("2022-03-01", periods=20, freq="D")
    rates = [200.0] * 5 + [260.0] * 15  # +30% jump on day 6, then flat
    df = pd.DataFrame({"date": dates, "rate": rates})
    events = detect_fx_events(df)
    assert len(events) == 1
    assert events[0]["event_type"] == "LKR_DEPRECIATION"
    assert events[0]["impact"] == "negative"


def test_fx_slow_drift_not_flagged():
    dates = pd.date_range("2022-01-01", periods=120, freq="D")
    rates = [200.0 + i * 0.1 for i in range(120)]  # ~1.5% per 30 days
    df = pd.DataFrame({"date": dates, "rate": rates})
    assert detect_fx_events(df) == []


def test_fx_appreciation_not_flagged():
    dates = pd.date_range("2022-03-01", periods=20, freq="D")
    rates = [260.0] * 5 + [200.0] * 15
    assert detect_fx_events(pd.DataFrame({"date": dates, "rate": rates})) == []


def test_inflation_spike_detected():
    df = pd.DataFrame({"date": ["2022-05-01", "2022-06-01"], "ccpi": [100.0, 106.0]})
    events = detect_inflation_events(df)
    assert len(events) == 1
    assert events[0]["event_type"] == "INFLATION_SPIKE"


def test_normal_inflation_not_flagged():
    df = pd.DataFrame({"date": ["2022-05-01", "2022-06-01"], "ccpi": [100.0, 103.0]})
    assert detect_inflation_events(df) == []


def test_inflation_handles_missing_values():
    df = pd.DataFrame({"date": ["2022-05-01", "2022-06-01"], "ccpi": [None, 100.0]})
    assert detect_inflation_events(df) == []
