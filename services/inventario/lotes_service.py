"""Sub-servicio: Lotes y vencimientos."""
from datetime import timedelta
from services.inventario._base import *
from services.inventario._base import _hoy


class LotesService:
    def crear_lote(self, producto_id: int, numero_lote: str, cantidad: int, fecha_fabricacion=None, fecha_vencimiento=None, proveedor_id: int = None, deposito_id: int = None, observaciones: str = "") -> LoteProducto:
        with get_db() as db:
            lote = LoteProducto(producto_id=producto_id, numero_lote=numero_lote[:50], fecha_fabricacion=fecha_fabricacion, fecha_vencimiento=fecha_vencimiento, proveedor_id=proveedor_id, deposito_id=deposito_id, cantidad_inicial=cantidad, cantidad_actual=cantidad, observaciones=observaciones[:250])
            db.add(lote)
            db.flush()
            return lote

    def listar_lotes(self, producto_id: int = None, solo_activos: bool = True):
        with get_db() as db:
            q = db.query(LoteProducto)
            if producto_id:
                q = q.filter(LoteProducto.producto_id == producto_id)
            if solo_activos:
                q = q.filter(LoteProducto.estado == "activo")
            return q.order_by(LoteProducto.fecha_vencimiento).all()

    def lotes_por_vencer(self, dias: int = 30):
        fecha_limite = _hoy() + timedelta(days=dias)
        with get_db() as db:
            return db.query(LoteProducto).filter(
                LoteProducto.estado == "activo", LoteProducto.fecha_vencimiento.isnot(None),
                LoteProducto.fecha_vencimiento <= fecha_limite, LoteProducto.cantidad_actual > 0,
            ).order_by(LoteProducto.fecha_vencimiento).all()

    def lotes_vencidos(self):
        with get_db() as db:
            return db.query(LoteProducto).filter(
                LoteProducto.estado == "activo", LoteProducto.fecha_vencimiento.isnot(None),
                LoteProducto.fecha_vencimiento < _hoy(), LoteProducto.cantidad_actual > 0,
            ).order_by(LoteProducto.fecha_vencimiento).all()

    def consumir_lote(self, lote_id: int, cantidad: int):
        with get_db() as db:
            lote = db.get(LoteProducto, lote_id)
            if not lote:
                raise ValueError("Lote no encontrado")
            if lote.cantidad_actual < cantidad:
                raise ValueError(f"Stock insuficiente en lote. Disponible: {lote.cantidad_actual}")
            lote.cantidad_actual -= cantidad
            if lote.cantidad_actual == 0:
                lote.estado = "agotado"

    def retirar_lote(self, lote_id: int, motivo: str = ""):
        with get_db() as db:
            lote = db.get(LoteProducto, lote_id)
            if lote:
                lote.estado = "retirado"
                lote.observaciones = motivo[:250] if motivo else "Retirado"
