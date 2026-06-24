"""Sub-servicio: Reglas de descuento y promociones."""
from services.precios._base import *
from services.precios._base import _hoy


class DescuentosService:
    def listar_reglas_descuento(self, solo_activas: bool = True):
        with get_db() as db:
            q = db.query(ReglaDescuento)
            if solo_activas:
                q = q.filter(ReglaDescuento.activo.is_(True))
            return q.order_by(ReglaDescuento.prioridad.desc()).all()

    def crear_regla_descuento(self, datos: dict) -> ReglaDescuento:
        with get_db() as db:
            regla = ReglaDescuento(**datos)
            db.add(regla)
            db.flush()
            return regla

    def eliminar_regla_descuento(self, regla_id: int):
        with get_db() as db:
            r = db.get(ReglaDescuento, regla_id)
            if r:
                r.activo = False

    def calcular_descuento(self, producto_id: int, cantidad: float, cliente_id: int = None, categoria_cliente: str = "") -> float:
        hoy = _hoy()
        with get_db() as db:
            reglas = db.query(ReglaDescuento).filter(ReglaDescuento.activo.is_(True)).order_by(ReglaDescuento.prioridad.desc()).all()
            mejor = 0.0
            for r in reglas:
                if r.fecha_desde and hoy < r.fecha_desde:
                    continue
                if r.fecha_hasta and hoy > r.fecha_hasta:
                    continue
                aplica = False
                if r.tipo == "volumen" and cantidad >= r.cantidad_minima:
                    if not r.producto_id or r.producto_id == producto_id:
                        aplica = True
                elif r.tipo == "cliente" and cliente_id:
                    if r.cliente_id == cliente_id or (r.categoria_cliente and r.categoria_cliente == categoria_cliente):
                        aplica = True
                elif r.tipo == "producto" and r.producto_id == producto_id:
                    aplica = True
                elif r.tipo == "promocion" and (not r.producto_id or r.producto_id == producto_id):
                    aplica = True
                if aplica and r.descuento_porcentaje > mejor:
                    mejor = r.descuento_porcentaje
            return mejor
