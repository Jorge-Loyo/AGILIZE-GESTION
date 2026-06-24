"""Servicio de inventario: productos, depositos, movimientos y stock."""
from datetime import date
from sqlalchemy import func
from core.database import get_db
# Importar todos los modelos para resolver relationships
from models import usuario, rol, permiso, empleado, sucursal  # noqa
from models.inventario import (
    CategoriaProducto, Producto, Deposito, StockDeposito, MovimientoStock
)
from services.auth_service import auth_service


class InventarioService:
    # === CATEGORIAS ===
    def listar_categorias(self):
        with get_db() as db:
            return db.query(CategoriaProducto).filter(
                CategoriaProducto.activo == True
            ).order_by(CategoriaProducto.nombre).all()

    def crear_categoria(self, nombre: str, descripcion: str = "") -> CategoriaProducto:
        with get_db() as db:
            cat = CategoriaProducto(nombre=nombre, descripcion=descripcion)
            db.add(cat)
            db.flush()
            return cat

    # === PRODUCTOS ===
    def listar_productos(self, solo_activos=True):
        with get_db() as db:
            q = db.query(Producto)
            if solo_activos:
                q = q.filter(Producto.activo == True)
            return q.order_by(Producto.nombre).all()

    def buscar_productos(self, texto: str):
        with get_db() as db:
            return db.query(Producto).filter(
                Producto.activo == True,
                (Producto.nombre.ilike(f"%{texto}%")) | (Producto.codigo.ilike(f"%{texto}%"))
            ).order_by(Producto.nombre).all()

    def obtener_producto(self, producto_id: int):
        with get_db() as db:
            return db.get(Producto, producto_id)

    def crear_producto(self, datos: dict) -> Producto:
        with get_db() as db:
            producto = Producto(**datos)
            db.add(producto)
            db.flush()
            return producto

    def actualizar_producto(self, producto_id: int, datos: dict):
        with get_db() as db:
            producto = db.get(Producto, producto_id)
            if not producto:
                raise ValueError("Producto no encontrado")
            for k, v in datos.items():
                setattr(producto, k, v)

    def desactivar_producto(self, producto_id: int):
        with get_db() as db:
            producto = db.get(Producto, producto_id)
            if producto:
                producto.activo = not producto.activo

    # === DEPOSITOS ===
    def listar_depositos(self, solo_activos=True):
        with get_db() as db:
            q = db.query(Deposito)
            if solo_activos:
                q = q.filter(Deposito.activo == True)
            return q.order_by(Deposito.nombre).all()

    def crear_deposito(self, nombre: str, direccion: str = "", sucursal_id: int = None) -> Deposito:
        with get_db() as db:
            deposito = Deposito(nombre=nombre, direccion=direccion, sucursal_id=sucursal_id)
            db.add(deposito)
            db.flush()
            return deposito

    def actualizar_deposito(self, deposito_id: int, datos: dict):
        with get_db() as db:
            deposito = db.get(Deposito, deposito_id)
            if not deposito:
                raise ValueError("Deposito no encontrado")
            for k, v in datos.items():
                setattr(deposito, k, v)

    # === STOCK ===
    def obtener_stock(self, producto_id: int, deposito_id: int) -> int:
        with get_db() as db:
            sd = db.query(StockDeposito).filter(
                StockDeposito.producto_id == producto_id,
                StockDeposito.deposito_id == deposito_id
            ).first()
            return sd.cantidad if sd else 0

    def obtener_stock_total(self, producto_id: int) -> int:
        with get_db() as db:
            result = db.query(func.sum(StockDeposito.cantidad)).filter(
                StockDeposito.producto_id == producto_id
            ).scalar()
            return result or 0

    def stock_por_deposito(self, deposito_id: int):
        """Retorna todos los productos con stock en un deposito."""
        with get_db() as db:
            return db.query(StockDeposito).filter(
                StockDeposito.deposito_id == deposito_id,
                StockDeposito.cantidad > 0
            ).all()

    def productos_bajo_minimo(self):
        """Retorna productos cuyo stock total esta por debajo del minimo."""
        with get_db() as db:
            productos = db.query(Producto).filter(Producto.activo == True, Producto.stock_minimo > 0).all()
            resultado = []
            for p in productos:
                total = db.query(func.sum(StockDeposito.cantidad)).filter(
                    StockDeposito.producto_id == p.id
                ).scalar() or 0
                if total < p.stock_minimo:
                    resultado.append({"producto": p, "stock_actual": total, "stock_minimo": p.stock_minimo})
            return resultado

    # === MOVIMIENTOS ===
    def registrar_entrada(self, producto_id: int, deposito_id: int, cantidad: int, motivo: str = "", referencia: str = ""):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        with get_db() as db:
            self._ajustar_stock(db, producto_id, deposito_id, cantidad)
            mov = MovimientoStock(
                producto_id=producto_id,
                deposito_id=deposito_id,
                tipo="entrada",
                cantidad=cantidad,
                motivo=motivo,
                referencia=referencia,
                fecha=date.today(),
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(mov)

    def registrar_salida(self, producto_id: int, deposito_id: int, cantidad: int, motivo: str = "", referencia: str = ""):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        with get_db() as db:
            stock_actual = db.query(StockDeposito).filter(
                StockDeposito.producto_id == producto_id,
                StockDeposito.deposito_id == deposito_id
            ).first()
            if not stock_actual or stock_actual.cantidad < cantidad:
                raise ValueError(f"Stock insuficiente. Disponible: {stock_actual.cantidad if stock_actual else 0}")
            self._ajustar_stock(db, producto_id, deposito_id, -cantidad)
            mov = MovimientoStock(
                producto_id=producto_id,
                deposito_id=deposito_id,
                tipo="salida",
                cantidad=cantidad,
                motivo=motivo,
                referencia=referencia,
                fecha=date.today(),
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(mov)

    def registrar_transferencia(self, producto_id: int, deposito_origen_id: int, deposito_destino_id: int, cantidad: int, motivo: str = ""):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        if deposito_origen_id == deposito_destino_id:
            raise ValueError("Origen y destino deben ser diferentes")
        with get_db() as db:
            stock_origen = db.query(StockDeposito).filter(
                StockDeposito.producto_id == producto_id,
                StockDeposito.deposito_id == deposito_origen_id
            ).first()
            if not stock_origen or stock_origen.cantidad < cantidad:
                raise ValueError(f"Stock insuficiente en origen. Disponible: {stock_origen.cantidad if stock_origen else 0}")
            self._ajustar_stock(db, producto_id, deposito_origen_id, -cantidad)
            self._ajustar_stock(db, producto_id, deposito_destino_id, cantidad)
            mov = MovimientoStock(
                producto_id=producto_id,
                deposito_id=deposito_origen_id,
                deposito_destino_id=deposito_destino_id,
                tipo="transferencia",
                cantidad=cantidad,
                motivo=motivo,
                fecha=date.today(),
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(mov)

    def registrar_ajuste(self, producto_id: int, deposito_id: int, nueva_cantidad: int, motivo: str = ""):
        with get_db() as db:
            sd = db.query(StockDeposito).filter(
                StockDeposito.producto_id == producto_id,
                StockDeposito.deposito_id == deposito_id
            ).first()
            cantidad_anterior = sd.cantidad if sd else 0
            diferencia = nueva_cantidad - cantidad_anterior

            if not sd:
                sd = StockDeposito(producto_id=producto_id, deposito_id=deposito_id, cantidad=nueva_cantidad)
                db.add(sd)
            else:
                sd.cantidad = nueva_cantidad

            mov = MovimientoStock(
                producto_id=producto_id,
                deposito_id=deposito_id,
                tipo="ajuste",
                cantidad=diferencia,
                motivo=motivo or f"Ajuste de {cantidad_anterior} a {nueva_cantidad}",
                fecha=date.today(),
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(mov)

    def listar_movimientos(self, producto_id: int = None, deposito_id: int = None, limite: int = 100):
        with get_db() as db:
            q = db.query(MovimientoStock)
            if producto_id:
                q = q.filter(MovimientoStock.producto_id == producto_id)
            if deposito_id:
                q = q.filter(MovimientoStock.deposito_id == deposito_id)
            return q.order_by(MovimientoStock.created_at.desc()).limit(limite).all()

    # === RESUMEN ===
    def resumen(self) -> dict:
        with get_db() as db:
            total_productos = db.query(Producto).filter(Producto.activo == True).count()
            total_depositos = db.query(Deposito).filter(Deposito.activo == True).count()
            total_stock = db.query(func.sum(StockDeposito.cantidad)).scalar() or 0
            valor_inventario = db.query(
                func.sum(StockDeposito.cantidad * Producto.precio_costo)
            ).join(Producto).scalar() or 0
            movimientos_hoy = db.query(MovimientoStock).filter(
                MovimientoStock.fecha == date.today()
            ).count()
            return {
                "total_productos": total_productos,
                "total_depositos": total_depositos,
                "total_stock": int(total_stock),
                "valor_inventario": float(valor_inventario),
                "movimientos_hoy": movimientos_hoy,
            }

    @staticmethod
    def _ajustar_stock(db, producto_id: int, deposito_id: int, cantidad: int):
        sd = db.query(StockDeposito).filter(
            StockDeposito.producto_id == producto_id,
            StockDeposito.deposito_id == deposito_id
        ).first()
        if not sd:
            sd = StockDeposito(producto_id=producto_id, deposito_id=deposito_id, cantidad=0)
            db.add(sd)
            db.flush()
        sd.cantidad += cantidad


inventario_service = InventarioService()
