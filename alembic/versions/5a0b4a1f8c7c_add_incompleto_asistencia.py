"""add_incompleto_asistencia

Revision ID: 5a0b4a1f8c7c
Revises: 1271a8a8ff57
Create Date: 2026-06-05 17:33:55.748958
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '5a0b4a1f8c7c'
down_revision: Union[str, None] = '1271a8a8ff57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('asistencias', sa.Column('incompleto', sa.Boolean(), server_default='false', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column('asistencias', 'incompleto')
