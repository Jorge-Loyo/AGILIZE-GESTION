from sqlalchemy import String, Boolean, Integer, ForeignKey, Date, Time, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date, time
from decimal import Decimal
import enum


class TipoDia(str, enum.Enum):
    NORMAL = "normal"
    SABADO = "sabado"
    DOMINGO = "domingo"
    FERIADO = "feriado"


class Asistencia(Base, TimestampMixin):
    __tablename__ = "asistencias"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    fecha: Mapped[date] = mapped_column(Date)
    hora_entrada: Mapped[time | None] = mapped_column(Time, nullable=True)
    hora_salida: Mapped[time | None] = mapped_column(Time, nullable=True)
    tipo_dia: Mapped[str] = mapped_column(String(20), default=TipoDia.NORMAL.value)
    horas_normales: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    horas_extra: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    es_feriado: Mapped[bool] = mapped_column(Boolean, default=False)
    incompleto: Mapped[bool] = mapped_column(Boolean, default=False)

    empleado = relationship("Empleado")


class Feriado(Base):
    __tablename__ = "feriados"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, unique=True)
    descripcion: Mapped[str] = mapped_column(String(150))


class TurnoLaboral(Base, TimestampMixin):
    """Definicion de turnos: manana, tarde, noche, rotativo."""
    __tablename__ = "turnos_laborales"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    hora_entrada: Mapped[time] = mapped_column(Time)
    hora_salida: Mapped[time] = mapped_column(Time)
    tolerancia_entrada: Mapped[int] = mapped_column(Integer, default=10)  # minutos
    tolerancia_salida: Mapped[int] = mapped_column(Integer, default=5)
    es_nocturno: Mapped[bool] = mapped_column(Boolean, default=False)
    horas_jornada: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("8"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class FichajePIN(Base, TimestampMixin):
    """Registro de fichaje por PIN/codigo desde la app (sin reloj biometrico)."""
    __tablename__ = "fichajes_pin"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    fecha: Mapped[date] = mapped_column(Date)
    hora: Mapped[time] = mapped_column(Time)
    tipo: Mapped[str] = mapped_column(String(10))  # entrada, salida
    metodo: Mapped[str] = mapped_column(String(20), default="pin")  # pin, biometrico, manual
    dispositivo: Mapped[str] = mapped_column(String(50), default="")  # nombre PC/terminal

    empleado = relationship("Empleado")
