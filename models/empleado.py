from sqlalchemy import String, Boolean, Integer, ForeignKey, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date
from decimal import Decimal


class Departamento(Base, TimestampMixin):
    __tablename__ = "departamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    empleados = relationship("Empleado", back_populates="departamento")


class Cargo(Base, TimestampMixin):
    __tablename__ = "cargos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    empleados = relationship("Empleado", back_populates="cargo")


class Empleado(Base, TimestampMixin):
    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column(primary_key=True)
    legajo: Mapped[str] = mapped_column(String(20), unique=True, default="")
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str] = mapped_column(String(100))
    dni: Mapped[str] = mapped_column(String(20), unique=True, nullable=True, default="")
    cuil: Mapped[str] = mapped_column(String(20), unique=True, nullable=True, default="")
    email: Mapped[str] = mapped_column(String(150), default="")
    telefono: Mapped[str] = mapped_column(String(50), default="")
    direccion: Mapped[str] = mapped_column(String(250), default="")
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    edad: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_ingreso: Mapped[date] = mapped_column(Date)
    fecha_egreso: Mapped[date | None] = mapped_column(Date, nullable=True)
    departamento_id: Mapped[int | None] = mapped_column(ForeignKey("departamentos.id"), nullable=True)
    cargo_id: Mapped[int | None] = mapped_column(ForeignKey("cargos.id"), nullable=True)
    sucursal_id: Mapped[int | None] = mapped_column(ForeignKey("sucursales.id"), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    horas_jornada: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("8"))
    valor_hora: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    valor_hora_extra: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    sueldo_mensual: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    dias_laborales: Mapped[str] = mapped_column(String(50), default="lun,mar,mie,jue,vie")  # dias separados por coma
    hora_entrada: Mapped[str] = mapped_column(String(5), default="08:00")
    hora_salida: Mapped[str] = mapped_column(String(5), default="17:00")
    tipo_liquidacion: Mapped[str] = mapped_column(String(20), default="por_hora")  # por_hora / mensual
    observaciones: Mapped[str] = mapped_column(Text, default="")

    departamento = relationship("Departamento", back_populates="empleados")
    cargo = relationship("Cargo", back_populates="empleados")
    sucursal = relationship("Sucursal", back_populates="empleados")
