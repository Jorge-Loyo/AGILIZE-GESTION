from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date


class CategoriaProducto(Base, TimestampMixin):
    __tablename__ = "categorias_producto"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str] = mapped_column(String(250), default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    productos = relationship("Producto", back_populates="categoria")


class Producto(Base, TimestampMixin):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias_producto.id"), nullable=True)
    unidad_medida: Mapped[str] = mapped_column(String(20), default="unidad")
    precio_costo: Mapped[float] = mapped_column(Float, default=0.0)
    precio_venta: Mapped[float] = mapped_column(Float, default=0.0)
    stock_minimo: Mapped[int] = mapped_column(Integer, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    categoria = relationship("CategoriaProducto", back_populates="productos")
    stock_depositos = relationship("StockDeposito", back_populates="producto")
    movimientos = relationship("MovimientoStock", back_populates="producto")

    @property
    def stock_total(self) -> int:
        return sum(sd.cantidad for sd in self.stock_depositos)


class Deposito(Base, TimestampMixin):
    __tablename__ = "depositos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    direccion: Mapped[str] = mapped_column(String(250), default="")
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursales.id"), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    sucursal = relationship("Sucursal")
    stock = relationship("StockDeposito", back_populates="deposito")
    movimientos = relationship("MovimientoStock", back_populates="deposito", foreign_keys="MovimientoStock.deposito_id")


class StockDeposito(Base, TimestampMixin):
    __tablename__ = "stock_deposito"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    deposito_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"))
    cantidad: Mapped[int] = mapped_column(Integer, default=0)

    producto = relationship("Producto", back_populates="stock_depositos")
    deposito = relationship("Deposito", back_populates="stock")


class MovimientoStock(Base, TimestampMixin):
    __tablename__ = "movimientos_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    deposito_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"))
    deposito_destino_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"), nullable=True)
    tipo: Mapped[str] = mapped_column(String(20))  # entrada, salida, transferencia, ajuste
    cantidad: Mapped[int] = mapped_column(Integer)
    motivo: Mapped[str] = mapped_column(String(250), default="")
    referencia: Mapped[str] = mapped_column(String(100), default="")
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    producto = relationship("Producto", back_populates="movimientos")
    deposito = relationship("Deposito", back_populates="movimientos", foreign_keys=[deposito_id])
    deposito_destino = relationship("Deposito", foreign_keys=[deposito_destino_id])
