from sqlalchemy import String, Numeric, Date, Time
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base, TimestampMixin
from datetime import date, time
from decimal import Decimal
from typing import Optional


class HistorialDolar(Base, TimestampMixin):
    """Registro diario del valor del dolar segun banco central del pais."""
    __tablename__ = "historial_dolar"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, index=False)
    hora_consulta: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    fuente: Mapped[str] = mapped_column(String(100), default="BCV")
    pais: Mapped[str] = mapped_column(String(30), default="venezuela")
