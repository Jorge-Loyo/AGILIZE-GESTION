from sqlalchemy import String, Integer, ForeignKey, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date
from decimal import Decimal


class LiquidacionDual(Base, TimestampMixin):
    """Liquidación real en USD (complemento a la liquidación legal en Bs)."""
    __tablename__ = "liquidaciones_dual"

    id: Mapped[int] = mapped_column(primary_key=True)
    liquidacion_legal_id: Mapped[int | None] = mapped_column(ForeignKey("liquidaciones.id"), nullable=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    periodo: Mapped[str] = mapped_column(String(7))
    fecha: Mapped[date] = mapped_column(Date)

    # Tasa
    tasa_bcv: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    fecha_tasa: Mapped[date] = mapped_column(Date)

    # Snapshot del empleado al liquidar
    sueldo_legal_bs: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    pago_total_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    canasta_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    bono_empresa_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    # Calculados
    sueldo_legal_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    complemento_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    faltas: Mapped[int] = mapped_column(Integer, default=0)
    descuento_faltas_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0"))
    deducciones_legal_bs: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    deducciones_legal_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0"))

    # Totales
    neto_nomina_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    neto_total_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    neto_total_bs: Mapped[Decimal] = mapped_column(Numeric(18, 2))

    # Relationships
    empleado = relationship("Empleado")
    liquidacion_legal = relationship("Liquidacion")
