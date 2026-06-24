from sqlalchemy import String, Boolean, Integer, ForeignKey, Date, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date
from decimal import Decimal


class ConceptoNomina(Base, TimestampMixin):
    """Conceptos de haberes y deducciones configurables."""
    __tablename__ = "conceptos_nomina"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(150))
    tipo: Mapped[str] = mapped_column(String(20))  # "haber" o "deduccion"
    categoria: Mapped[str] = mapped_column(String(30), default="remunerativo")  # remunerativo, no_remunerativo, retencion
    calculo: Mapped[str] = mapped_column(String(20), default="porcentaje")  # "porcentaje", "fijo", "por_dia"
    base_calculo: Mapped[str] = mapped_column(String(20), default="basico")  # basico, bruto, neto
    porcentaje: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    monto_fijo: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    aplica_a: Mapped[str] = mapped_column(String(20), default="todos")  # todos, por_hora, mensual
    orden: Mapped[int] = mapped_column(Integer, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    detalles = relationship("LiquidacionDetalle", back_populates="concepto")


class Liquidacion(Base, TimestampMixin):
    """Cabecera de liquidación de sueldo."""
    __tablename__ = "liquidaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    periodo: Mapped[str] = mapped_column(String(7))  # "2025-06" (YYYY-MM)
    fecha_liquidacion: Mapped[date] = mapped_column(Date)
    sueldo_basico: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total_haberes: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_deducciones: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    neto: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    observaciones: Mapped[str] = mapped_column(Text, default="")

    empleado = relationship("Empleado")
    detalles = relationship("LiquidacionDetalle", back_populates="liquidacion", cascade="all, delete-orphan")


class LiquidacionDetalle(Base):
    """Líneas del recibo (cada concepto aplicado)."""
    __tablename__ = "liquidacion_detalle"

    id: Mapped[int] = mapped_column(primary_key=True)
    liquidacion_id: Mapped[int] = mapped_column(ForeignKey("liquidaciones.id"))
    concepto_id: Mapped[int] = mapped_column(ForeignKey("conceptos_nomina.id"))
    tipo: Mapped[str] = mapped_column(String(20))  # "haber" o "deduccion"
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    liquidacion = relationship("Liquidacion", back_populates="detalles")
    concepto = relationship("ConceptoNomina", back_populates="detalles")
