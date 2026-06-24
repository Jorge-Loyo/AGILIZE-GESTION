"""Sub-servicio: Toma de inventario fisico."""
from services.inventario._base import *
from services.inventario._base import _hoy


class TomaService:
    def iniciar_toma_inventario(self, deposito_id: int, observaciones: str = "") -> TomaInventario:
        with get_db() as db:
            ultimo = db.query(func.max(TomaInventario.numero)).scalar() or 0
            toma = TomaInventario(numero=ultimo + 1, fecha=_hoy(), deposito_id=deposito_id, estado="contando", observaciones=observaciones[:500], usuario_id=auth_service.current_user.id if auth_service.current_user else None)
            db.add(toma)
            db.flush()
            stocks = db.query(StockDeposito).filter(StockDeposito.deposito_id == deposito_id).all()
            for sd in stocks:
                db.add(TomaInventarioDetalle(toma_id=toma.id, producto_id=sd.producto_id, stock_teorico=sd.cantidad))
            ids_con_stock = [sd.producto_id for sd in stocks]
            productos_sin_stock = db.query(Producto).filter(Producto.activo.is_(True), Producto.tipo_articulo == "fisico", ~Producto.id.in_(ids_con_stock) if ids_con_stock else True).all()
            for p in productos_sin_stock:
                db.add(TomaInventarioDetalle(toma_id=toma.id, producto_id=p.id, stock_teorico=0))
            return toma

    def listar_tomas(self, deposito_id: int = None, limite: int = 50):
        with get_db() as db:
            q = db.query(TomaInventario)
            if deposito_id:
                q = q.filter(TomaInventario.deposito_id == deposito_id)
            return q.order_by(TomaInventario.fecha.desc()).limit(limite).all()

    def obtener_toma_detalles(self, toma_id: int):
        with get_db() as db:
            detalles = db.query(TomaInventarioDetalle).filter(TomaInventarioDetalle.toma_id == toma_id).all()
            result = []
            for d in detalles:
                prod = db.get(Producto, d.producto_id)
                result.append({"id": d.id, "producto_id": d.producto_id, "codigo": prod.codigo if prod else "", "nombre": prod.nombre if prod else "", "stock_teorico": d.stock_teorico, "conteo_fisico": d.conteo_fisico, "diferencia": d.diferencia, "ajustado": d.ajustado})
            return result

    def registrar_conteo(self, detalle_id: int, conteo_fisico: int):
        with get_db() as db:
            d = db.get(TomaInventarioDetalle, detalle_id)
            if not d:
                return
            d.conteo_fisico = conteo_fisico
            d.diferencia = conteo_fisico - d.stock_teorico

    def aplicar_ajustes_toma(self, toma_id: int) -> dict:
        with get_db() as db:
            toma = db.get(TomaInventario, toma_id)
            if not toma:
                raise ValueError("Toma no encontrada")
            detalles = db.query(TomaInventarioDetalle).filter(TomaInventarioDetalle.toma_id == toma_id, TomaInventarioDetalle.conteo_fisico.isnot(None), TomaInventarioDetalle.ajustado.is_(False), TomaInventarioDetalle.diferencia != 0).all()
            ajustados = 0
            for d in detalles:
                sd = db.query(StockDeposito).filter(StockDeposito.producto_id == d.producto_id, StockDeposito.deposito_id == toma.deposito_id).first()
                if not sd:
                    sd = StockDeposito(producto_id=d.producto_id, deposito_id=toma.deposito_id, cantidad=0)
                    db.add(sd)
                    db.flush()
                sd.cantidad = d.conteo_fisico
                db.add(MovimientoStock(producto_id=d.producto_id, deposito_id=toma.deposito_id, tipo="ajuste", cantidad=d.diferencia, motivo=f"Toma inventario #{toma.numero}", referencia=f"toma_{toma.id}", fecha=_hoy(), usuario_id=auth_service.current_user.id if auth_service.current_user else None))
                d.ajustado = True
                ajustados += 1
            toma.estado = "ajustada"
            return {"ajustados": ajustados, "total_items": len(detalles)}

    def cerrar_toma(self, toma_id: int):
        with get_db() as db:
            toma = db.get(TomaInventario, toma_id)
            if toma:
                toma.estado = "cerrada"
