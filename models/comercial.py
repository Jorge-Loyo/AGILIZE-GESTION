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
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    impuesto: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, en_proceso, entregado, cancelado
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
