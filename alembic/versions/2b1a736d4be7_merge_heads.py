"""merge_heads

Revision ID: 2b1a736d4be7
Revises: a1b2c3d4e5f6, d8a1b2c34e05
Create Date: 2026-06-24 10:23:21.137775
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '2b1a736d4be7'
down_revision: Union[str, None] = ('a1b2c3d4e5f6', 'd8a1b2c34e05')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
