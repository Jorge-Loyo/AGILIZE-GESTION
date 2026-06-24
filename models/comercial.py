from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date


class Presupuesto(Base, TimestampMixin):
    __tablename__ = "presupuestos"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    cliente_nombre: Mapped[str] = mapped_column(String(200), default="")
    validez_dias: Mapped[int] = mapped_column(Integer, default=15)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    impuesto: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, aprobado, rechazado, vencido
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("PresupuestoDetalle", back_populates="presupuesto", cascade="all, delete-orphan")


class PresupuestoDetalle(Base):
    __tablename__ = "presupuesto_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    presupuesto_id: Mapped[int] = mapped_column(ForeignKey("presupuestos.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)
    precio_unitario: Mapped[float] = mapped_column(Float, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)

    presupuesto = relationship("Presupuesto", back_populates="detalles")


class PedidoVenta(Base, TimestampMixin):
    __tablename__ = "pedidos_venta"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    cliente_nombre: Mapped[str] = mapped_column(String(200), default="")
    presupuesto_id: Mapped[int] = mapped_column(ForeignKey("presupuestos.id"), nullable=True)
    direccion_entrega_id: Mapped[int] = mapped_column(ForeignKey("direcciones_entrega_cliente.id"), nullable=True)
    condicion_pago: Mapped[str] = mapped_column(String(100), default="")
    fecha_entrega: Mapped[date] = mapped_column(Date, nullable=True)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    impuesto: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, en_proceso, despachado, entregado, cancelado
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("PedidoVentaDetalle", back_populates="pedido", cascade="all, delete-orphan")


class PedidoVentaDetalle(Base):
    __tablename__ = "pedido_venta_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos_venta.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)
    precio_unitario: Mapped[float] = mapped_column(Float, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)

    pedido = relationship("PedidoVenta", back_populates="detalles")


class OrdenCompra(Base, TimestampMixin):
    __tablename__ = "ordenes_compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedores.id"), nullable=True)
    proveedor_nombre: Mapped[str] = mapped_column(String(200), default="")
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    impuesto: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, enviada, recibida, cancelada
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("OrdenCompraDetalle", back_populates="orden", cascade="all, delete-orphan")


class OrdenCompraDetalle(Base):
    __tablename__ = "orden_compra_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes_compra.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)
    precio_unitario: Mapped[float] = mapped_column(Float, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)

    orden = relationship("OrdenCompra", back_populates="detalles")


# === REMITO DE SALIDA ===

class RemitoSalida(Base, TimestampMixin):
    """Documento logistico que acompaña la mercaderia. Mueve stock."""
    __tablename__ = "remitos_salida"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos_venta.id"), nullable=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    cliente_nombre: Mapped[str] = mapped_column(String(200), default="")
    direccion_entrega: Mapped[str] = mapped_column(String(250), default="")
    deposito_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"), nullable=True)
    transportista: Mapped[str] = mapped_column(String(150), default="")
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, despachado, entregado
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("RemitoSalidaDetalle", back_populates="remito", cascade="all, delete-orphan")


class RemitoSalidaDetalle(Base):
    __tablename__ = "remito_salida_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    remito_id: Mapped[int] = mapped_column(ForeignKey("remitos_salida.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)
    precio_unitario: Mapped[float] = mapped_column(Float, default=0.0)

    remito = relationship("RemitoSalida", back_populates="detalles")


# === FACTURA DE VENTA ===

class FacturaVenta(Base, TimestampMixin):
    """Documento fiscal. Genera derecho de cobro."""
    __tablename__ = "facturas_venta"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(50))  # A-0001-00000123
    tipo_comprobante: Mapped[str] = mapped_column(String(5), default="A")  # A, B, C, E
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    cliente_nombre: Mapped[str] = mapped_column(String(200), default="")
    cliente_cuit: Mapped[str] = mapped_column(String(30), default="")
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos_venta.id"), nullable=True)
    remito_id: Mapped[int] = mapped_column(ForeignKey("remitos_salida.id"), nullable=True)
    condicion_pago: Mapped[str] = mapped_column(String(100), default="")
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    descuento: Mapped[float] = mapped_column(Float, default=0.0)
    subtotal_neto: Mapped[float] = mapped_column(Float, default=0.0)
    iva_porcentaje: Mapped[float] = mapped_column(Float, default=0.0)
    iva_monto: Mapped[float] = mapped_column(Float, default=0.0)
    percepciones: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    estado: Mapped[str] = mapped_column(String(20), default="emitida")  # emitida, cobrada, anulada
    cae: Mapped[str] = mapped_column(String(20), default="")  # Factura electronica
    cae_vencimiento: Mapped[date] = mapped_column(Date, nullable=True)
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("FacturaVentaDetalle", back_populates="factura", cascade="all, delete-orphan")


class FacturaVentaDetalle(Base):
    __tablename__ = "factura_venta_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    factura_id: Mapped[int] = mapped_column(ForeignKey("facturas_venta.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)
    precio_unitario: Mapped[float] = mapped_column(Float, default=0.0)
    descuento: Mapped[float] = mapped_column(Float, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)

    factura = relationship("FacturaVenta", back_populates="detalles")


# === NOTAS DE CREDITO / DEBITO ===

class NotaCreditoDebito(Base, TimestampMixin):
    """Nota de credito (devolucion/anulacion) o debito (cargo adicional)."""
    __tablename__ = "notas_credito_debito"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(50))
    tipo: Mapped[str] = mapped_column(String(10))  # credito, debito
    tipo_comprobante: Mapped[str] = mapped_column(String(5), default="A")
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    cliente_nombre: Mapped[str] = mapped_column(String(200), default="")
    factura_id: Mapped[int] = mapped_column(ForeignKey("facturas_venta.id"), nullable=True)
    motivo: Mapped[str] = mapped_column(String(250), default="")  # devolucion, anulacion, correccion_precio, bonificacion
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    iva_monto: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    estado: Mapped[str] = mapped_column(String(20), default="emitida")  # emitida, aplicada, anulada
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("NotaCreditoDebitoDetalle", back_populates="nota", cascade="all, delete-orphan")


class NotaCreditoDebitoDetalle(Base):
    __tablename__ = "nota_credito_debito_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    nota_id: Mapped[int] = mapped_column(ForeignKey("notas_credito_debito.id"))
    descripcion: Mapped[str] = mapped_column(String(250))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)
    precio_unitario: Mapped[float] = mapped_column(Float, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)

    nota = relationship("NotaCreditoDebito", back_populates="detalles")
