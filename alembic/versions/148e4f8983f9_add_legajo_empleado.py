"""add_legajo_empleado

Revision ID: 148e4f8983f9
Revises: 761e1a771bab
Create Date: 2026-06-05 15:32:49.251522
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '148e4f8983f9'
down_revision: Union[str, None] = '761e1a771bab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar columna nullable primero
    op.add_column('empleados', sa.Column('legajo', sa.String(length=20), nullable=True))
    # Generar legajo para registros existentes
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM empleados WHERE legajo IS NULL OR legajo = ''"))
    for row in result:
        conn.execute(sa.text(f"UPDATE empleados SET legajo = 'EMP-{row[0]:04d}' WHERE id = {row[0]}"))
    # Ahora hacer NOT NULL y unique
    op.alter_column('empleados', 'legajo', nullable=False)
    op.create_unique_constraint('uq_empleados_legajo', 'empleados', ['legajo'])


def downgrade() -> None:
    op.drop_constraint('uq_empleados_legajo', 'empleados', type_='unique')
    op.drop_column('empleados', 'legajo')
