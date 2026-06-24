"""Servicio de ventas: presupuestos y pedidos."""
from datetime import date
from sqlalchemy import func
from core.database import get_db
from models.comercial import Presupuesto, PresupuestoDetalle, PedidoVenta, PedidoVentaDetalle
from services.core.auth_service import auth_service
from services.core.empresa_service import empresa_service


class VentasService:
    def _get_iva(self) -> float:
        pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
        return 16.0 if pais == "Venezuela" else 21.0

    # === PRESUPUESTOS ===
    def crear_presupuesto(self, cliente_nombre: str, items: list, cliente_id: int = None,
                          validez_dias: int = 15, observaciones: str = "") -> Presupuesto:
        with get_db() as db:
            ultimo = db.query(func.max(Presupuesto.numero)).scalar() or 0
            subtotal = sum(i["cantidad"] * i["precio_unitario"] for i in items)
            iva_pct = self._get_iva()
            impuesto = round(subtotal * iva_pct / 100, 2)

            pres = Presupuesto(
                numero=ultimo + 1, fecha=date.today(),
                cliente_id=cliente_id, cliente_nombre=cliente_nombre,
                validez_dias=validez_dias, subtotal=subtotal,
                impuesto=impuesto, total=subtotal + impuesto,
                observaciones=observaciones,
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(pres)
            db.flush()
            for item in items:
                db.add(PresupuestoDetalle(
                    presupuesto_id=pres.id, descripcion=item["descripcion"],
                    cantidad=item["cantidad"], precio_unitario=item["precio_unitario"],
                    subtotal=round(item["cantidad"] * item["precio_unitario"], 2),
                ))
            return pres

    def listar_presupuestos(self, limite: int = 100):
        with get_db() as db:
            return db.query(Presupuesto).order_by(Presupuesto.fecha.desc(), Presupuesto.id.desc()).limit(limite).all()

    def aprobar_presupuesto(self, presupuesto_id: int):
        with get_db() as db:
            p = db.get(Presupuesto, presupuesto_id)
            if p:
                p.estado = "aprobado"

    def rechazar_presupuesto(self, presupuesto_id: int):
        with get_db() as db:
            p = db.get(Presupuesto, presupuesto_id)
            if p:
                p.estado = "rechazado"

    # === PEDIDOS ===
    def crear_pedido(self, cliente_nombre: str, items: list, cliente_id: int = None,
                     presupuesto_id: int = None, observaciones: str = "") -> PedidoVenta:
        with get_db() as db:
            ultimo = db.query(func.max(PedidoVenta.numero)).scalar() or 0
            subtotal = sum(i["cantidad"] * i["precio_unitario"] for i in items)
            iva_pct = self._get_iva()
            impuesto = round(subtotal * iva_pct / 100, 2)

            pedido = PedidoVenta(
                numero=ultimo + 1, fecha=date.today(),
                cliente_id=cliente_id, cliente_nombre=cliente_nombre,
                presupuesto_id=presupuesto_id, subtotal=subtotal,
                impuesto=impuesto, total=subtotal + impuesto,
                observaciones=observaciones,
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(pedido)
            db.flush()
            for item in items:
                db.add(PedidoVentaDetalle(
                    pedido_id=pedido.id, descripcion=item["descripcion"],
                    cantidad=item["cantidad"], precio_unitario=item["precio_unitario"],
                    subtotal=round(item["cantidad"] * item["precio_unitario"], 2),
                ))
            return pedido

    def listar_pedidos(self, limite: int = 100):
        with get_db() as db:
            return db.query(PedidoVenta).order_by(PedidoVenta.fecha.desc(), PedidoVenta.id.desc()).limit(limite).all()

    def cambiar_estado_pedido(self, pedido_id: int, estado: str):
        with get_db() as db:
            p = db.get(PedidoVenta, pedido_id)
            if p:
                p.estado = estado


ventas_service = VentasService()
