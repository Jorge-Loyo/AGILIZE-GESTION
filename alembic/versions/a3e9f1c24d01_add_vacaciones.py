"""add_vacaciones

Revision ID: a3e9f1c24d01
Revises: b01cf5ca68b0
Create Date: 2026-06-16 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a3e9f1c24d01'
down_revision: Union[str, None] = 'b01cf5ca68b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('vacaciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('empleado_id', sa.Integer(), nullable=False),
        sa.Column('periodo_anual', sa.Integer(), nullable=False),
        sa.Column('dias_correspondientes', sa.Integer(), nullable=False),
        sa.Column('fecha_desde', sa.Date(), nullable=True),
        sa.Column('fecha_hasta', sa.Date(), nullable=True),
        sa.Column('dias_tomados', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('estado', sa.String(length=20), nullable=False, server_default='pendiente'),
        sa.Column('aprobado_por', sa.Integer(), nullable=True),
        sa.Column('fecha_aprobacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('observaciones', sa.String(length=250), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['empleado_id'], ['empleados.id']),
        sa.ForeignKeyConstraint(['aprobado_por'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('vacaciones')
