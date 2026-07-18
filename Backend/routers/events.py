"""
Backend/routers/events.py

Public endpoint for macro events feed (t2-3).
GET /api/events?from=YYYY-MM-DD&to=YYYY-MM-DD
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import MacroEvent
from Backend.schemas import MacroEventOut

router = APIRouter()


@router.get("/events", response_model=list[MacroEventOut])
def get_events(
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    query = db.query(MacroEvent)
    if date_from:
        query = query.filter(MacroEvent.date >= date_from)
    if date_to:
        query = query.filter(MacroEvent.date <= date_to)
    return query.order_by(MacroEvent.date).all()
