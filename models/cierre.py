from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import datetime


class CierreAsistencia(Base, TimestampMixin):
    """Cierre global de asistencia por período."""
    __tablename__ = "cierres_asistencia"

    id: Mapped[int] = mapped_column(primary_key=True)
    periodo: Mapped[str] = mapped_column(String(7), unique=True)  # YYYY-MM
    cerrado: Mapped[bool] = mapped_column(Boolean, default=True)
    cerrado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)  # usuario_id
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reabierto_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_reapertura: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CierreLiquidacion(Base, TimestampMixin):
    """Cierre de liquidación por empleado y período."""
    __tablename__ = "cierres_liquidacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    periodo: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    cerrado: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    empleado = relationship("Empleado")
