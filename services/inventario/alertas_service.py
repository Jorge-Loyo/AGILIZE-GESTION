"""Sub-servicio: Alertas de stock y reposicion automatica."""
from services.inventario._base import *


class AlertasService:
    def obtener_stock_disponible(self, producto_id: int) -> dict:
        with get_db() as db:
            stock_real = db.query(func.sum(StockDeposito.cantidad)).filter(StockDeposito.producto_id == producto_id).scalar() or 0
            codigo = self._get_codigo_producto(db, producto_id)
            from models.comercial import PedidoVentaDetalle, PedidoVenta, OrdenCompraDetalle, OrdenCompra
            comprometido = db.query(func.sum(PedidoVentaDetalle.cantidad)).join(PedidoVenta).filter(
                PedidoVentaDetalle.descripcion.ilike(f"%{codigo}%"), PedidoVenta.estado.in_(["pendiente", "en_proceso"]),
            ).scalar() or 0
            en_camino = db.query(func.sum(OrdenCompraDetalle.cantidad)).join(OrdenCompra).filter(
                OrdenCompraDetalle.descripcion.ilike(f"%{codigo}%"), OrdenCompra.estado == "enviada",
            ).scalar() or 0
            en_transito = db.query(func.sum(MovimientoStock.cantidad)).filter(
                MovimientoStock.producto_id == producto_id, MovimientoStock.tipo == "transferencia_transito", MovimientoStock.referencia == "en_transito",
            ).scalar() or 0
            return {"stock_real": int(stock_real), "comprometido": int(comprometido), "en_camino": int(en_camino), "en_transito": int(en_transito), "disponible": int(stock_real) - int(comprometido) + int(en_camino)}

    def _get_codigo_producto(self, db, producto_id: int) -> str:
        p = db.get(Producto, producto_id)
        return p.codigo if p else ""

    def alertas_stock(self) -> list:
        alertas = []
        with get_db() as db:
            productos = db.query(Producto).filter(Producto.activo.is_(True), Producto.tipo_articulo == "fisico").all()
            for p in productos:
                stock = db.query(func.sum(StockDeposito.cantidad)).filter(StockDeposito.producto_id == p.id).scalar() or 0
                if p.punto_pedido and stock <= p.punto_pedido:
                    alertas.append({"producto_id": p.id, "codigo": p.codigo, "nombre": p.nombre, "stock_actual": int(stock), "punto_pedido": p.punto_pedido, "stock_minimo": p.stock_minimo, "stock_maximo": p.stock_maximo, "tipo_alerta": "punto_pedido", "cantidad_sugerida": (p.stock_maximo or p.stock_minimo * 2 or 10) - int(stock)})
                elif p.stock_minimo and stock < p.stock_minimo:
                    alertas.append({"producto_id": p.id, "codigo": p.codigo, "nombre": p.nombre, "stock_actual": int(stock), "punto_pedido": p.punto_pedido, "stock_minimo": p.stock_minimo, "stock_maximo": p.stock_maximo, "tipo_alerta": "bajo_minimo", "cantidad_sugerida": (p.stock_maximo or p.stock_minimo * 2) - int(stock)})
                elif p.stock_maximo and stock > p.stock_maximo:
                    alertas.append({"producto_id": p.id, "codigo": p.codigo, "nombre": p.nombre, "stock_actual": int(stock), "punto_pedido": p.punto_pedido, "stock_minimo": p.stock_minimo, "stock_maximo": p.stock_maximo, "tipo_alerta": "sobre_maximo", "cantidad_sugerida": 0})
        alertas.sort(key=lambda x: {"punto_pedido": 0, "bajo_minimo": 1, "sobre_maximo": 2}.get(x["tipo_alerta"], 9))
        return alertas

    def generar_reposicion_automatica(self) -> int:
        alertas = self.alertas_stock()
        items_reposicion = [a for a in alertas if a["tipo_alerta"] in ("punto_pedido", "bajo_minimo") and a["cantidad_sugerida"] > 0]
        if not items_reposicion:
            return 0
        from services.compras_service import compras_service
        items = [{"descripcion": f"{i['codigo']} - {i['nombre']}", "cantidad": i["cantidad_sugerida"]} for i in items_reposicion]
        compras_service.crear_requisicion("Sistema - Reposicion Automatica", items)
        return len(items)
