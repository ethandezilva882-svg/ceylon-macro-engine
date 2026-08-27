from sqlalchemy import (
    Column, Integer, Numeric, String, Date,
    Text, DateTime, CheckConstraint,
    UniqueConstraint, Index, ForeignKey
)
from sqlalchemy.sql import func
from .database import Base


class CbslRate(Base):
    __tablename__ = "cbsl_rates"

    id         = Column(Integer, primary_key=True)
    date       = Column(Date, nullable=False, unique=True)
    sdfr       = Column(Numeric(5, 2), nullable=False)
    slfr       = Column(Numeric(5, 2), nullable=False)
    bank_rate  = Column(Numeric(5, 2))
    change_bps = Column(Integer, default=0)
    notes      = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InflationData(Base):
    __tablename__ = "inflation_data"

    id         = Column(Integer, primary_key=True)
    date       = Column(Date, nullable=False, unique=True)
    ncpi       = Column(Numeric(8, 2))
    ccpi       = Column(Numeric(8, 2))
    ncpi_yoy   = Column(Numeric(6, 2))
    ccpi_yoy   = Column(Numeric(6, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        UniqueConstraint("date", "currency", name="uq_exchange_date_currency"),
        Index("idx_exchange_rates_currency", "currency"),
        Index("idx_exchange_rates_date", "date"),
    )

    id         = Column(Integer, primary_key=True)
    date       = Column(Date, nullable=False)
    currency   = Column(String(10), nullable=False)
    rate       = Column(Numeric(12, 4), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MacroEvent(Base):
    __tablename__ = "macro_events"
    __table_args__ = (
        CheckConstraint("impact IN ('positive', 'negative', 'neutral')", name="ck_impact"),
        Index("idx_macro_events_type", "event_type"),
        Index("idx_macro_events_date", "date"),
    )

    id          = Column(Integer, primary_key=True)
    date        = Column(Date, nullable=False)
    event_type  = Column(String(50), nullable=False)
    title       = Column(String(200), nullable=False)
    description = Column(Text)
    impact      = Column(String(10))
    source      = Column(String(200))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_email", "email"),
    )

    id              = Column(Integer, primary_key=True)
    email           = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Basket(Base):
    __tablename__ = "baskets"

    id                 = Column(Integer, primary_key=True)
    user_id            = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    food_weight        = Column(Numeric(5, 2), nullable=False, default=40.00)
    transport_weight   = Column(Numeric(5, 2), nullable=False, default=15.00)
    housing_weight     = Column(Numeric(5, 2), nullable=False, default=20.00)
    healthcare_weight  = Column(Numeric(5, 2), nullable=False, default=8.00)
    education_weight   = Column(Numeric(5, 2), nullable=False, default=7.00)
    clothing_weight    = Column(Numeric(5, 2), nullable=False, default=5.00)
    other_weight       = Column(Numeric(5, 2), nullable=False, default=5.00)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())
    updated_at         = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
