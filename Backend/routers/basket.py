"""
Backend/routers/basket.py

Personal basket endpoints (t2-6). Auth-protected, one basket per user.

GET /basket: 404 if the user has no basket yet.
PUT /basket: upsert, creates if missing, updates if present. Enforces
weights sum to 100 via BasketIn's model validator.
GET /basket/impact: honest reduced version. inflation_data only has
headline CCPI/NCPI, no category breakdown exists yet (open question
from the PRD, t1-13), so this returns the basket plus official CPI
change over the period, NOT a real personalized inflation rate. Says
so explicitly in the response rather than faking a number.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import Basket, InflationData, User
from Backend.schemas import BasketIn, BasketOut, BasketImpactOut
from Backend.auth import get_current_user

router = APIRouter()


@router.get("/basket", response_model=BasketOut)
def get_basket(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    basket = db.query(Basket).filter(Basket.user_id == current_user.id).first()
    if not basket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No basket found for this user. Create one with PUT /api/basket.",
        )
    return basket


@router.put("/basket", response_model=BasketOut)
def upsert_basket(
    payload: BasketIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    basket = db.query(Basket).filter(Basket.user_id == current_user.id).first()

    if basket:
        basket.food_weight = payload.food_weight
        basket.transport_weight = payload.transport_weight
        basket.housing_weight = payload.housing_weight
        basket.healthcare_weight = payload.healthcare_weight
        basket.education_weight = payload.education_weight
        basket.clothing_weight = payload.clothing_weight
        basket.other_weight = payload.other_weight
    else:
        basket = Basket(
            user_id=current_user.id,
            food_weight=payload.food_weight,
            transport_weight=payload.transport_weight,
            housing_weight=payload.housing_weight,
            healthcare_weight=payload.healthcare_weight,
            education_weight=payload.education_weight,
            clothing_weight=payload.clothing_weight,
            other_weight=payload.other_weight,
        )
        db.add(basket)

    db.commit()
    db.refresh(basket)
    return basket


@router.get("/basket/impact", response_model=BasketImpactOut)
def get_basket_impact(
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    basket = db.query(Basket).filter(Basket.user_id == current_user.id).first()
    if not basket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No basket found for this user. Create one with PUT /api/basket.",
        )

    query = db.query(InflationData).filter(InflationData.ccpi.isnot(None))
    if date_from:
        query = query.filter(InflationData.date >= date_from)
    if date_to:
        query = query.filter(InflationData.date <= date_to)

    rows = query.order_by(InflationData.date).all()

    if not rows:
        return BasketImpactOut(basket=basket, period_from=date_from, period_to=date_to)

    start_row = rows[0]
    end_row = rows[-1]
    start_val = float(start_row.ccpi)
    end_val = float(end_row.ccpi)
    pct_change = ((end_val - start_val) / start_val) * 100 if start_val else None

    return BasketImpactOut(
        basket=basket,
        period_from=start_row.date,
        period_to=end_row.date,
        official_ccpi_start=start_val,
        official_ccpi_end=end_val,
        official_inflation_pct=round(pct_change, 2) if pct_change is not None else None,
    )
