from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func


class HistoricoSueldo(Base):
    __tablename__ = "historico_sueldo"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    fecha_cambio: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    campo: Mapped[str] = mapped_column(String(50))  # valor_hora, valor_hora_extra, sueldo_mensual
    valor_anterior: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    valor_nuevo: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    empleado = relationship("Empleado")
    usuario = relationship("Usuario")
