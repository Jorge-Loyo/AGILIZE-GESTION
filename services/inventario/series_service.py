"""Sub-servicio: Numeros de serie y garantias."""
from datetime import timedelta
from services.inventario._base import *
from services.inventario._base import _hoy


class SeriesService:
    def crear_numero_serie(self, producto_id: int, numero_serie: str, lote_id: int = None, deposito_id: int = None, garantia_meses: int = 0) -> NumeroSerie:
        with get_db() as db:
            ns = NumeroSerie(producto_id=producto_id, numero_serie=numero_serie[:100], lote_id=lote_id, deposito_id=deposito_id, garantia_meses=garantia_meses)
            db.add(ns)
            db.flush()
            return ns

    def crear_series_masivo(self, producto_id: int, numeros: list, lote_id: int = None, deposito_id: int = None, garantia_meses: int = 0) -> int:
        creados = 0
        with get_db() as db:
            for numero in numeros:
                db.add(NumeroSerie(producto_id=producto_id, numero_serie=str(numero)[:100], lote_id=lote_id, deposito_id=deposito_id, garantia_meses=garantia_meses))
                creados += 1
        return creados

    def listar_series(self, producto_id: int = None, estado: str = None, deposito_id: int = None):
        with get_db() as db:
            q = db.query(NumeroSerie)
            if producto_id:
                q = q.filter(NumeroSerie.producto_id == producto_id)
            if estado:
                q = q.filter(NumeroSerie.estado == estado)
            if deposito_id:
                q = q.filter(NumeroSerie.deposito_id == deposito_id)
            return q.order_by(NumeroSerie.created_at.desc()).all()

    def buscar_serie(self, numero_serie: str):
        with get_db() as db:
            return db.query(NumeroSerie).filter(NumeroSerie.numero_serie == numero_serie).first()

    def vender_serie(self, numero_serie_id: int, cliente_id: int = None, factura_referencia: str = ""):
        with get_db() as db:
            ns = db.get(NumeroSerie, numero_serie_id)
            if not ns:
                raise ValueError("Numero de serie no encontrado")
            if ns.estado != "disponible":
                raise ValueError(f"Serie no disponible. Estado actual: {ns.estado}")
            ns.estado = "vendido"
            ns.cliente_id = cliente_id
            ns.fecha_venta = _hoy()
            ns.factura_referencia = factura_referencia[:50]
            if ns.garantia_meses > 0:
                ns.fecha_fin_garantia = _hoy() + timedelta(days=ns.garantia_meses * 30)

    def devolver_serie(self, numero_serie_id: int, motivo: str = ""):
        with get_db() as db:
            ns = db.get(NumeroSerie, numero_serie_id)
            if not ns:
                raise ValueError("Numero de serie no encontrado")
            ns.estado = "devuelto"
            ns.observaciones = motivo[:250]

    def serie_en_garantia(self, numero_serie_id: int) -> bool:
        with get_db() as db:
            ns = db.get(NumeroSerie, numero_serie_id)
            if not ns or not ns.fecha_fin_garantia:
                return False
            return _hoy() <= ns.fecha_fin_garantia

    def series_en_garantia_activa(self):
        with get_db() as db:
            return db.query(NumeroSerie).filter(NumeroSerie.estado == "vendido", NumeroSerie.fecha_fin_garantia.isnot(None), NumeroSerie.fecha_fin_garantia >= _hoy()).order_by(NumeroSerie.fecha_fin_garantia).all()

    def dar_baja_serie(self, numero_serie_id: int, motivo: str = ""):
        with get_db() as db:
            ns = db.get(NumeroSerie, numero_serie_id)
            if ns:
                ns.estado = "dado_baja"
                ns.observaciones = motivo[:250]
