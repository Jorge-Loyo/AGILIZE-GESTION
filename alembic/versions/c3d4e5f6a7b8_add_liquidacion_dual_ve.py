"""add liquidacion dual ve

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c3d4e5f6a7b8'
down_revision = ('2b1a736d4be7', 'b2c3d4e5f6a7')
branch_labels = None
depends_on = None


def upgrade():
    # Campos nuevos en empleados
    op.add_column('empleados', sa.Column('pago_total_usd', sa.Numeric(12, 2), server_default='0', nullable=False))
    op.add_column('empleados', sa.Column('canasta_usd', sa.Numeric(12, 2), server_default='0', nullable=False))
    op.add_column('empleados', sa.Column('bono_empresa_usd', sa.Numeric(12, 2), server_default='0', nullable=False))

    # Tabla liquidaciones_dual
    op.create_table(
        'liquidaciones_dual',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('liquidacion_legal_id', sa.Integer(), sa.ForeignKey('liquidaciones.id'), nullable=True),
        sa.Column('empleado_id', sa.Integer(), sa.ForeignKey('empleados.id'), nullable=False),
        sa.Column('periodo', sa.String(7), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('tasa_bcv', sa.Numeric(18, 6), nullable=False),
        sa.Column('fecha_tasa', sa.Date(), nullable=False),
        sa.Column('sueldo_legal_bs', sa.Numeric(12, 2), nullable=False),
        sa.Column('pago_total_usd', sa.Numeric(12, 2), nullable=False),
        sa.Column('canasta_usd', sa.Numeric(12, 2), nullable=False),
        sa.Column('bono_empresa_usd', sa.Numeric(12, 2), nullable=False),
        sa.Column('sueldo_legal_usd', sa.Numeric(12, 4), nullable=False),
        sa.Column('complemento_usd', sa.Numeric(12, 4), nullable=False),
        sa.Column('faltas', sa.Integer(), server_default='0', nullable=False),
        sa.Column('descuento_faltas_usd', sa.Numeric(12, 4), server_default='0', nullable=False),
        sa.Column('deducciones_legal_bs', sa.Numeric(12, 2), server_default='0', nullable=False),
        sa.Column('deducciones_legal_usd', sa.Numeric(12, 4), server_default='0', nullable=False),
        sa.Column('neto_nomina_usd', sa.Numeric(12, 2), nullable=False),
        sa.Column('neto_total_usd', sa.Numeric(12, 2), nullable=False),
        sa.Column('neto_total_bs', sa.Numeric(18, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('liquidaciones_dual')
    op.drop_column('empleados', 'bono_empresa_usd')
    op.drop_column('empleados', 'canasta_usd')
    op.drop_column('empleados', 'pago_total_usd')
