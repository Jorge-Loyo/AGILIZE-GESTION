from sqlalchemy import String, Integer, ForeignKey, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date, datetime


class Vacaciones(Base, TimestampMixin):
    __tablename__ = "vacaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    periodo_anual: Mapped[int] = mapped_column(Integer)  # 2026
    dias_correspondientes: Mapped[int] = mapped_column(Integer)
    fecha_desde: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
    dias_tomados: Mapped[int] = mapped_column(Integer, default=0)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente/aprobada/tomada/cancelada
    aprobado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    fecha_aprobacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    observaciones: Mapped[str] = mapped_column(String(250), default="")

    empleado = relationship("Empleado")
    aprobador = relationship("Usuario")
