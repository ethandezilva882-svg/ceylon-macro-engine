"""
Backend/routers/inflation.py

Public endpoint for CPI/inflation data (t2-3).
GET /api/inflation?from=YYYY-MM-DD&to=YYYY-MM-DD&type=CCPI|NCPI
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import InflationData
from Backend.schemas import InflationDataOut

router = APIRouter()


@router.get("/inflation", response_model=list[InflationDataOut])
def get_inflation(
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
    type: Optional[str] = Query(None, pattern="^(CCPI|NCPI)$"),
    db: Session = Depends(get_db),
):
    query = db.query(InflationData)
    if date_from:
        query = query.filter(InflationData.date >= date_from)
    if date_to:
        query = query.filter(InflationData.date <= date_to)
    if type == "CCPI":
        query = query.filter(InflationData.ccpi.isnot(None))
    elif type == "NCPI":
        query = query.filter(InflationData.ncpi.isnot(None))
    return query.order_by(InflationData.date).all()
