import requests
import pandas as pd
from io import BytesIO
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from Backend.database import SessionLocal
from Backend.models import CbslRate
from Scrapers.validation import (
    validate_date, validate_numeric_range, ValidationError,
    SDFR_SLFR_RANGE, log_skip
)

HISTORICAL_URL = "https://www.cbsl.gov.lk/sites/default/files/cbslweb_documents/about/historical_policy_interest_rates.xlsx"


def download_excel():
    print("Downloading historical rates from CBSL...")
    response = requests.get(HISTORICAL_URL, timeout=30)
    response.raise_for_status()
    print("Download successful.")
    return BytesIO(response.content)


def parse_rates():
    data = download_excel()
    xl = pd.ExcelFile(data)
    df = pd.read_excel(xl, sheet_name="Historical Policy Rates", header=None)

    block1 = df.iloc[4:103, [1, 2, 3]].copy()
    block1.columns = ["date", "sdfr", "slfr"]

    block2 = df.iloc[109:112, [1, 2, 3]].copy()
    block2.columns = ["date", "sdfr", "slfr"]

    combined = pd.concat([block1, block2], ignore_index=True)
    combined = combined.dropna(subset=["date", "sdfr", "slfr"], how="any")
    combined["date"] = combined["date"].astype(str).str.replace(r"\s*\(.*?\)", "", regex=True).str.strip()
    combined["date"] = pd.to_datetime(combined["date"], format="%d.%m.%Y", errors="coerce")
    combined = combined.dropna(subset=["date"])
    combined["sdfr"] = pd.to_numeric(combined["sdfr"], errors="coerce")
    combined["slfr"] = pd.to_numeric(combined["slfr"], errors="coerce")
    combined = combined.dropna(subset=["sdfr", "slfr"])

    print(f"\nParsed {len(combined)} rate records.")
    print(combined.head(10))
    print("...")
    print(combined.tail(5))
    return combined


def seed_cbsl_rates():
    df = parse_rates()
    db = SessionLocal()
    inserted = 0
    skipped_existing = 0
    skipped_invalid = 0

    try:
        for _, row in df.iterrows():
            raw_date = row["date"].date()
            label = f"row date={raw_date}"

            try:
                clean_date = validate_date(raw_date, "date")
                clean_sdfr = validate_numeric_range(row["sdfr"], *SDFR_SLFR_RANGE, "sdfr")
                clean_slfr = validate_numeric_range(row["slfr"], *SDFR_SLFR_RANGE, "slfr")
            except ValidationError as e:
                log_skip(label, e)
                skipped_invalid += 1
                continue

            existing = db.query(CbslRate).filter(CbslRate.date == clean_date).first()
            if existing:
                skipped_existing += 1
                continue

            record = CbslRate(
                date=clean_date,
                sdfr=clean_sdfr,
                slfr=clean_slfr,
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
    seed_cbsl_rates()
