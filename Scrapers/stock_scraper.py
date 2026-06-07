import requests
import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from Backend.database import SessionLocal
from Backend.models import StockPrice

TRADE_SUMMARY_URL = "https://www.cse.lk/api/tradeSummary"

HEADERS = {
    'Referer': 'https://www.cse.lk/equity/trade-summary',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

# Only scrape these symbols -- your holdings plus major indices
TARGET_SYMBOLS = {
    "JKH.N0000", "HNB.N0000", "DIAL.N0000",
    "SPEN.N0000", "TKYO.N0000", "TKYO.X0000",
}


def fetch_trade_summary():
    print("Fetching trade summary from CSE...")
    r = requests.post(TRADE_SUMMARY_URL, data={}, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    records = data.get("reqTradeSummery", [])
    print(f"Fetched {len(records)} records.")
    return records


def seed_stock_prices(target_symbols=None):
    records = fetch_trade_summary()
    if not records:
        print("No data returned.")
        return

    today = datetime.date.today()
    db = SessionLocal()
    inserted = 0
    skipped = 0

    try:
        for rec in records:
            symbol = rec.get("symbol")
            if target_symbols and symbol not in target_symbols:
                continue

            close = rec.get("closingPrice") or rec.get("price")
            if not close:
                continue

            existing = db.query(StockPrice).filter(
                StockPrice.date == today,
                StockPrice.symbol == symbol
            ).first()

            if existing:
                skipped += 1
                continue

            db.add(StockPrice(
                date=today,
                symbol=symbol,
                open=rec.get("open"),
                high=rec.get("high"),
                low=rec.get("low"),
                close=close,
                volume=rec.get("sharevolume", 0),
            ))
            inserted += 1

        db.commit()
        print(f"\nDone. Inserted: {inserted}, Skipped: {skipped}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_stock_prices(target_symbols=TARGET_SYMBOLS)