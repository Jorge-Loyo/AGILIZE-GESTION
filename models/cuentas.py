from sqlalchemy import String, Integer, Float, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date


class MovimientoCuenta(Base, TimestampMixin):
    __tablename__ = "movimientos_cuenta"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_entidad: Mapped[str] = mapped_column(String(20))  # cliente, proveedor
    entidad_id: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    tipo: Mapped[str] = mapped_column(String(10))  # debe, haber
    concepto: Mapped[str] = mapped_column(String(250))
    comprobante: Mapped[str] = mapped_column(String(100), default="")
    monto: Mapped[float] = mapped_column(Float)
    saldo: Mapped[float] = mapped_column(Float, default=0.0)
    notas: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
