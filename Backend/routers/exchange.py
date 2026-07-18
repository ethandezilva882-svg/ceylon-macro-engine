"""
Backend/routers/exchange.py

Public endpoint for exchange rates (t2-3).
GET /api/exchange?currency=USD&from=YYYY-MM-DD&to=YYYY-MM-DD
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import ExchangeRate
from Backend.schemas import ExchangeRateOut

router = APIRouter()


@router.get("/exchange", response_model=list[ExchangeRateOut])
def get_exchange(
    currency: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    query = db.query(ExchangeRate)
    if currency:
        query = query.filter(ExchangeRate.currency == currency.upper())
    if date_from:
        query = query.filter(ExchangeRate.date >= date_from)
    if date_to:
        query = query.filter(ExchangeRate.date <= date_to)
    return query.order_by(ExchangeRate.date).all()
