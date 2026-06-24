from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin


class Proveedor(Base, TimestampMixin):
    __tablename__ = "proveedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Datos basicos
    razon_social: Mapped[str] = mapped_column(String(200))
    nombre_fantasia: Mapped[str] = mapped_column(String(200), default="")
    # Datos fiscales
    cuit_rif: Mapped[str] = mapped_column(String(30), default="")
    tipo_contribuyente: Mapped[str] = mapped_column(String(50), default="")  # responsable inscripto, monotributo, exento
    condicion_iva: Mapped[str] = mapped_column(String(50), default="")  # gravado, exento, no alcanzado
    numero_ingresos_brutos: Mapped[str] = mapped_column(String(30), default="")
    # Direccion
    direccion: Mapped[str] = mapped_column(String(250), default="")
    ciudad: Mapped[str] = mapped_column(String(100), default="")
    provincia_estado: Mapped[str] = mapped_column(String(100), default="")
    codigo_postal: Mapped[str] = mapped_column(String(20), default="")
    pais: Mapped[str] = mapped_column(String(50), default="")
    # Contacto
    telefono: Mapped[str] = mapped_column(String(50), default="")
    celular: Mapped[str] = mapped_column(String(50), default="")
    email: Mapped[str] = mapped_column(String(150), default="")
    web: Mapped[str] = mapped_column(String(200), default="")
    contacto_nombre: Mapped[str] = mapped_column(String(150), default="")
    contacto_cargo: Mapped[str] = mapped_column(String(100), default="")
    contacto_telefono: Mapped[str] = mapped_column(String(50), default="")
    contacto_email: Mapped[str] = mapped_column(String(150), default="")
    # Condiciones comerciales
    rubro: Mapped[str] = mapped_column(String(100), default="")
    categoria: Mapped[str] = mapped_column(String(50), default="")  # critico, estrategico, regular, esporadico
    condicion_pago: Mapped[str] = mapped_column(String(100), default="")  # contado, 15 dias, 30 dias, 60 dias
    dias_pago: Mapped[int] = mapped_column(Integer, default=0)
    moneda: Mapped[str] = mapped_column(String(10), default="")
    descuento_default: Mapped[float] = mapped_column(Float, default=0.0)
    # Datos bancarios
    banco: Mapped[str] = mapped_column(String(100), default="")
    tipo_cuenta_banco: Mapped[str] = mapped_column(String(30), default="")
    numero_cuenta: Mapped[str] = mapped_column(String(50), default="")
    cbu_clabe: Mapped[str] = mapped_column(String(30), default="")
    titular_cuenta: Mapped[str] = mapped_column(String(150), default="")
    # Evaluacion
    calificacion: Mapped[int] = mapped_column(Integer, default=0)  # 1-5 estrellas
    cumplimiento_plazo: Mapped[str] = mapped_column(String(20), default="")  # excelente, bueno, regular, malo
    # Notas
    notas: Mapped[str] = mapped_column(Text, default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Cliente(Base, TimestampMixin):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(200))
    nombre_fantasia: Mapped[str] = mapped_column(String(200), default="")
    cuit_rif: Mapped[str] = mapped_column(String(30), default="")
    tipo_documento: Mapped[str] = mapped_column(String(20), default="")  # DNI, RIF, CUIT, CI
    numero_documento: Mapped[str] = mapped_column(String(30), default="")
    direccion: Mapped[str] = mapped_column(String(250), default="")
    ciudad: Mapped[str] = mapped_column(String(100), default="")
    provincia_estado: Mapped[str] = mapped_column(String(100), default="")
    telefono: Mapped[str] = mapped_column(String(50), default="")
    celular: Mapped[str] = mapped_column(String(50), default="")
    email: Mapped[str] = mapped_column(String(150), default="")
    contacto: Mapped[str] = mapped_column(String(150), default="")
    categoria: Mapped[str] = mapped_column(String(50), default="")  # mayorista, minorista, VIP
    condicion_pago: Mapped[str] = mapped_column(String(100), default="")
    limite_credito: Mapped[float] = mapped_column(Float, default=0.0)
    saldo: Mapped[float] = mapped_column(Float, default=0.0)
    notas: Mapped[str] = mapped_column(Text, default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
