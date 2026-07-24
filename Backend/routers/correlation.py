"""
Backend/routers/correlation.py

Public correlation endpoints (t2-4).
GET /api/correlation/rate-vs-inflation?lag_months=6
GET /api/correlation/lkr-vs-inflation?window_days=90
"""

import pandas as pd
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import CbslRate, InflationData, ExchangeRate
from Backend.schemas import RateInflationCorrelationOut, FxInflationCorrelationOut
from Backend.correlation import compute_rate_vs_inflation, compute_lkr_vs_inflation

router = APIRouter()


@router.get("/correlation/rate-vs-inflation", response_model=RateInflationCorrelationOut)
def get_rate_vs_inflation(
    lag_months: int = Query(6, ge=0, le=24),
    db: Session = Depends(get_db),
):
    rates = db.query(CbslRate).order_by(CbslRate.date).all()
    inflation = db.query(InflationData).order_by(InflationData.date).all()

    rates_df = pd.DataFrame([
        {"date": r.date, "sdfr": float(r.sdfr)} for r in rates
    ])
    inflation_df = pd.DataFrame([
        {"date": i.date, "ccpi_yoy": float(i.ccpi_yoy) if i.ccpi_yoy is not None else None}
        for i in inflation
    ])

    result = compute_rate_vs_inflation(rates_df, inflation_df, lag_months=lag_months)
    return result


@router.get("/correlation/lkr-vs-inflation", response_model=FxInflationCorrelationOut)
def get_lkr_vs_inflation(
    window_days: int = Query(90, ge=1, le=3650),
    db: Session = Depends(get_db),
):
    exchange = (
        db.query(ExchangeRate)
        .filter(ExchangeRate.currency == "USD")
        .order_by(ExchangeRate.date)
        .all()
    )
    inflation = db.query(InflationData).order_by(InflationData.date).all()

    exchange_df = pd.DataFrame([
        {"date": e.date, "rate": float(e.rate)} for e in exchange
    ])
    inflation_df = pd.DataFrame([
        {"date": i.date, "ccpi_yoy": float(i.ccpi_yoy) if i.ccpi_yoy is not None else None}
        for i in inflation
    ])

    result = compute_lkr_vs_inflation(exchange_df, inflation_df, window_days=window_days)
    return result
