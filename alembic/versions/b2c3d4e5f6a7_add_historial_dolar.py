"""add_historial_dolar

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-04 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'historial_dolar',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('fecha', sa.Date(), nullable=False, unique=True),
        sa.Column('valor', sa.Numeric(18, 6), nullable=False),
        sa.Column('fuente', sa.String(100), server_default='BCV'),
        sa.Column('pais', sa.String(30), server_default='venezuela'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_historial_dolar_fecha', 'historial_dolar', ['fecha'])


def downgrade() -> None:
    op.drop_index('ix_historial_dolar_fecha')
    op.drop_table('historial_dolar')
