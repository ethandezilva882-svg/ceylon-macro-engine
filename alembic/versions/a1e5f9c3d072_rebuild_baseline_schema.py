"""rebuild baseline schema

Squashes the original three migrations (initial schema, lkr_usd->exchange_rates,
drop_cse_tables) into one clean baseline. Those migrations assumed cbsl_rates,
inflation_data, and macro_events already existed from manual pre-Alembic setup,
and referenced dead CSE stock tables (lkr_usd, sector_indices, foreign_flow,
stock_prices) that never belonged in the deployed schema per PRD v3. This
baseline creates exactly what models.py defines, nothing else, so the full
chain can build the schema from scratch on any empty database.

Revision ID: a1e5f9c3d072
Revises: 
Create Date: 2026-09-20
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1e5f9c3d072'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cbsl_rates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False, unique=True),
        sa.Column('sdfr', sa.Numeric(5, 2), nullable=False),
        sa.Column('slfr', sa.Numeric(5, 2), nullable=False),
        sa.Column('bank_rate', sa.Numeric(5, 2)),
        sa.Column('change_bps', sa.Integer(), server_default='0'),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'inflation_data',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False, unique=True),
        sa.Column('ncpi', sa.Numeric(8, 2)),
        sa.Column('ccpi', sa.Numeric(8, 2)),
        sa.Column('ncpi_yoy', sa.Numeric(6, 2)),
        sa.Column('ccpi_yoy', sa.Numeric(6, 2)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'exchange_rates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('rate', sa.Numeric(12, 4), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('date', 'currency', name='uq_exchange_date_currency'),
    )
    op.create_index('idx_exchange_rates_currency', 'exchange_rates', ['currency'])
    op.create_index('idx_exchange_rates_date', 'exchange_rates', ['date'])

    op.create_table(
        'macro_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('impact', sa.String(10)),
        sa.Column('source', sa.String(200)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.CheckConstraint("impact IN ('positive', 'negative', 'neutral')", name='ck_impact'),
    )
    op.create_index('idx_macro_events_type', 'macro_events', ['event_type'])
    op.create_index('idx_macro_events_date', 'macro_events', ['date'])


def downgrade() -> None:
    op.drop_table('macro_events')
    op.drop_index('idx_exchange_rates_date', table_name='exchange_rates')
    op.drop_index('idx_exchange_rates_currency', table_name='exchange_rates')
    op.drop_table('exchange_rates')
    op.drop_table('inflation_data')
    op.drop_table('cbsl_rates')
