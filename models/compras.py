"""Modelos del circuito documental de compras."""
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date


class TipoCompra(Base, TimestampMixin):
    """Tipos de compra: Operativa, Productiva, etc."""
    __tablename__ = "tipos_compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str] = mapped_column(String(250), default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Requisicion(Base, TimestampMixin):
    """Solicitud interna de compra."""
    __tablename__ = "requisiciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    solicitante: Mapped[str] = mapped_column(String(150), default="")
    departamento: Mapped[str] = mapped_column(String(100), default="")
    tipo_compra_id: Mapped[int] = mapped_column(ForeignKey("tipos_compra.id"), nullable=True)
    prioridad: Mapped[str] = mapped_column(String(20), default="normal")
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("RequisicionDetalle", back_populates="requisicion", cascade="all, delete-orphan")


class RequisicionDetalle(Base):
    __tablename__ = "requisicion_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    requisicion_id: Mapped[int] = mapped_column(ForeignKey("requisiciones.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)
    unidad: Mapped[str] = mapped_column(String(20), default="unidad")
    observacion: Mapped[str] = mapped_column(String(200), default="")

    requisicion = relationship("Requisicion", back_populates="detalles")


class RecepcionCompra(Base, TimestampMixin):
    """Remito de entrada / recepcion de mercaderia."""
    __tablename__ = "recepciones_compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    orden_compra_id: Mapped[int] = mapped_column(ForeignKey("ordenes_compra.id"), nullable=True)
    proveedor_nombre: Mapped[str] = mapped_column(String(200), default="")
    remito_proveedor: Mapped[str] = mapped_column(String(50), default="")
    deposito_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="recibido")  # recibido, parcial, con_diferencia
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("RecepcionDetalle", back_populates="recepcion", cascade="all, delete-orphan")


class RecepcionDetalle(Base):
    __tablename__ = "recepcion_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    recepcion_id: Mapped[int] = mapped_column(ForeignKey("recepciones_compra.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad_esperada: Mapped[float] = mapped_column(Float, default=0)
    cantidad_recibida: Mapped[float] = mapped_column(Float, default=0)
    precio_unitario: Mapped[float] = mapped_column(Float, default=0)
    observacion: Mapped[str] = mapped_column(String(200), default="")

    recepcion = relationship("RecepcionCompra", back_populates="detalles")


class FacturaCompra(Base, TimestampMixin):
    """Factura del proveedor."""
    __tablename__ = "facturas_compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero_factura: Mapped[str] = mapped_column(String(50))
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=True)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedores.id"), nullable=True)
    proveedor_nombre: Mapped[str] = mapped_column(String(200), default="")
    orden_compra_id: Mapped[int] = mapped_column(ForeignKey("ordenes_compra.id"), nullable=True)
    recepcion_id: Mapped[int] = mapped_column(ForeignKey("recepciones_compra.id"), nullable=True)
    subtotal: Mapped[float] = mapped_column(Float, default=0)
    impuesto_porcentaje: Mapped[float] = mapped_column(Float, default=0)
    impuesto_monto: Mapped[float] = mapped_column(Float, default=0)
    total: Mapped[float] = mapped_column(Float, default=0)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, pagada, anulada
    conciliada: Mapped[bool] = mapped_column(Boolean, default=False)  # three-way match OK
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("FacturaCompraDetalle", back_populates="factura", cascade="all, delete-orphan")


class FacturaCompraDetalle(Base):
    __tablename__ = "factura_compra_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    factura_id: Mapped[int] = mapped_column(ForeignKey("facturas_compra.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)
    precio_unitario: Mapped[float] = mapped_column(Float, default=0)
    subtotal: Mapped[float] = mapped_column(Float, default=0)

    factura = relationship("FacturaCompra", back_populates="detalles")


# === LISTAS DE PRECIOS DE PROVEEDORES ===

class ListaPrecioProveedor(Base, TimestampMixin):
    """Lista/catalogo de precios de un proveedor."""
    __tablename__ = "listas_precio_proveedor"

    id: Mapped[int] = mapped_column(primary_key=True)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedores.id"))
    nombre: Mapped[str] = mapped_column(String(200), default="")  # ej: "Lista Enero 2025"
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    moneda: Mapped[str] = mapped_column(String(10), default="USD")
    vigente: Mapped[bool] = mapped_column(Boolean, default=True)
    observaciones: Mapped[str] = mapped_column(Text, default="")

    detalles = relationship("ListaPrecioDetalle", back_populates="lista", cascade="all, delete-orphan")
    proveedor = relationship("Proveedor", foreign_keys=[proveedor_id])


class ListaPrecioDetalle(Base):
    """Item de la lista de precios."""
    __tablename__ = "lista_precio_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    lista_id: Mapped[int] = mapped_column(ForeignKey("listas_precio_proveedor.id"))
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=True)
    codigo_proveedor: Mapped[str] = mapped_column(String(50), default="")
    descripcion: Mapped[str] = mapped_column(String(250))
    precio_unitario: Mapped[float] = mapped_column(Float, default=0)
    descuento: Mapped[float] = mapped_column(Float, default=0)  # porcentaje
    precio_neto: Mapped[float] = mapped_column(Float, default=0)  # precio - descuento

    lista = relationship("ListaPrecioProveedor", back_populates="detalles")


# === COTIZACIONES / SOURCING ===

class CotizacionCompra(Base, TimestampMixin):
    """Comparacion de presupuestos de proveedores para una necesidad."""
    __tablename__ = "cotizaciones_compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    descripcion: Mapped[str] = mapped_column(String(250), default="")
    requisicion_id: Mapped[int] = mapped_column(ForeignKey("requisiciones.id"), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="abierta")  # abierta, cerrada, adjudicada
    proveedor_adjudicado_id: Mapped[int] = mapped_column(ForeignKey("proveedores.id"), nullable=True)
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("CotizacionCompraDetalle", back_populates="cotizacion", cascade="all, delete-orphan")


class CotizacionCompraDetalle(Base):
    """Linea de cotizacion: un proveedor cotiza un item."""
    __tablename__ = "cotizacion_compra_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    cotizacion_id: Mapped[int] = mapped_column(ForeignKey("cotizaciones_compra.id"))
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedores.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)
    precio_unitario: Mapped[float] = mapped_column(Float, default=0)
    plazo_entrega: Mapped[str] = mapped_column(String(50), default="")  # ej: "5 dias"
    condicion_pago: Mapped[str] = mapped_column(String(100), default="")
    seleccionado: Mapped[bool] = mapped_column(Boolean, default=False)

    cotizacion = relationship("CotizacionCompra", back_populates="detalles")


# === APROBACIONES DE COMPRA ===

class ReglaAprobacion(Base, TimestampMixin):
    """Reglas de negocio para aprobaciones de OC."""
    __tablename__ = "reglas_aprobacion_compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    documento: Mapped[str] = mapped_column(String(30), default="orden_compra")  # orden_compra, requisicion
    condicion: Mapped[str] = mapped_column(String(20), default="monto_mayor")  # monto_mayor, siempre
    valor_condicion: Mapped[float] = mapped_column(Float, default=0)  # ej: 5000
    moneda: Mapped[str] = mapped_column(String(10), default="USD")
    aprobador_usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    aprobador_rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class AprobacionCompra(Base, TimestampMixin):
    """Registro de aprobaciones pendientes/realizadas."""
    __tablename__ = "aprobaciones_compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    regla_id: Mapped[int] = mapped_column(ForeignKey("reglas_aprobacion_compra.id"), nullable=True)
    documento_tipo: Mapped[str] = mapped_column(String(30))  # orden_compra, requisicion
    documento_id: Mapped[int] = mapped_column(Integer)
    documento_numero: Mapped[int] = mapped_column(Integer, default=0)
    monto: Mapped[float] = mapped_column(Float, default=0)
    solicitante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    aprobador_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, aprobada, rechazada
    fecha_respuesta: Mapped[date] = mapped_column(Date, nullable=True)
    comentario: Mapped[str] = mapped_column(Text, default="")
