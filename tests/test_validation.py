import datetime

import pytest

from Scrapers.validation import (
    ValidationError,
    validate_date,
    validate_numeric_range,
    validate_not_empty_string,
    log_skip,
    SDFR_SLFR_RANGE,
    CPI_INDEX_RANGE,
    CPI_YOY_RANGE,
    EXCHANGE_RATE_RANGE,
)


# ---------- validate_date ----------

def test_validate_date_accepts_normal_date():
    d = datetime.date(2023, 5, 1)
    assert validate_date(d) == d


def test_validate_date_converts_datetime_to_date():
    result = validate_date(datetime.datetime(2023, 5, 1, 14, 30))
    assert result == datetime.date(2023, 5, 1)
    assert type(result) is datetime.date


def test_validate_date_accepts_today():
    today = datetime.date.today()
    assert validate_date(today) == today


def test_validate_date_rejects_none():
    with pytest.raises(ValidationError, match="missing"):
        validate_date(None)


def test_validate_date_rejects_string():
    with pytest.raises(ValidationError, match="not a valid date"):
        validate_date("2023-05-01")


def test_validate_date_rejects_future():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    with pytest.raises(ValidationError, match="future"):
        validate_date(tomorrow)


def test_validate_date_rejects_too_old():
    with pytest.raises(ValidationError, match="before"):
        validate_date(datetime.date(1979, 12, 31))


def test_validate_date_accepts_min_boundary():
    d = datetime.date(1980, 1, 1)
    assert validate_date(d) == d


def test_validate_date_error_uses_field_name():
    with pytest.raises(ValidationError, match="my_field"):
        validate_date(None, "my_field")


# ---------- validate_numeric_range ----------

def test_numeric_accepts_value_in_range():
    assert validate_numeric_range(8.25, 0.0, 30.0) == 8.25


def test_numeric_returns_float():
    result = validate_numeric_range(5, 0.0, 30.0)
    assert isinstance(result, float)
    assert result == 5.0


def test_numeric_accepts_numeric_string():
    assert validate_numeric_range("5.5", 0.0, 30.0) == 5.5


def test_numeric_boundaries_are_inclusive():
    assert validate_numeric_range(0.0, 0.0, 30.0) == 0.0
    assert validate_numeric_range(30.0, 0.0, 30.0) == 30.0


def test_numeric_rejects_just_above_max():
    with pytest.raises(ValidationError, match="outside plausible range"):
        validate_numeric_range(30.01, 0.0, 30.0)


def test_numeric_rejects_just_below_min():
    with pytest.raises(ValidationError, match="outside plausible range"):
        validate_numeric_range(-0.01, 0.0, 30.0)


def test_numeric_rejects_none():
    with pytest.raises(ValidationError, match="missing"):
        validate_numeric_range(None, 0.0, 30.0)


def test_numeric_rejects_nan():
    with pytest.raises(ValidationError, match="NaN"):
        validate_numeric_range(float("nan"), 0.0, 30.0)


def test_numeric_rejects_non_numeric_string():
    with pytest.raises(ValidationError, match="not numeric"):
        validate_numeric_range("abc", 0.0, 30.0)


def test_numeric_error_uses_field_name():
    with pytest.raises(ValidationError, match="sdfr"):
        validate_numeric_range(99, 0.0, 30.0, "sdfr")


# ---------- the rule from the tech doc: SDFR > 30 or < 0 is suspicious ----------

def test_sdfr_range_constant_matches_tech_doc():
    assert SDFR_SLFR_RANGE == (0.0, 30.0)


@pytest.mark.parametrize("bad", [31, 45.5, -1, -0.5])
def test_sdfr_out_of_range_rejected(bad):
    with pytest.raises(ValidationError):
        validate_numeric_range(bad, *SDFR_SLFR_RANGE, "sdfr")


@pytest.mark.parametrize("good", [0, 5.5, 8.25, 14.5, 30])
def test_sdfr_plausible_values_accepted(good):
    assert validate_numeric_range(good, *SDFR_SLFR_RANGE, "sdfr") == float(good)


# ---------- validate_not_empty_string ----------

def test_string_accepts_and_strips():
    assert validate_not_empty_string("  USD  ") == "USD"


@pytest.mark.parametrize("bad", [None, "", "   ", "nan", "NaN", "NAN"])
def test_string_rejects_empty_or_nan(bad):
    with pytest.raises(ValidationError):
        validate_not_empty_string(bad, "currency")


# ---------- the other range constants ----------

def test_other_range_constants_are_sane():
    assert CPI_INDEX_RANGE[0] < CPI_INDEX_RANGE[1]
    assert CPI_YOY_RANGE[0] < 0 < CPI_YOY_RANGE[1]
    assert EXCHANGE_RATE_RANGE[0] < EXCHANGE_RATE_RANGE[1]
    # real CCPI value from the live data must pass
    assert validate_numeric_range(207.7, *CPI_INDEX_RANGE, "ccpi") == 207.7
    # real USD rate from the live data must pass
    assert validate_numeric_range(424.283, *EXCHANGE_RATE_RANGE, "usd") == 424.283


# ---------- log_skip ----------

def test_log_skip_format(capsys):
    log_skip("row date=2023-01-01", ValidationError("sdfr is NaN"))
    out = capsys.readouterr().out
    assert "[SKIPPED]" in out
    assert "row date=2023-01-01" in out
    assert "sdfr is NaN" in out


# ---------- ValidationError is catchable so scrapers can skip, not crash ----------

def test_validation_error_is_an_exception():
    assert issubclass(ValidationError, Exception)
