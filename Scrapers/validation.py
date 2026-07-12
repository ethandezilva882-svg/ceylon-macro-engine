"""
Shared validation helpers for all scrapers (CBSL rates, inflation, exchange rates).

Goal: reject bad records before they hit the DB, log why, and skip them instead of
crashing the whole scraper run. Never let a scraper insert a null on a required
field or a value outside a plausible range.
"""

import datetime
import math


class ValidationError(Exception):
    """Raised when a single record fails validation. Callers should catch this,
    log it, and skip the record rather than let it propagate."""
    pass


MIN_VALID_DATE = datetime.date(1980, 1, 1)


def validate_date(value, field_name="date"):
    """
    Ensures value is a real date, not None, not in the future, not absurdly old.
    Returns the date on success, raises ValidationError on failure.
    """
    if value is None:
        raise ValidationError(f"{field_name} is missing (None)")

    if isinstance(value, datetime.datetime):
        value = value.date()

    if not isinstance(value, datetime.date):
        raise ValidationError(f"{field_name} is not a valid date object: {value!r}")

    if value < MIN_VALID_DATE:
        raise ValidationError(f"{field_name} {value} is before {MIN_VALID_DATE}, looks wrong")

    if value > datetime.date.today():
        raise ValidationError(f"{field_name} {value} is in the future")

    return value


def validate_numeric_range(value, min_val, max_val, field_name="value"):
    """
    Ensures value is a real number, not None/NaN, and within [min_val, max_val].
    Returns the float on success, raises ValidationError on failure.
    """
    if value is None:
        raise ValidationError(f"{field_name} is missing (None)")

    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} is not numeric: {value!r}")

    if math.isnan(value):
        raise ValidationError(f"{field_name} is NaN")

    if value < min_val or value > max_val:
        raise ValidationError(
            f"{field_name} = {value} is outside plausible range [{min_val}, {max_val}]"
        )

    return value


def validate_not_empty_string(value, field_name="value"):
    """Ensures a string field is present and non-blank (e.g. currency codes)."""
    if value is None:
        raise ValidationError(f"{field_name} is missing (None)")

    value = str(value).strip()
    if not value or value.lower() == "nan":
        raise ValidationError(f"{field_name} is empty or 'nan'")

    return value


# --- Domain-specific range constants, so scrapers don't hardcode magic numbers ---

SDFR_SLFR_RANGE = (0.0, 30.0)          # CBSL policy rates, percent
CPI_INDEX_RANGE = (0.0, 1000.0)        # CCPI/NCPI index values
CPI_YOY_RANGE = (-50.0, 200.0)         # year-on-year inflation %, generous either side
EXCHANGE_RATE_RANGE = (0.0, 2000.0)    # LKR per unit foreign currency, covers all 14 currencies


def log_skip(record_label, error):
    """Consistent log format when a record gets skipped."""
    print(f"  [SKIPPED] {record_label}: {error}")
