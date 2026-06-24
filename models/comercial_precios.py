"""Modelos de politica comercial: listas de precios, descuentos, monedas."""
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date


class ListaPrecioVenta(Base, TimestampMixin):
    """Listas de precios para venta: mayorista, minorista, distribuidor, etc."""
    __tablename__ = "listas_precio_venta"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    moneda: Mapped[str] = mapped_column(String(10), default="USD")
    margen_sobre_costo: Mapped[float] = mapped_column(Float, default=0)  # % sobre costo (alternativo)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    items = relationship("ListaPrecioVentaItem", back_populates="lista", cascade="all, delete-orphan")


class ListaPrecioVentaItem(Base):
    """Precio especifico por producto en una lista."""
    __tablename__ = "lista_precio_venta_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    lista_id: Mapped[int] = mapped_column(ForeignKey("listas_precio_venta.id"))
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    precio: Mapped[float] = mapped_column(Float, default=0)

    lista = relationship("ListaPrecioVenta", back_populates="items")


class ReglaDescuento(Base, TimestampMixin):
    """Reglas de descuento: por volumen, por cliente, por producto, promociones temporales."""
    __tablename__ = "reglas_descuento"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    tipo: Mapped[str] = mapped_column(String(20))  # volumen, cliente, producto, promocion
    # Condiciones
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias_producto.id"), nullable=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    categoria_cliente: Mapped[str] = mapped_column(String(50), default="")  # mayorista, VIP, etc
    cantidad_minima: Mapped[float] = mapped_column(Float, default=0)  # para descuento por volumen
    # Descuento
    descuento_porcentaje: Mapped[float] = mapped_column(Float, default=0)
    descuento_monto: Mapped[float] = mapped_column(Float, default=0)  # monto fijo
    # Vigencia
    fecha_desde: Mapped[date] = mapped_column(Date, nullable=True)
    fecha_hasta: Mapped[date] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    prioridad: Mapped[int] = mapped_column(Integer, default=0)  # mayor = se aplica primero


class TipoCambio(Base, TimestampMixin):
    """Tipos de cambio diarios para conversion de moneda."""
    __tablename__ = "tipos_cambio"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date)
    moneda_origen: Mapped[str] = mapped_column(String(10))  # USD, EUR
    moneda_destino: Mapped[str] = mapped_column(String(10))  # ARS, VES
    tasa_compra: Mapped[float] = mapped_column(Float, default=0)
    tasa_venta: Mapped[float] = mapped_column(Float, default=0)
    fuente: Mapped[str] = mapped_column(String(50), default="")  # manual, BCV, BNA
