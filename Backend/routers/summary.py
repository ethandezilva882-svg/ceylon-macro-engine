"""
Backend/routers/summary.py

Public endpoint for latest values across all indicators (t2-3).
GET /api/summary
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import CbslRate, InflationData, ExchangeRate
from Backend.schemas import SummaryOut

router = APIRouter()


@router.get("/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db)):
    latest_rate = db.query(CbslRate).order_by(CbslRate.date.desc()).first()
    latest_inflation = (
        db.query(InflationData).order_by(InflationData.date.desc()).first()
    )

    # Latest exchange rate per currency, not just the single latest row overall,
    # since each currency updates independently.
    latest_date_per_currency = (
        db.query(
            ExchangeRate.currency,
            db.query(ExchangeRate.date)
            .filter(ExchangeRate.currency == ExchangeRate.currency)
            .order_by(ExchangeRate.date.desc())
            .limit(1)
            .scalar_subquery()
            .label("max_date"),
        )
        .distinct(ExchangeRate.currency)
        .subquery()
    )

    latest_exchange_rates = (
        db.query(ExchangeRate)
        .join(
            latest_date_per_currency,
            (ExchangeRate.currency == latest_date_per_currency.c.currency)
            & (ExchangeRate.date == latest_date_per_currency.c.max_date),
        )
        .order_by(ExchangeRate.currency)
        .all()
    )

    return SummaryOut(
        latest_rate=latest_rate,
        latest_inflation=latest_inflation,
        latest_exchange_rates=latest_exchange_rates,
    )
