from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date, datetime


# === PLAN DE CUENTAS ===
class CuentaContable(Base, TimestampMixin):
    __tablename__ = "cuentas_contables"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(150))
    tipo: Mapped[str] = mapped_column(String(20))  # activo, pasivo, patrimonio, ingreso, egreso
    padre_id: Mapped[int] = mapped_column(ForeignKey("cuentas_contables.id"), nullable=True)
    es_grupo: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    padre = relationship("CuentaContable", remote_side="CuentaContable.id")
    asientos_detalle = relationship("AsientoDetalle", back_populates="cuenta")


# === ASIENTOS CONTABLES ===
class Asiento(Base, TimestampMixin):
    __tablename__ = "asientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    concepto: Mapped[str] = mapped_column(String(250))
    tipo: Mapped[str] = mapped_column(String(30), default="manual")  # manual, factura, pago, ajuste
    referencia: Mapped[str] = mapped_column(String(100), default="")
    anulado: Mapped[bool] = mapped_column(Boolean, default=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("AsientoDetalle", back_populates="asiento", cascade="all, delete-orphan")


class AsientoDetalle(Base):
    __tablename__ = "asiento_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    asiento_id: Mapped[int] = mapped_column(ForeignKey("asientos.id"))
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas_contables.id"))
    debe: Mapped[float] = mapped_column(Float, default=0.0)
    haber: Mapped[float] = mapped_column(Float, default=0.0)
    descripcion: Mapped[str] = mapped_column(String(200), default="")

    asiento = relationship("Asiento", back_populates="detalles")
    cuenta = relationship("CuentaContable", back_populates="asientos_detalle")


# === FACTURACION ===
class Factura(Base, TimestampMixin):
    __tablename__ = "facturas"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_comprobante: Mapped[str] = mapped_column(String(30))  # factura, nota_credito, nota_debito
    letra: Mapped[str] = mapped_column(String(1), default="")  # A, B, C (AR) o vacio (VE)
    punto_venta: Mapped[int] = mapped_column(Integer, default=1)
    numero: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    tipo_entidad: Mapped[str] = mapped_column(String(20))  # cliente, proveedor
    entidad_id: Mapped[int] = mapped_column(Integer)
    entidad_nombre: Mapped[str] = mapped_column(String(200), default="")
    entidad_documento: Mapped[str] = mapped_column(String(30), default="")
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    impuesto_porcentaje: Mapped[float] = mapped_column(Float, default=0.0)
    impuesto_monto: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    moneda: Mapped[str] = mapped_column(String(10), default="")
    observaciones: Mapped[str] = mapped_column(Text, default="")
    estado: Mapped[str] = mapped_column(String(20), default="emitida")  # emitida, pagada, anulada
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("FacturaDetalle", back_populates="factura", cascade="all, delete-orphan")


class FacturaDetalle(Base):
    __tablename__ = "factura_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    factura_id: Mapped[int] = mapped_column(ForeignKey("facturas.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)
    precio_unitario: Mapped[float] = mapped_column(Float, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)

    factura = relationship("Factura", back_populates="detalles")


# === BANCOS ===
class CuentaBancaria(Base, TimestampMixin):
    __tablename__ = "cuentas_bancarias"

    id: Mapped[int] = mapped_column(primary_key=True)
    banco: Mapped[str] = mapped_column(String(100))
    tipo_cuenta: Mapped[str] = mapped_column(String(30))  # corriente, ahorro
    numero: Mapped[str] = mapped_column(String(50))
    moneda: Mapped[str] = mapped_column(String(10), default="")
    saldo: Mapped[float] = mapped_column(Float, default=0.0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    movimientos = relationship("MovimientoBanco", back_populates="cuenta_bancaria")


class MovimientoBanco(Base, TimestampMixin):
    __tablename__ = "movimientos_banco"

    id: Mapped[int] = mapped_column(primary_key=True)
    cuenta_bancaria_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bancarias.id"))
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    tipo: Mapped[str] = mapped_column(String(20))  # deposito, retiro, transferencia, cheque, debito, credito
    concepto: Mapped[str] = mapped_column(String(250))
    referencia: Mapped[str] = mapped_column(String(100), default="")
    monto: Mapped[float] = mapped_column(Float)
    saldo: Mapped[float] = mapped_column(Float, default=0.0)
    conciliado: Mapped[bool] = mapped_column(Boolean, default=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    cuenta_bancaria = relationship("CuentaBancaria", back_populates="movimientos")


# === CAJA ===
class Caja(Base, TimestampMixin):
    __tablename__ = "cajas"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    apertura: Mapped[float] = mapped_column(Float, default=0.0)
    cierre: Mapped[float] = mapped_column(Float, default=0.0)
    estado: Mapped[str] = mapped_column(String(20), default="abierta")  # abierta, cerrada
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    movimientos = relationship("MovimientoCaja", back_populates="caja")


class MovimientoCaja(Base, TimestampMixin):
    __tablename__ = "movimientos_caja"

    id: Mapped[int] = mapped_column(primary_key=True)
    caja_id: Mapped[int] = mapped_column(ForeignKey("cajas.id"))
    tipo: Mapped[str] = mapped_column(String(20))  # ingreso, egreso
    concepto: Mapped[str] = mapped_column(String(250))
    monto: Mapped[float] = mapped_column(Float)
    referencia: Mapped[str] = mapped_column(String(100), default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    caja = relationship("Caja", back_populates="movimientos")
