"""
Backend/routers/rates.py

Public endpoint for CBSL policy rates (t2-3).
GET /api/rates?from=YYYY-MM-DD&to=YYYY-MM-DD
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import CbslRate
from Backend.schemas import CbslRateOut

router = APIRouter()


@router.get("/rates", response_model=list[CbslRateOut])
def get_rates(
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    query = db.query(CbslRate)
    if date_from:
        query = query.filter(CbslRate.date >= date_from)
    if date_to:
        query = query.filter(CbslRate.date <= date_to)
    return query.order_by(CbslRate.date).all()
