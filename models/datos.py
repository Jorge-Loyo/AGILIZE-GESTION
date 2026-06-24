from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin


class Proveedor(Base, TimestampMixin):
    __tablename__ = "proveedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(200))
    nombre_fantasia: Mapped[str] = mapped_column(String(200), default="")
    cuit_rif: Mapped[str] = mapped_column(String(30), default="")
    direccion: Mapped[str] = mapped_column(String(250), default="")
    ciudad: Mapped[str] = mapped_column(String(100), default="")
    provincia_estado: Mapped[str] = mapped_column(String(100), default="")
    telefono: Mapped[str] = mapped_column(String(50), default="")
    celular: Mapped[str] = mapped_column(String(50), default="")
    email: Mapped[str] = mapped_column(String(150), default="")
    web: Mapped[str] = mapped_column(String(200), default="")
    contacto: Mapped[str] = mapped_column(String(150), default="")
    rubro: Mapped[str] = mapped_column(String(100), default="")
    condicion_pago: Mapped[str] = mapped_column(String(100), default="")
    cuenta_bancaria: Mapped[str] = mapped_column(String(100), default="")
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
