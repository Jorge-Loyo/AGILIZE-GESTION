from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import datetime
from decimal import Decimal


class AprobacionExtras(Base, TimestampMixin):
    __tablename__ = "aprobacion_extras"

    id: Mapped[int] = mapped_column(primary_key=True)
    asistencia_id: Mapped[int] = mapped_column(ForeignKey("asistencias.id"))
    horas_extra: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente/aprobada/rechazada
    aprobado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    fecha_aprobacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    motivo_rechazo: Mapped[str] = mapped_column(String(250), default="")

    asistencia = relationship("Asistencia")
    aprobador = relationship("Usuario")
