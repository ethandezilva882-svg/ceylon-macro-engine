"""drop_cse_tables

Revision ID: a1b2c3d4e5f6
Revises: 913bc8c2dd67
Create Date: 2026-07-04

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '913bc8c2dd67'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('sector_indices')
    op.drop_table('foreign_flow')
    op.drop_table('stock_prices')


def downgrade():
    op.create_table(
        'stock_prices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('open', sa.Numeric(12, 2)),
        sa.Column('high', sa.Numeric(12, 2)),
        sa.Column('low', sa.Numeric(12, 2)),
        sa.Column('close', sa.Numeric(12, 2), nullable=False),
        sa.Column('volume', sa.BigInteger(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('date', 'symbol', name='uq_stock_date_symbol'),
    )
    op.create_index('idx_stock_prices_symbol', 'stock_prices', ['symbol'])
    op.create_index('idx_stock_prices_date', 'stock_prices', ['date'])

    op.create_table(
        'foreign_flow',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False, unique=True),
        sa.Column('buy_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('sell_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('net_flow', sa.Numeric(15, 2), sa.Computed('buy_value - sell_value', persisted=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'sector_indices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('sector', sa.String(length=60), nullable=False),
        sa.Column('index_value', sa.Numeric(12, 2), nullable=False),
        sa.Column('change_pct', sa.Numeric(6, 2)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('date', 'sector', name='uq_sector_date'),
    )
    op.create_index('idx_sector_indices_sector', 'sector_indices', ['sector'])