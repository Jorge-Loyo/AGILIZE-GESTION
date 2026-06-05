from sqlalchemy import String, Boolean, Integer, ForeignKey, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date


class TipoPermiso(Base, TimestampMixin):
    """Tipos de permiso configurables: licencia, enfermedad, autorizado, etc."""
    __tablename__ = "tipos_permiso"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    con_goce: Mapped[bool] = mapped_column(Boolean, default=True)  # Si se paga o no
    dias_max: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Limite de dias por anio
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class PermisoEmpleado(Base, TimestampMixin):
    """Permiso/licencia otorgado a un empleado."""
    __tablename__ = "permisos_empleado"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    tipo_permiso_id: Mapped[int] = mapped_column(ForeignKey("tipos_permiso.id"))
    fecha_desde: Mapped[date] = mapped_column(Date)
    fecha_hasta: Mapped[date] = mapped_column(Date)
    dias: Mapped[int] = mapped_column(Integer)
    motivo: Mapped[str] = mapped_column(Text, default="")
    aprobado: Mapped[bool] = mapped_column(Boolean, default=True)

    empleado = relationship("Empleado")
    tipo_permiso = relationship("TipoPermiso")


class Ausencia(Base, TimestampMixin):
    """Registro de ausencia de un empleado."""
    __tablename__ = "ausencias"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    fecha: Mapped[date] = mapped_column(Date)
    justificada: Mapped[bool] = mapped_column(Boolean, default=False)
    motivo: Mapped[str] = mapped_column(String(250), default="")
    periodo: Mapped[str] = mapped_column(String(7), default="")  # YYYY-MM

    empleado = relationship("Empleado")
