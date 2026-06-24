"""Sub-servicio: Tipo de cambio y conversion de moneda."""
from services.precios._base import *
from services.precios._base import _hoy


class MonedaService:
    def registrar_tipo_cambio(self, moneda_origen: str, moneda_destino: str, tasa_compra: float, tasa_venta: float, fuente: str = "manual"):
        with get_db() as db:
            tc = TipoCambio(fecha=_hoy(), moneda_origen=moneda_origen[:10].upper(), moneda_destino=moneda_destino[:10].upper(), tasa_compra=tasa_compra, tasa_venta=tasa_venta, fuente=fuente[:50])
            db.add(tc)
            db.flush()
            return tc

    def obtener_tipo_cambio(self, moneda_origen: str, moneda_destino: str, fecha: date = None) -> dict:
        fecha_buscar = fecha or _hoy()
        with get_db() as db:
            tc = db.query(TipoCambio).filter(TipoCambio.moneda_origen == moneda_origen.upper(), TipoCambio.moneda_destino == moneda_destino.upper(), TipoCambio.fecha <= fecha_buscar).order_by(TipoCambio.fecha.desc()).first()
            if not tc:
                return {"tasa_compra": 0, "tasa_venta": 0, "fecha": None, "fuente": ""}
            return {"tasa_compra": tc.tasa_compra, "tasa_venta": tc.tasa_venta, "fecha": tc.fecha, "fuente": tc.fuente}

    def convertir_monto(self, monto: float, moneda_origen: str, moneda_destino: str, tipo: str = "venta") -> float:
        if moneda_origen.upper() == moneda_destino.upper():
            return monto
        tc = self.obtener_tipo_cambio(moneda_origen, moneda_destino)
        tasa = tc["tasa_venta"] if tipo == "venta" else tc["tasa_compra"]
        if tasa <= 0:
            raise ValueError(f"No hay tipo de cambio para {moneda_origen}/{moneda_destino}")
        return round(monto * tasa, 2)

    def historial_tipo_cambio(self, moneda_origen: str, moneda_destino: str, dias: int = 30):
        fecha_desde = _hoy() - timedelta(days=dias)
        with get_db() as db:
            return db.query(TipoCambio).filter(TipoCambio.moneda_origen == moneda_origen.upper(), TipoCambio.moneda_destino == moneda_destino.upper(), TipoCambio.fecha >= fecha_desde).order_by(TipoCambio.fecha.desc()).all()
