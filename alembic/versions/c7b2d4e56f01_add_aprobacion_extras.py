"""add_aprobacion_extras

Revision ID: c7b2d4e56f01
Revises: a3e9f1c24d01
Create Date: 2026-06-16 14:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c7b2d4e56f01'
down_revision: Union[str, None] = 'a3e9f1c24d01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('aprobacion_extras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asistencia_id', sa.Integer(), nullable=False),
        sa.Column('horas_extra', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=False, server_default='pendiente'),
        sa.Column('aprobado_por', sa.Integer(), nullable=True),
        sa.Column('fecha_aprobacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('motivo_rechazo', sa.String(length=250), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['asistencia_id'], ['asistencias.id']),
        sa.ForeignKeyConstraint(['aprobado_por'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('aprobacion_extras')
