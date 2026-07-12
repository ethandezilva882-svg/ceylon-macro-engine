import requests
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
import sys
import os
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from Backend.database import SessionLocal
from Backend.models import InflationData
from Scrapers.validation import (
    validate_date, validate_numeric_range, ValidationError,
    CPI_INDEX_RANGE, CPI_YOY_RANGE, log_skip
)

PRICES_PAGE_URL = "https://www.cbsl.gov.lk/en/statistics/statistical-tables/real-sector/prices-wages-employment"

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}


def get_download_urls():
    print("Fetching download URLs from CBSL...")
    r = requests.get(PRICES_PAGE_URL, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")

    ccpi_url = None
    ncpi_url = None

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "CCPI_and_CCPI_CORE" in href and href.endswith(".xlsx"):
            ccpi_url = href if href.startswith("http") else "https://www.cbsl.gov.lk" + href
        if "NCPI_and_NCPI_CORE" in href and href.endswith(".xlsx"):
            ncpi_url = href if href.startswith("http") else "https://www.cbsl.gov.lk" + href

    print(f"CCPI URL: {ccpi_url}")
    print(f"NCPI URL: {ncpi_url}")
    return ccpi_url, ncpi_url


def parse_index(url, col_index, col_yoy, col_yoy_core, label):
    print(f"\nDownloading {label}...")
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    xl = pd.ExcelFile(BytesIO(r.content))
    sheet = xl.sheet_names[0]
    df = pd.read_excel(xl, sheet_name=sheet, header=None)

    records = []
    for _, row in df.iloc[4:].iterrows():
        period = str(row[1]).strip()
        if not period or period == "nan":
            continue

        parts = period.split()
        if len(parts) != 2:
            continue
        year_str, month_str = parts
        if month_str not in MONTH_MAP:
            continue

        try:
            year = int(year_str)
            month = MONTH_MAP[month_str]
        except ValueError:
            continue

        date = datetime.date(year, month, 1)

        index_val = pd.to_numeric(row[col_index], errors="coerce")
        yoy = pd.to_numeric(row[col_yoy], errors="coerce")
        yoy_core = pd.to_numeric(row[col_yoy_core], errors="coerce")

        records.append({
            "date": date,
            "index": index_val,
            "yoy": yoy,
            "yoy_core": yoy_core,
        })

    print(f"Parsed {len(records)} {label} records.")
    return records


def seed_inflation():
    ccpi_url, ncpi_url = get_download_urls()

    if not ccpi_url or not ncpi_url:
        print("Could not find download URLs. Check the page structure.")
        return

    ccpi_records = parse_index(ccpi_url, 2, 6, 7, "CCPI")
    ncpi_records = parse_index(ncpi_url, 2, 6, 7, "NCPI")

    ccpi_by_date = {r["date"]: r for r in ccpi_records}
    ncpi_by_date = {r["date"]: r for r in ncpi_records}
    all_dates = set(ccpi_by_date.keys()) | set(ncpi_by_date.keys())

    db = SessionLocal()
    inserted = 0
    skipped_existing = 0
    skipped_invalid = 0

    try:
        for date in sorted(all_dates):
            label = f"row date={date}"

            try:
                clean_date = validate_date(date, "date")
            except ValidationError as e:
                log_skip(label, e)
                skipped_invalid += 1
                continue

            existing = db.query(InflationData).filter(InflationData.date == clean_date).first()
            if existing:
                skipped_existing += 1
                continue

            ccpi_raw = ccpi_by_date.get(date, {})
            ncpi_raw = ncpi_by_date.get(date, {})

            def clean_optional(value, bounds, field_name):
                if value is None or pd.isna(value):
                    return None
                try:
                    return validate_numeric_range(value, *bounds, field_name)
                except ValidationError as e:
                    log_skip(f"{label} [{field_name}]", e)
                    return None

            ccpi_val = clean_optional(ccpi_raw.get("index"), CPI_INDEX_RANGE, "ccpi")
            ncpi_val = clean_optional(ncpi_raw.get("index"), CPI_INDEX_RANGE, "ncpi")
            ccpi_yoy_val = clean_optional(ccpi_raw.get("yoy"), CPI_YOY_RANGE, "ccpi_yoy")
            ncpi_yoy_val = clean_optional(ncpi_raw.get("yoy"), CPI_YOY_RANGE, "ncpi_yoy")

            if ccpi_val is None and ncpi_val is None:
                log_skip(label, "both ccpi and ncpi missing/invalid, skipping record entirely")
                skipped_invalid += 1
                continue

            record = InflationData(
                date=clean_date,
                ccpi=ccpi_val,
                ncpi=ncpi_val,
                ccpi_yoy=ccpi_yoy_val,
                ncpi_yoy=ncpi_yoy_val,
            )
            db.add(record)
            inserted += 1

        db.commit()
        print(f"\nDone. Inserted: {inserted}, Skipped (already exist): {skipped_existing}, Skipped (failed validation): {skipped_invalid}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_inflation()
