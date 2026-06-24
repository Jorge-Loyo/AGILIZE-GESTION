"""Servicio de reportes y analitica de ventas: ABC, comisiones, margen."""
from datetime import date, timezone, datetime, timedelta
from sqlalchemy import func, desc
from core.database import get_db
from models import sucursal, usuario, empleado, rol, permiso  # noqa
from models.datos import Cliente
from models.inventario import Producto, CategoriaProducto
from models.comercial import FacturaVenta, FacturaVentaDetalle, PedidoVenta


def _hoy() -> date:
    return datetime.now(timezone.utc).date()


class ReportesVentaService:
    # === RANKING ABC ===
    def ranking_productos(self, dias: int = 30, limite: int = 50) -> dict:
        """Ranking ABC de productos mas vendidos por monto facturado."""
        fecha_desde = _hoy() - timedelta(days=dias)
        with get_db() as db:
            datos = db.query(
                FacturaVentaDetalle.descripcion,
                func.sum(FacturaVentaDetalle.cantidad).label("cantidad_total"),
                func.sum(FacturaVentaDetalle.subtotal).label("monto_total"),
            ).join(FacturaVenta).filter(
                FacturaVenta.fecha >= fecha_desde,
                FacturaVenta.estado != "anulada",
            ).group_by(FacturaVentaDetalle.descripcion).order_by(desc("monto_total")).limit(limite).all()

            total_ventas = sum(d.monto_total for d in datos) if datos else 0
            items = []
            acumulado = 0
            for d in datos:
                acumulado += d.monto_total
                pct = (d.monto_total / total_ventas * 100) if total_ventas else 0
                pct_acum = (acumulado / total_ventas * 100) if total_ventas else 0
                # Clasificacion ABC
                if pct_acum <= 80:
                    clase = "A"
                elif pct_acum <= 95:
                    clase = "B"
                else:
                    clase = "C"
                items.append({
                    "descripcion": d.descripcion,
                    "cantidad": float(d.cantidad_total),
                    "monto": float(d.monto_total),
                    "porcentaje": round(pct, 1),
                    "porcentaje_acumulado": round(pct_acum, 1),
                    "clase": clase,
                })
            return {"periodo_dias": dias, "total_ventas": total_ventas, "items": items}

    def ranking_clientes(self, dias: int = 30, limite: int = 50) -> dict:
        """Ranking ABC de clientes por monto facturado."""
        fecha_desde = _hoy() - timedelta(days=dias)
        with get_db() as db:
            datos = db.query(
                FacturaVenta.cliente_nombre,
                FacturaVenta.cliente_id,
                func.count(FacturaVenta.id).label("cant_facturas"),
                func.sum(FacturaVenta.total).label("monto_total"),
            ).filter(
                FacturaVenta.fecha >= fecha_desde,
                FacturaVenta.estado != "anulada",
            ).group_by(FacturaVenta.cliente_nombre, FacturaVenta.cliente_id).order_by(desc("monto_total")).limit(limite).all()

            total = sum(d.monto_total for d in datos) if datos else 0
            items = []
            acumulado = 0
            for d in datos:
                acumulado += d.monto_total
                pct_acum = (acumulado / total * 100) if total else 0
                clase = "A" if pct_acum <= 80 else ("B" if pct_acum <= 95 else "C")
                items.append({
                    "cliente": d.cliente_nombre,
                    "cliente_id": d.cliente_id,
                    "facturas": d.cant_facturas,
                    "monto": float(d.monto_total),
                    "porcentaje": round((d.monto_total / total * 100) if total else 0, 1),
                    "clase": clase,
                })
            return {"periodo_dias": dias, "total": total, "items": items}

    def ranking_vendedores(self, dias: int = 30) -> list:
        """Ranking de vendedores por monto facturado."""
        fecha_desde = _hoy() - timedelta(days=dias)
        with get_db() as db:
            from models.usuario import Usuario
            datos = db.query(
                FacturaVenta.usuario_id,
                func.count(FacturaVenta.id).label("cant_facturas"),
                func.sum(FacturaVenta.total).label("monto_total"),
            ).filter(
                FacturaVenta.fecha >= fecha_desde,
                FacturaVenta.estado != "anulada",
                FacturaVenta.usuario_id.isnot(None),
            ).group_by(FacturaVenta.usuario_id).order_by(desc("monto_total")).all()

            result = []
            for d in datos:
                u = db.get(Usuario, d.usuario_id)
                result.append({
                    "vendedor_id": d.usuario_id,
                    "vendedor": u.nombre_completo if u else "",
                    "facturas": d.cant_facturas,
                    "monto": float(d.monto_total),
                })
            return result

    # === COMISIONES ===
    def calcular_comisiones(self, dias: int = 30, porcentaje_comision: float = 5.0, base: str = "facturado") -> list:
        """
        Calcula comisiones por vendedor.
        base: 'facturado' (sobre emitido) o 'cobrado' (solo facturas cobradas).
        """
        fecha_desde = _hoy() - timedelta(days=dias)
        with get_db() as db:
            from models.usuario import Usuario
            filtro_estado = FacturaVenta.estado != "anulada"
            if base == "cobrado":
                filtro_estado = FacturaVenta.estado == "cobrada"

            datos = db.query(
                FacturaVenta.usuario_id,
                func.sum(FacturaVenta.total).label("monto_base"),
            ).filter(
                FacturaVenta.fecha >= fecha_desde,
                filtro_estado,
                FacturaVenta.usuario_id.isnot(None),
            ).group_by(FacturaVenta.usuario_id).all()

            result = []
            for d in datos:
                u = db.get(Usuario, d.usuario_id)
                monto = float(d.monto_base or 0)
                comision = round(monto * porcentaje_comision / 100, 2)
                result.append({
                    "vendedor_id": d.usuario_id,
                    "vendedor": u.nombre_completo if u else "",
                    "monto_base": monto,
                    "porcentaje": porcentaje_comision,
                    "comision": comision,
                    "base_calculo": base,
                })
            result.sort(key=lambda x: x["comision"], reverse=True)
            return result

    # === MARGEN DE CONTRIBUCION ===
    def margen_contribucion(self, dias: int = 30) -> dict:
        """Calcula rentabilidad real: Precio Venta - Costo."""
        fecha_desde = _hoy() - timedelta(days=dias)
        with get_db() as db:
            facturas = db.query(FacturaVenta).filter(
                FacturaVenta.fecha >= fecha_desde,
                FacturaVenta.estado != "anulada",
            ).all()

            items = []
            total_venta = 0.0
            total_costo = 0.0

            for f in facturas:
                detalles = db.query(FacturaVentaDetalle).filter(FacturaVentaDetalle.factura_id == f.id).all()
                for det in detalles:
                    # Intentar encontrar costo del producto
                    costo_unit = self._obtener_costo(db, det.descripcion)
                    venta = det.subtotal
                    costo = costo_unit * det.cantidad
                    margen = venta - costo
                    total_venta += venta
                    total_costo += costo
                    items.append({
                        "descripcion": det.descripcion,
                        "cantidad": det.cantidad,
                        "precio_venta": det.precio_unitario,
                        "costo_unitario": costo_unit,
                        "venta_total": venta,
                        "costo_total": costo,
                        "margen": margen,
                        "margen_pct": round((margen / venta * 100) if venta else 0, 1),
                    })

            # Agrupar por producto
            agrupado = {}
            for item in items:
                key = item["descripcion"]
                if key not in agrupado:
                    agrupado[key] = {"descripcion": key, "cantidad": 0, "venta": 0, "costo": 0, "margen": 0}
                agrupado[key]["cantidad"] += item["cantidad"]
                agrupado[key]["venta"] += item["venta_total"]
                agrupado[key]["costo"] += item["costo_total"]
                agrupado[key]["margen"] += item["margen"]

            ranking = sorted(agrupado.values(), key=lambda x: x["margen"], reverse=True)
            for r in ranking:
                r["margen_pct"] = round((r["margen"] / r["venta"] * 100) if r["venta"] else 0, 1)

            margen_global = total_venta - total_costo
            return {
                "periodo_dias": dias,
                "total_venta": round(total_venta, 2),
                "total_costo": round(total_costo, 2),
                "margen_total": round(margen_global, 2),
                "margen_pct": round((margen_global / total_venta * 100) if total_venta else 0, 1),
                "por_producto": ranking,
            }

    def margen_por_cliente(self, dias: int = 30) -> list:
        """Margen de contribucion agrupado por cliente."""
        fecha_desde = _hoy() - timedelta(days=dias)
        with get_db() as db:
            facturas = db.query(FacturaVenta).filter(
                FacturaVenta.fecha >= fecha_desde,
                FacturaVenta.estado != "anulada",
            ).all()

            por_cliente = {}
            for f in facturas:
                key = f.cliente_nombre or "(Sin cliente)"
                if key not in por_cliente:
                    por_cliente[key] = {"cliente": key, "venta": 0, "costo": 0}
                detalles = db.query(FacturaVentaDetalle).filter(FacturaVentaDetalle.factura_id == f.id).all()
                for det in detalles:
                    costo_unit = self._obtener_costo(db, det.descripcion)
                    por_cliente[key]["venta"] += det.subtotal
                    por_cliente[key]["costo"] += costo_unit * det.cantidad

            result = []
            for data in por_cliente.values():
                margen = data["venta"] - data["costo"]
                result.append({
                    "cliente": data["cliente"],
                    "venta": round(data["venta"], 2),
                    "costo": round(data["costo"], 2),
                    "margen": round(margen, 2),
                    "margen_pct": round((margen / data["venta"] * 100) if data["venta"] else 0, 1),
                })
            result.sort(key=lambda x: x["margen"], reverse=True)
            return result

    def _obtener_costo(self, db, descripcion: str) -> float:
        """Intenta obtener costo del producto por su descripcion/codigo."""
        codigo = descripcion.split(" - ")[0].strip() if " - " in descripcion else descripcion.split()[0] if descripcion else ""
        prod = db.query(Producto).filter(Producto.codigo == codigo).first()
        return prod.precio_costo if prod and prod.precio_costo else 0


reportes_venta_service = ReportesVentaService()
