from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin


class Sucursal(Base, TimestampMixin):
    __tablename__ = "sucursales"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    direccion: Mapped[str] = mapped_column(String(250), default="")
    telefono: Mapped[str] = mapped_column(String(50), default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    empleados = relationship("Empleado", back_populates="sucursal")
