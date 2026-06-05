"""add_calculo_to_conceptos

Revision ID: 1271a8a8ff57
Revises: 7e6d1ba8ac1b
Create Date: 2026-06-05 17:09:47.810788
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '1271a8a8ff57'
down_revision: Union[str, None] = '7e6d1ba8ac1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar columna nullable primero
    op.add_column('conceptos_nomina', sa.Column('calculo', sa.String(length=20), nullable=True))
    # Setear default para existentes
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE conceptos_nomina SET calculo = 'porcentaje' WHERE porcentaje IS NOT NULL"))
    conn.execute(sa.text("UPDATE conceptos_nomina SET calculo = 'fijo' WHERE porcentaje IS NULL AND monto_fijo IS NOT NULL"))
    conn.execute(sa.text("UPDATE conceptos_nomina SET calculo = 'porcentaje' WHERE calculo IS NULL"))
    # Hacer NOT NULL
    op.alter_column('conceptos_nomina', 'calculo', nullable=False, server_default='porcentaje')


def downgrade() -> None:
    op.drop_column('conceptos_nomina', 'calculo')
