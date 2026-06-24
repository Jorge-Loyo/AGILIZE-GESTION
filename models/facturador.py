from sqlalchemy import String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base, TimestampMixin


class ConfigFacturador(Base, TimestampMixin):
    __tablename__ = "config_facturadores"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100), default="")
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursales.id"), nullable=True)
    depositos_ids: Mapped[str] = mapped_column(String(200), default="")  # IDs separados por coma: "3,5"
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
