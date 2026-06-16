"""add_historico_sueldo

Revision ID: b01cf5ca68b0
Revises: 5a0b4a1f8c7c
Create Date: 2026-06-16 13:38:09.450752

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b01cf5ca68b0'
down_revision: Union[str, None] = '5a0b4a1f8c7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('historico_sueldo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('empleado_id', sa.Integer(), nullable=False),
        sa.Column('fecha_cambio', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('campo', sa.String(length=50), nullable=False),
        sa.Column('valor_anterior', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('valor_nuevo', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['empleado_id'], ['empleados.id']),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('historico_sueldo')
