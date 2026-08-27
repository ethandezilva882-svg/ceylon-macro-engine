"""
Backend/schemas.py

Pydantic v2 response schemas for public API endpoints (t2-2).
One schema per model in Backend/models.py, matching field-for-field.
Auth/basket schemas (t2-5, t2-6) get added separately when those tickets start.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CbslRateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    sdfr: Decimal
    slfr: Decimal
    bank_rate: Optional[Decimal] = None
    change_bps: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime


class InflationDataOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    ncpi: Optional[Decimal] = None
    ccpi: Optional[Decimal] = None
    ncpi_yoy: Optional[Decimal] = None
    ccpi_yoy: Optional[Decimal] = None
    created_at: datetime


class ExchangeRateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    currency: str
    rate: Decimal
    created_at: datetime


class MacroEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    event_type: str
    title: str
    description: Optional[str] = None
    impact: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime


class SummaryOut(BaseModel):
    """Latest values for all three indicators, per /api/summary."""
    model_config = ConfigDict(from_attributes=True)

    latest_rate: Optional[CbslRateOut] = None
    latest_inflation: Optional[InflationDataOut] = None
    latest_exchange_rates: list[ExchangeRateOut] = []


class RateInflationPoint(BaseModel):
    month: str
    rate: float
    inflation: float


class RateInflationCorrelationOut(BaseModel):
    correlation: Optional[float] = None
    sample_size: int
    lag_months: int
    points: list[RateInflationPoint] = []


class FxInflationPoint(BaseModel):
    month: str
    fx_change_pct: float
    inflation: float


class FxInflationCorrelationOut(BaseModel):
    correlation: Optional[float] = None
    sample_size: int
    window_days: int
    points: list[FxInflationPoint] = []


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class BasketIn(BaseModel):
    food_weight: float = Field(ge=0, le=100)
    transport_weight: float = Field(ge=0, le=100)
    housing_weight: float = Field(ge=0, le=100)
    healthcare_weight: float = Field(ge=0, le=100)
    education_weight: float = Field(ge=0, le=100)
    clothing_weight: float = Field(ge=0, le=100)
    other_weight: float = Field(ge=0, le=100)

    @model_validator(mode="after")
    def weights_sum_to_100(self):
        total = (
            self.food_weight + self.transport_weight + self.housing_weight
            + self.healthcare_weight + self.education_weight
            + self.clothing_weight + self.other_weight
        )
        if abs(total - 100) > 0.01:
            raise ValueError(f"Basket weights must sum to 100, got {total}")
        return self


class BasketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    food_weight: Decimal
    transport_weight: Decimal
    housing_weight: Decimal
    healthcare_weight: Decimal
    education_weight: Decimal
    clothing_weight: Decimal
    other_weight: Decimal
    created_at: datetime
    updated_at: datetime


class BasketImpactOut(BaseModel):
    basket: BasketOut
    period_from: Optional[date] = None
    period_to: Optional[date] = None
    official_ccpi_start: Optional[float] = None
    official_ccpi_end: Optional[float] = None
    official_inflation_pct: Optional[float] = None
    note: str = (
        "Category-level inflation breakdown is not yet available. This shows "
        "your saved basket weights and the official headline CPI change over "
        "the selected period, not a personalized inflation rate."
    )
