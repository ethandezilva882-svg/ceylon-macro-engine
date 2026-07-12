import requests
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from Backend.database import SessionLocal
from Backend.models import ExchangeRate
from Scrapers.validation import (
    validate_date, validate_numeric_range, validate_not_empty_string,
    ValidationError, EXCHANGE_RATE_RANGE, log_skip
)

EXCHANGE_PAGE_URL = "https://www.cbsl.gov.lk/en/rates-and-indicators/exchange-rates"

CURRENCIES = {
    3:  "USD",
    4:  "GBP",
    5:  "INR",
    6:  "JPY",
    7:  "EUR",
    8:  "CHF",
    9:  "AUD",
    10: "CAD",
    11: "SGD",
    12: "DKK",
    13: "HKD",
    14: "NZD",
    15: "NOK",
    16: "SEK",
}

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}


def get_download_url():
    print("Fetching exchange rate spreadsheet URL from CBSL...")
    r = requests.get(EXCHANGE_PAGE_URL, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "IF_Monthly_Average_Exchange_Rates" in href:
            url = href if href.startswith("http") else "https://www.cbsl.gov.lk" + href
            print(f"Found URL: {url}")
            return url

    return None


def parse_rates():
    url = get_download_url()
    if not url:
        print("Could not find URL.")
        return []

    print("Downloading...")
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    xl = pd.ExcelFile(BytesIO(r.content))
    df = pd.read_excel(xl, sheet_name="Avg ExRate", header=None)

    records = []
    current_year = None

    for _, row in df.iloc[8:].iterrows():
        year_val = row[1]
        if pd.notna(year_val):
            try:
                current_year = int(float(year_val))
            except (ValueError, TypeError):
                pass

        month_val = str(row[2]).strip() if pd.notna(row[2]) else ""
        if month_val not in MONTH_MAP or current_year is None:
            continue

        month = MONTH_MAP[month_val]
        date = datetime.date(current_year, month, 1)

        for col_idx, currency in CURRENCIES.items():
            val = row[col_idx]
            if pd.isna(val) or str(val).strip() in ("-", "", "nan"):
                continue
            rate = pd.to_numeric(val, errors="coerce")
            if pd.isna(rate):
                continue

            records.append({
                "date": date,
                "currency": currency,
                "rate": rate,
            })

    print(f"Parsed {len(records)} exchange rate records across {len(CURRENCIES)} currencies.")
    return records


def seed_exchange_rates():
    records = parse_rates()
    if not records:
        return

    db = SessionLocal()
    inserted = 0
    skipped_existing = 0
    skipped_invalid = 0

    try:
        for rec in records:
            label = f"date={rec['date']} currency={rec['currency']}"

            try:
                clean_date = validate_date(rec["date"], "date")
                clean_currency = validate_not_empty_string(rec["currency"], "currency")
                clean_rate = validate_numeric_range(rec["rate"], *EXCHANGE_RATE_RANGE, "rate")
            except ValidationError as e:
                log_skip(label, e)
                skipped_invalid += 1
                continue

            existing = db.query(ExchangeRate).filter(
                ExchangeRate.date == clean_date,
                ExchangeRate.currency == clean_currency
            ).first()
            if existing:
                skipped_existing += 1
                continue

            db.add(ExchangeRate(
                date=clean_date,
                currency=clean_currency,
                rate=clean_rate,
            ))
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
    seed_exchange_rates()
