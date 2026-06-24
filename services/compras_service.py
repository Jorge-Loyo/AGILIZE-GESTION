"""Servicio de compras: ordenes de compra."""
from datetime import date
from sqlalchemy import func
from core.database import get_db
from models.comercial import OrdenCompra, OrdenCompraDetalle
from services.auth_service import auth_service
from services.empresa_service import empresa_service


class ComprasService:
    def _get_iva(self) -> float:
        pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
        return 16.0 if pais == "Venezuela" else 21.0

    def crear_orden(self, proveedor_nombre: str, items: list, proveedor_id: int = None,
                    observaciones: str = "") -> OrdenCompra:
        with get_db() as db:
            ultimo = db.query(func.max(OrdenCompra.numero)).scalar() or 0
            subtotal = sum(i["cantidad"] * i["precio_unitario"] for i in items)
            iva_pct = self._get_iva()
            impuesto = round(subtotal * iva_pct / 100, 2)

            orden = OrdenCompra(
                numero=ultimo + 1, fecha=date.today(),
                proveedor_id=proveedor_id, proveedor_nombre=proveedor_nombre,
                subtotal=subtotal, impuesto=impuesto, total=subtotal + impuesto,
                observaciones=observaciones,
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(orden)
            db.flush()
            for item in items:
                db.add(OrdenCompraDetalle(
                    orden_id=orden.id, descripcion=item["descripcion"],
                    cantidad=item["cantidad"], precio_unitario=item["precio_unitario"],
                    subtotal=round(item["cantidad"] * item["precio_unitario"], 2),
                ))
            return orden

    def listar_ordenes(self, limite: int = 100):
        with get_db() as db:
            return db.query(OrdenCompra).order_by(OrdenCompra.fecha.desc(), OrdenCompra.id.desc()).limit(limite).all()

    def cambiar_estado(self, orden_id: int, estado: str):
        with get_db() as db:
            o = db.get(OrdenCompra, orden_id)
            if o:
                o.estado = estado


compras_service = ComprasService()
