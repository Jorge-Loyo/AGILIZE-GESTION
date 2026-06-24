"""Sub-servicio: Listas de precios de venta."""
from services.precios._base import *
from services.precios._base import _hoy


class ListasPrecioService:
    def listar_listas(self):
        with get_db() as db:
            return db.query(ListaPrecioVenta).filter(ListaPrecioVenta.activo.is_(True)).order_by(ListaPrecioVenta.nombre).all()

    def crear_lista(self, codigo: str, nombre: str, moneda: str = "USD", margen: float = 0) -> ListaPrecioVenta:
        with get_db() as db:
            lista = ListaPrecioVenta(codigo=codigo[:20].upper(), nombre=nombre[:100], moneda=moneda[:10], margen_sobre_costo=margen)
            db.add(lista)
            db.flush()
            return lista

    def obtener_precio_lista(self, producto_id: int, lista_codigo: str) -> float:
        with get_db() as db:
            lista = db.query(ListaPrecioVenta).filter(ListaPrecioVenta.codigo == lista_codigo).first()
            if not lista:
                return 0
            item = db.query(ListaPrecioVentaItem).filter(ListaPrecioVentaItem.lista_id == lista.id, ListaPrecioVentaItem.producto_id == producto_id).first()
            if item:
                return item.precio
            if lista.margen_sobre_costo > 0:
                prod = db.get(Producto, producto_id)
                if prod and prod.precio_costo:
                    return round(prod.precio_costo * (1 + lista.margen_sobre_costo / 100), 2)
            prod = db.get(Producto, producto_id)
            return prod.precio_venta if prod else 0

    def asignar_precio(self, lista_id: int, producto_id: int, precio: float):
        with get_db() as db:
            item = db.query(ListaPrecioVentaItem).filter(ListaPrecioVentaItem.lista_id == lista_id, ListaPrecioVentaItem.producto_id == producto_id).first()
            if item:
                item.precio = precio
            else:
                db.add(ListaPrecioVentaItem(lista_id=lista_id, producto_id=producto_id, precio=precio))

    def items_lista(self, lista_id: int):
        with get_db() as db:
            return db.query(ListaPrecioVentaItem).filter(ListaPrecioVentaItem.lista_id == lista_id).all()
