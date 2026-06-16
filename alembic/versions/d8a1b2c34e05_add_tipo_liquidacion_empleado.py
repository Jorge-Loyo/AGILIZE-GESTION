"""add_tipo_liquidacion_empleado

Revision ID: d8a1b2c34e05
Revises: c7b2d4e56f01
Create Date: 2026-06-16 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd8a1b2c34e05'
down_revision: Union[str, None] = 'c7b2d4e56f01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('empleados', sa.Column('tipo_liquidacion', sa.String(length=20), nullable=False, server_default='por_hora'))


def downgrade() -> None:
    op.drop_column('empleados', 'tipo_liquidacion')
