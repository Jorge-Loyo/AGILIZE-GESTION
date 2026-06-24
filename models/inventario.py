"""Modelos de inventario: productos, depositos, stock, UOM, codigos, kits."""
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

    subcategorias = relationship("SubcategoriaProducto", back_populates="categoria")
    productos = relationship("Producto", back_populates="categoria")


class SubcategoriaProducto(Base, TimestampMixin):
    __tablename__ = "subcategorias_producto"

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias_producto.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    categoria = relationship("CategoriaProducto", back_populates="subcategorias")
    productos = relationship("Producto", back_populates="subcategoria")


class MarcaProducto(Base, TimestampMixin):
    __tablename__ = "marcas_producto"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    productos = relationship("Producto", back_populates="marca")


class UnidadMedida(Base, TimestampMixin):
    """Unidades de medida: unidad, kg, litro, caja, pallet, etc."""
    __tablename__ = "unidades_medida"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(10), unique=True)  # UN, KG, LT, CJ, PL
    nombre: Mapped[str] = mapped_column(String(50))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class ConversionUOM(Base):
    """Tabla de conversion entre unidades. Ej: 1 CJ = 12 UN."""
    __tablename__ = "conversiones_uom"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=True)
    uom_origen_id: Mapped[int] = mapped_column(ForeignKey("unidades_medida.id"))
    uom_destino_id: Mapped[int] = mapped_column(ForeignKey("unidades_medida.id"))
    factor: Mapped[float] = mapped_column(Float, default=1.0)  # 1 origen = factor destino

    uom_origen = relationship("UnidadMedida", foreign_keys=[uom_origen_id])
    uom_destino = relationship("UnidadMedida", foreign_keys=[uom_destino_id])


class Producto(Base, TimestampMixin):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    # Tipo de articulo
    tipo_articulo: Mapped[str] = mapped_column(String(20), default="fisico")  # fisico, servicio, kit
    # Clasificacion jerarquica
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias_producto.id"), nullable=True)
    subcategoria_id: Mapped[int] = mapped_column(ForeignKey("subcategorias_producto.id"), nullable=True)
    marca_id: Mapped[int] = mapped_column(ForeignKey("marcas_producto.id"), nullable=True)
    # UOM
    unidad_medida: Mapped[str] = mapped_column(String(20), default="unidad")
    uom_compra_id: Mapped[int] = mapped_column(ForeignKey("unidades_medida.id"), nullable=True)
    uom_venta_id: Mapped[int] = mapped_column(ForeignKey("unidades_medida.id"), nullable=True)
    # Precios
    precio_costo: Mapped[float] = mapped_column(Float, default=0.0)
    precio_venta: Mapped[float] = mapped_column(Float, default=0.0)
    stock_minimo: Mapped[int] = mapped_column(Integer, default=0)
    stock_maximo: Mapped[int] = mapped_column(Integer, default=0)
    punto_pedido: Mapped[int] = mapped_column(Integer, default=0)  # nivel donde se dispara alerta/reposicion
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    categoria = relationship("CategoriaProducto", back_populates="productos")
    subcategoria = relationship("SubcategoriaProducto", back_populates="productos")
    marca = relationship("MarcaProducto", back_populates="productos")
    uom_compra = relationship("UnidadMedida", foreign_keys=[uom_compra_id])
    uom_venta = relationship("UnidadMedida", foreign_keys=[uom_venta_id])
    stock_depositos = relationship("StockDeposito", back_populates="producto")
    movimientos = relationship("MovimientoStock", back_populates="producto")
    codigos_barra = relationship("CodigoBarraProducto", back_populates="producto", cascade="all, delete-orphan")
    kit_componentes = relationship("KitDetalle", back_populates="kit", foreign_keys="KitDetalle.kit_id", cascade="all, delete-orphan")

    @property
    def stock_total(self) -> int:
        return sum(sd.cantidad for sd in self.stock_depositos)


class CodigoBarraProducto(Base):
    """Multiples codigos de barra/SKU por producto."""
    __tablename__ = "codigos_barra_producto"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    codigo: Mapped[str] = mapped_column(String(50))
    tipo: Mapped[str] = mapped_column(String(30), default="propio")  # propio, proveedor, interno, ean13, ean8
    descripcion: Mapped[str] = mapped_column(String(100), default="")
    principal: Mapped[bool] = mapped_column(Boolean, default=False)

    producto = relationship("Producto", back_populates="codigos_barra")


class KitDetalle(Base):
    """Componentes de un producto tipo Kit/Combo."""
    __tablename__ = "kit_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    kit_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    componente_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    cantidad: Mapped[float] = mapped_column(Float, default=1.0)

    kit = relationship("Producto", foreign_keys=[kit_id], back_populates="kit_componentes")
    componente = relationship("Producto", foreign_keys=[componente_id])


class Deposito(Base, TimestampMixin):
    __tablename__ = "depositos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[str] = mapped_column(String(30), default="general")  # general, central, sucursal, fallados, devolucion, transito
    direccion: Mapped[str] = mapped_column(String(250), default="")
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursales.id"), nullable=True)
    responsable: Mapped[str] = mapped_column(String(150), default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    sucursal = relationship("Sucursal")
    ubicaciones = relationship("UbicacionDeposito", back_populates="deposito", cascade="all, delete-orphan")
    stock = relationship("StockDeposito", back_populates="deposito")
    movimientos = relationship("MovimientoStock", back_populates="deposito", foreign_keys="MovimientoStock.deposito_id")


class UbicacionDeposito(Base, TimestampMixin):
    """Posicion logistica dentro de un deposito: Pasillo-Estanteria-Altura."""
    __tablename__ = "ubicaciones_deposito"

    id: Mapped[int] = mapped_column(primary_key=True)
    deposito_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"))
    codigo: Mapped[str] = mapped_column(String(30))  # Ej: A-03-2 (Pasillo A, Estante 3, Altura 2)
    pasillo: Mapped[str] = mapped_column(String(10), default="")
    estanteria: Mapped[str] = mapped_column(String(10), default="")
    altura: Mapped[str] = mapped_column(String(10), default="")
    descripcion: Mapped[str] = mapped_column(String(100), default="")
    capacidad: Mapped[int] = mapped_column(Integer, default=0)  # 0 = ilimitada
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    deposito = relationship("Deposito", back_populates="ubicaciones")


class StockDeposito(Base, TimestampMixin):
    __tablename__ = "stock_deposito"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    deposito_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"))
    ubicacion_id: Mapped[int] = mapped_column(ForeignKey("ubicaciones_deposito.id"), nullable=True)
    cantidad: Mapped[int] = mapped_column(Integer, default=0)

    producto = relationship("Producto", back_populates="stock_depositos")
    deposito = relationship("Deposito", back_populates="stock")
    ubicacion = relationship("UbicacionDeposito")


class MovimientoStock(Base, TimestampMixin):
    __tablename__ = "movimientos_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    deposito_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"))
    deposito_destino_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"), nullable=True)
    ubicacion_id: Mapped[int] = mapped_column(ForeignKey("ubicaciones_deposito.id"), nullable=True)
    ubicacion_destino_id: Mapped[int] = mapped_column(ForeignKey("ubicaciones_deposito.id"), nullable=True)
    lote_id: Mapped[int] = mapped_column(ForeignKey("lotes_producto.id"), nullable=True)
    numero_serie_id: Mapped[int] = mapped_column(ForeignKey("numeros_serie.id"), nullable=True)
    tipo: Mapped[str] = mapped_column(String(20))  # entrada, salida, transferencia, ajuste, reubicacion
    cantidad: Mapped[int] = mapped_column(Integer)
    motivo: Mapped[str] = mapped_column(String(250), default="")
    referencia: Mapped[str] = mapped_column(String(100), default="")
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    producto = relationship("Producto", back_populates="movimientos")
    deposito = relationship("Deposito", back_populates="movimientos", foreign_keys=[deposito_id])
    deposito_destino = relationship("Deposito", foreign_keys=[deposito_destino_id])
    ubicacion = relationship("UbicacionDeposito", foreign_keys=[ubicacion_id])
    ubicacion_destino = relationship("UbicacionDeposito", foreign_keys=[ubicacion_destino_id])
    lote = relationship("LoteProducto", foreign_keys=[lote_id])
    numero_serie = relationship("NumeroSerie", foreign_keys=[numero_serie_id])


# === LOTES Y VENCIMIENTOS ===

class LoteProducto(Base, TimestampMixin):
    """Control de lotes con fecha de vencimiento."""
    __tablename__ = "lotes_producto"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    numero_lote: Mapped[str] = mapped_column(String(50))
    fecha_fabricacion: Mapped[date] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=True)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedores.id"), nullable=True)
    deposito_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"), nullable=True)
    cantidad_inicial: Mapped[int] = mapped_column(Integer, default=0)
    cantidad_actual: Mapped[int] = mapped_column(Integer, default=0)
    estado: Mapped[str] = mapped_column(String(20), default="activo")  # activo, agotado, vencido, retirado
    observaciones: Mapped[str] = mapped_column(String(250), default="")

    producto = relationship("Producto")


# === NUMEROS DE SERIE ===

class NumeroSerie(Base, TimestampMixin):
    """Control unitario por numero de serie (electronica, electrodomesticos)."""
    __tablename__ = "numeros_serie"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    numero_serie: Mapped[str] = mapped_column(String(100), unique=True)
    lote_id: Mapped[int] = mapped_column(ForeignKey("lotes_producto.id"), nullable=True)
    deposito_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="disponible")  # disponible, vendido, en_garantia, devuelto, dado_baja
    # Trazabilidad de venta
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    fecha_venta: Mapped[date] = mapped_column(Date, nullable=True)
    factura_referencia: Mapped[str] = mapped_column(String(50), default="")
    # Garantia
    garantia_meses: Mapped[int] = mapped_column(Integer, default=0)
    fecha_fin_garantia: Mapped[date] = mapped_column(Date, nullable=True)
    observaciones: Mapped[str] = mapped_column(String(250), default="")

    producto = relationship("Producto")
    lote = relationship("LoteProducto")


# === INVENTARIO FISICO / TOMA DE STOCK ===

class TomaInventario(Base, TimestampMixin):
    """Encabezado de una toma de inventario fisico."""
    __tablename__ = "tomas_inventario"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    deposito_id: Mapped[int] = mapped_column(ForeignKey("depositos.id"))
    estado: Mapped[str] = mapped_column(String(20), default="abierta")  # abierta, contando, cerrada, ajustada
    observaciones: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    detalles = relationship("TomaInventarioDetalle", back_populates="toma", cascade="all, delete-orphan")


class TomaInventarioDetalle(Base):
    """Linea de conteo: stock teorico vs conteo fisico."""
    __tablename__ = "toma_inventario_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    toma_id: Mapped[int] = mapped_column(ForeignKey("tomas_inventario.id"))
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    stock_teorico: Mapped[int] = mapped_column(Integer, default=0)
    conteo_fisico: Mapped[int] = mapped_column(Integer, nullable=True)  # NULL = no contado aun
    diferencia: Mapped[int] = mapped_column(Integer, default=0)
    ajustado: Mapped[bool] = mapped_column(Boolean, default=False)

    toma = relationship("TomaInventario", back_populates="detalles")
