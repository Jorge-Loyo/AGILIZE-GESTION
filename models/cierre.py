from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import datetime, date


class CierreAsistencia(Base, TimestampMixin):
    """Cierre de asistencia por quincena con fechas flexibles."""
    __tablename__ = "cierres_asistencia"

    id: Mapped[int] = mapped_column(primary_key=True)
    periodo: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    quincena: Mapped[int] = mapped_column(Integer, default=1)  # 1 o 2
    fecha_desde: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
    cerrado: Mapped[bool] = mapped_column(Boolean, default=True)
    cerrado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reabierto_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_reapertura: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CierreLiquidacion(Base, TimestampMixin):
    """Cierre de liquidacion por empleado y periodo."""
    __tablename__ = "cierres_liquidacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    periodo: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    quincena: Mapped[int] = mapped_column(Integer, default=0)  # 0=mensual, 1=1ra, 2=2da
    cerrado: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    empleado = relationship("Empleado")
