import requests
import pandas as pd
from io import BytesIO
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from Backend.database import SessionLocal
from Backend.models import CbslRate

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

    # Block 1: rows 4-102 (pre-OPR era)
    block1 = df.iloc[4:103, [1, 2, 3]].copy()
    block1.columns = ["date", "sdfr", "slfr"]

    # Block 2: rows 109-111 (post-OPR derived SDFR/SLFR)
    block2 = df.iloc[109:112, [1, 2, 3]].copy()
    block2.columns = ["date", "sdfr", "slfr"]

    combined = pd.concat([block1, block2], ignore_index=True)

    # Drop rows where date or both rates are NaN
    combined = combined.dropna(subset=["date", "sdfr", "slfr"], how="any")

    # Strip " (Close of Business)" and similar suffixes from date strings
    combined["date"] = combined["date"].astype(str).str.replace(r"\s*\(.*?\)", "", regex=True).str.strip()

    # Parse dates (format is DD.MM.YYYY)
    combined["date"] = pd.to_datetime(combined["date"], format="%d.%m.%Y", errors="coerce")

    # Drop any rows where date parsing failed
    combined = combined.dropna(subset=["date"])

    # Convert rates to float
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
    skipped = 0

    try:
        for _, row in df.iterrows():
            existing = db.query(CbslRate).filter(CbslRate.date == row["date"].date()).first()
            if existing:
                skipped += 1
                continue

            record = CbslRate(
                date=row["date"].date(),
                sdfr=row["sdfr"],
                slfr=row["slfr"],
            )
            db.add(record)
            inserted += 1

        db.commit()
        print(f"\nDone. Inserted: {inserted}, Skipped (already exist): {skipped}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_cbsl_rates()