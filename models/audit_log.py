from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from datetime import datetime


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=True)
    accion: Mapped[str] = mapped_column(String(50))  # LOGIN, CREATE, UPDATE, DELETE
    tabla: Mapped[str] = mapped_column(String(50), default="")
    registro_id: Mapped[int] = mapped_column(Integer, nullable=True)
    detalle: Mapped[str] = mapped_column(Text, default="")
    ip: Mapped[str] = mapped_column(String(45), default="")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
