from sqlalchemy import (
    Column, Integer, Numeric, String, Date,
    Text, BigInteger, DateTime, CheckConstraint,
    UniqueConstraint, Index, Computed
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


class LkrUsd(Base):
    __tablename__ = "lkr_usd"

    id         = Column(Integer, primary_key=True)
    date       = Column(Date, nullable=False, unique=True)
    rate       = Column(Numeric(10, 4), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StockPrice(Base):
    __tablename__ = "stock_prices"
    __table_args__ = (
        UniqueConstraint("date", "symbol", name="uq_stock_date_symbol"),
        Index("idx_stock_prices_symbol", "symbol"),
        Index("idx_stock_prices_date", "date"),
    )

    id         = Column(Integer, primary_key=True)
    date       = Column(Date, nullable=False)
    symbol     = Column(String(20), nullable=False)
    open       = Column(Numeric(12, 2))
    high       = Column(Numeric(12, 2))
    low        = Column(Numeric(12, 2))
    close      = Column(Numeric(12, 2), nullable=False)
    volume     = Column(BigInteger, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SectorIndex(Base):
    __tablename__ = "sector_indices"
    __table_args__ = (
        UniqueConstraint("date", "sector", name="uq_sector_date"),
        Index("idx_sector_indices_sector", "sector"),
    )

    id          = Column(Integer, primary_key=True)
    date        = Column(Date, nullable=False)
    sector      = Column(String(60), nullable=False)
    index_value = Column(Numeric(12, 2), nullable=False)
    change_pct  = Column(Numeric(6, 2))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class ForeignFlow(Base):
    __tablename__ = "foreign_flow"

    id         = Column(Integer, primary_key=True)
    date       = Column(Date, nullable=False, unique=True)
    buy_value  = Column(Numeric(15, 2), nullable=False, default=0)
    sell_value = Column(Numeric(15, 2), nullable=False, default=0)
    net_flow   = Column(Numeric(15, 2), Computed("buy_value - sell_value", persisted=True))
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