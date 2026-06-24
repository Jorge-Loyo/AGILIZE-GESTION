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
    # Datos personales
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str] = mapped_column(String(100))
    dni: Mapped[str] = mapped_column(String(20), unique=True, nullable=True, default="")
    cuil: Mapped[str] = mapped_column(String(20), unique=True, nullable=True, default="")
    sexo: Mapped[str] = mapped_column(String(10), default="")  # M, F, otro
    estado_civil: Mapped[str] = mapped_column(String(20), default="")  # soltero, casado, divorciado, viudo
    nacionalidad: Mapped[str] = mapped_column(String(50), default="")
    email: Mapped[str] = mapped_column(String(150), default="")
    telefono: Mapped[str] = mapped_column(String(50), default="")
    celular: Mapped[str] = mapped_column(String(50), default="")
    direccion: Mapped[str] = mapped_column(String(250), default="")
    ciudad: Mapped[str] = mapped_column(String(100), default="")
    codigo_postal: Mapped[str] = mapped_column(String(20), default="")
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    edad: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Contacto de emergencia
    emergencia_nombre: Mapped[str] = mapped_column(String(150), default="")
    emergencia_telefono: Mapped[str] = mapped_column(String(50), default="")
    emergencia_parentesco: Mapped[str] = mapped_column(String(50), default="")
    # Salud basica
    grupo_sanguineo: Mapped[str] = mapped_column(String(10), default="")
    obra_social: Mapped[str] = mapped_column(String(100), default="")
    nro_afiliado: Mapped[str] = mapped_column(String(30), default="")
    alergias: Mapped[str] = mapped_column(String(250), default="")
    # Datos contractuales
    fecha_ingreso: Mapped[date] = mapped_column(Date)
    fecha_egreso: Mapped[date | None] = mapped_column(Date, nullable=True)
    tipo_contrato: Mapped[str] = mapped_column(String(30), default="indefinido")  # indefinido, temporal, pasantia, eventual
    motivo_egreso: Mapped[str] = mapped_column(String(100), default="")
    departamento_id: Mapped[int | None] = mapped_column(ForeignKey("departamentos.id"), nullable=True)
    cargo_id: Mapped[int | None] = mapped_column(ForeignKey("cargos.id"), nullable=True)
    sucursal_id: Mapped[int | None] = mapped_column(ForeignKey("sucursales.id"), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    # Jornada y liquidacion
    horas_jornada: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("8"))
    valor_hora: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    valor_hora_extra: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    sueldo_mensual: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    dias_laborales: Mapped[str] = mapped_column(String(50), default="lun,mar,mie,jue,vie")
    hora_entrada: Mapped[str] = mapped_column(String(5), default="08:00")
    hora_salida: Mapped[str] = mapped_column(String(5), default="17:00")
    tipo_liquidacion: Mapped[str] = mapped_column(String(20), default="por_hora")  # por_hora / mensual
    # Cuenta bancaria
    banco: Mapped[str] = mapped_column(String(100), default="")
    tipo_cuenta: Mapped[str] = mapped_column(String(30), default="")  # cta_ahorro, cta_corriente
    numero_cuenta: Mapped[str] = mapped_column(String(50), default="")
    cbu_clabe: Mapped[str] = mapped_column(String(30), default="")
    # Notas
    observaciones: Mapped[str] = mapped_column(Text, default="")

    departamento = relationship("Departamento", back_populates="empleados")
    cargo = relationship("Cargo", back_populates="empleados")
    sucursal = relationship("Sucursal", back_populates="empleados")
    legajo_eventos = relationship("LegajoEvento", back_populates="empleado", cascade="all, delete-orphan")


class LegajoEvento(Base, TimestampMixin):
    """Historial del legajo: ascensos, cambios sueldo, sanciones, herramientas, evaluaciones."""
    __tablename__ = "legajo_eventos"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    fecha: Mapped[date] = mapped_column(Date)
    tipo: Mapped[str] = mapped_column(String(30))  # ascenso, cambio_sueldo, sancion, herramienta, evaluacion, capacitacion, otro
    titulo: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    # Datos especificos segun tipo
    valor_anterior: Mapped[str] = mapped_column(String(100), default="")  # cargo/sueldo anterior
    valor_nuevo: Mapped[str] = mapped_column(String(100), default="")  # cargo/sueldo nuevo
    documento_adjunto: Mapped[str] = mapped_column(String(250), default="")  # path archivo
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    empleado = relationship("Empleado", back_populates="legajo_eventos")
