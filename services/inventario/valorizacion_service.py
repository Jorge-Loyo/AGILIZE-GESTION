"""Sub-servicio: Valorizacion de inventario (PPP, FIFO, LIFO)."""
from services.inventario._base import *


class ValorizacionService:
    def valorizar_inventario(self, metodo: str = "ppp", deposito_id: int = None) -> dict:
        with get_db() as db:
            q = db.query(StockDeposito).options(joinedload(StockDeposito.producto))
            if deposito_id:
                q = q.filter(StockDeposito.deposito_id == deposito_id)
            stocks = q.filter(StockDeposito.cantidad > 0).all()
            if metodo == "ppp":
                return self._valorizar_ppp(stocks)
            elif metodo == "fifo":
                return self._valorizar_fifo(db, stocks)
            elif metodo == "lifo":
                return self._valorizar_lifo(db, stocks)
            raise ValueError(f"Metodo no soportado: {metodo}")

    def _valorizar_ppp(self, stocks) -> dict:
        total = 0.0
        items = []
        for sd in stocks:
            valor = sd.cantidad * (sd.producto.precio_costo or 0)
            total += valor
            items.append({"codigo": sd.producto.codigo, "nombre": sd.producto.nombre, "cantidad": sd.cantidad, "costo_unitario": sd.producto.precio_costo or 0, "valor": valor})
        return {"metodo": "PPP", "total": round(total, 2), "items": items}

    def _valorizar_fifo(self, db, stocks) -> dict:
        total = 0.0
        items = []
        for sd in stocks:
            entradas = db.query(MovimientoStock).filter(MovimientoStock.producto_id == sd.producto_id, MovimientoStock.deposito_id == sd.deposito_id, MovimientoStock.tipo == "entrada").order_by(MovimientoStock.fecha.asc()).all()
            valor = self._calcular_valor_por_capas(entradas, sd.cantidad, sd.producto)
            total += valor
            items.append({"codigo": sd.producto.codigo, "nombre": sd.producto.nombre, "cantidad": sd.cantidad, "valor": valor, "costo_unitario": round(valor / sd.cantidad, 2) if sd.cantidad else 0})
        return {"metodo": "FIFO", "total": round(total, 2), "items": items}

    def _valorizar_lifo(self, db, stocks) -> dict:
        total = 0.0
        items = []
        for sd in stocks:
            entradas = db.query(MovimientoStock).filter(MovimientoStock.producto_id == sd.producto_id, MovimientoStock.deposito_id == sd.deposito_id, MovimientoStock.tipo == "entrada").order_by(MovimientoStock.fecha.desc()).all()
            valor = self._calcular_valor_por_capas(entradas, sd.cantidad, sd.producto)
            total += valor
            items.append({"codigo": sd.producto.codigo, "nombre": sd.producto.nombre, "cantidad": sd.cantidad, "valor": valor, "costo_unitario": round(valor / sd.cantidad, 2) if sd.cantidad else 0})
        return {"metodo": "LIFO", "total": round(total, 2), "items": items}

    def _calcular_valor_por_capas(self, entradas, cantidad_stock: int, producto) -> float:
        restante = cantidad_stock
        valor = 0.0
        for mov in entradas:
            if restante <= 0:
                break
            precio = producto.precio_costo or 0
            usar = min(restante, mov.cantidad)
            valor += usar * precio
            restante -= usar
        if restante > 0:
            valor += restante * (producto.precio_costo or 0)
        return round(valor, 2)
