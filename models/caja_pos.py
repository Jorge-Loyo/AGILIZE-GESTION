"""Modelos de gestion de cajas y turnos."""
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date, datetime


class CajaPOS(Base, TimestampMixin):
    """Posicion de caja fisica."""
    __tablename__ = "cajas_pos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursales.id"), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class TurnoCaja(Base, TimestampMixin):
    """Turno/sesion de un cajero en una caja."""
    __tablename__ = "turnos_caja"

    id: Mapped[int] = mapped_column(primary_key=True)
    caja_id: Mapped[int] = mapped_column(ForeignKey("cajas_pos.id"))
    cajero_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha: Mapped[date] = mapped_column(Date)
    hora_apertura: Mapped[datetime] = mapped_column(DateTime)
    hora_cierre: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    fondo_inicial: Mapped[float] = mapped_column(Float, default=0)
    # Totales calculados al cierre
    total_efectivo: Mapped[float] = mapped_column(Float, default=0)
    total_tarjeta_debito: Mapped[float] = mapped_column(Float, default=0)
    total_tarjeta_credito: Mapped[float] = mapped_column(Float, default=0)
    total_transferencia: Mapped[float] = mapped_column(Float, default=0)
    total_otros: Mapped[float] = mapped_column(Float, default=0)
    retiros: Mapped[float] = mapped_column(Float, default=0)
    ingresos: Mapped[float] = mapped_column(Float, default=0)
    # Arqueo
    efectivo_esperado: Mapped[float] = mapped_column(Float, default=0)
    efectivo_contado: Mapped[float] = mapped_column(Float, nullable=True)
    diferencia: Mapped[float] = mapped_column(Float, default=0)
    # Estado
    estado: Mapped[str] = mapped_column(String(20), default="abierto")  # abierto, cerrado, con_diferencia
    observaciones: Mapped[str] = mapped_column(Text, default="")


class MovimientoCajaPOS(Base, TimestampMixin):
    """Movimiento individual en la caja (venta, retiro, ingreso)."""
    __tablename__ = "movimientos_caja_pos"

    id: Mapped[int] = mapped_column(primary_key=True)
    turno_id: Mapped[int] = mapped_column(ForeignKey("turnos_caja.id"))
    tipo: Mapped[str] = mapped_column(String(20))  # venta, retiro, ingreso, anulacion
    medio_pago: Mapped[str] = mapped_column(String(30), default="efectivo")  # efectivo, tarjeta_debito, tarjeta_credito, transferencia, mixto
    monto: Mapped[float] = mapped_column(Float, default=0)
    referencia: Mapped[str] = mapped_column(String(100), default="")  # nro factura, motivo
    detalle_medios: Mapped[str] = mapped_column(Text, default="")  # JSON para pagos partidos
    hora: Mapped[datetime] = mapped_column(DateTime)
