"""Servicio de control de riesgo comercial: credito, margen, bloqueos."""
from datetime import date, timezone, datetime, timedelta
from sqlalchemy import func
from core.database import get_db
from models import sucursal, usuario, empleado, rol, permiso  # noqa
from models.datos import Cliente
from models.inventario import Producto
from models.comercial import FacturaVenta
from services.core.auth_service import auth_service


def _hoy() -> date:
    return datetime.now(timezone.utc).date()


class RiesgoVentaService:
    # === CONTROL DE CREDITO ===
    def validar_venta(self, cliente_id: int, monto_venta: float) -> dict:
        """
        Validacion integral antes de crear pedido/remito/factura.
        Retorna: puede_vender, motivo_bloqueo, requiere_autorizacion.
        """
        with get_db() as db:
            cliente = db.get(Cliente, cliente_id)
            if not cliente:
                return {"puede_vender": False, "motivo": "Cliente no encontrado", "requiere_autorizacion": False}

            bloqueos = []

            # 1. Cliente bloqueado manualmente
            if cliente.credito_bloqueado:
                bloqueos.append("Cliente con credito bloqueado")

            # 2. Excede limite de credito
            if cliente.limite_credito > 0:
                deuda = cliente.saldo or 0
                if (deuda + monto_venta) > cliente.limite_credito:
                    disponible = max(0, cliente.limite_credito - deuda)
                    bloqueos.append(f"Excede limite de credito (disponible: ${disponible:,.2f})")

            # 3. Facturas vencidas impagas
            facturas_vencidas = self._facturas_vencidas(db, cliente_id)
            if facturas_vencidas:
                total_vencido = sum(f.total for f in facturas_vencidas)
                bloqueos.append(f"{len(facturas_vencidas)} facturas vencidas (${total_vencido:,.2f})")

            if bloqueos:
                return {
                    "puede_vender": False,
                    "motivo": " | ".join(bloqueos),
                    "requiere_autorizacion": True,
                    "deuda_actual": cliente.saldo or 0,
                    "limite": cliente.limite_credito,
                    "facturas_vencidas": len(facturas_vencidas) if facturas_vencidas else 0,
                }

            return {"puede_vender": True, "motivo": "", "requiere_autorizacion": False}

    def _facturas_vencidas(self, db, cliente_id: int):
        """Facturas emitidas con fecha_vencimiento pasada y no cobradas."""
        return db.query(FacturaVenta).filter(
            FacturaVenta.cliente_id == cliente_id,
            FacturaVenta.estado == "emitida",
            FacturaVenta.fecha_vencimiento.isnot(None),
            FacturaVenta.fecha_vencimiento < _hoy(),
        ).all()

    def facturas_vencidas_cliente(self, cliente_id: int) -> list:
        """Lista publica de facturas vencidas de un cliente."""
        with get_db() as db:
            return self._facturas_vencidas(db, cliente_id)

    def autorizar_venta_bloqueada(self, cliente_id: int, monto: float, autorizador_id: int = None) -> bool:
        """Un supervisor autoriza la venta a pesar del bloqueo."""
        # Registrar la autorizacion (se podria vincular a audit_log)
        return True  # El flujo externo registra en audit

    # === MARGEN MINIMO ===
    def validar_margen(self, producto_id: int, precio_venta: float, margen_minimo_pct: float = 10.0) -> dict:
        """
        Verifica que el precio de venta respete el margen minimo sobre costo.
        margen_minimo_pct: porcentaje minimo de ganancia requerido (default 10%).
        """
        with get_db() as db:
            prod = db.get(Producto, producto_id)
            if not prod:
                return {"valido": False, "alerta": "Producto no encontrado"}

            costo = prod.precio_costo or 0
            if costo <= 0:
                return {"valido": True, "alerta": "", "margen_real": 100, "costo": 0, "precio_venta": precio_venta}

            margen_real = ((precio_venta - costo) / costo) * 100
            precio_minimo = round(costo * (1 + margen_minimo_pct / 100), 2)

            if precio_venta < costo:
                return {
                    "valido": False,
                    "alerta": f"VENTA BAJO COSTO: precio ${precio_venta:,.2f} < costo ${costo:,.2f}",
                    "margen_real": round(margen_real, 1),
                    "margen_minimo": margen_minimo_pct,
                    "costo": costo,
                    "precio_venta": precio_venta,
                    "precio_minimo": precio_minimo,
                }
            elif margen_real < margen_minimo_pct:
                return {
                    "valido": False,
                    "alerta": f"Margen insuficiente: {margen_real:.1f}% < minimo {margen_minimo_pct}%",
                    "margen_real": round(margen_real, 1),
                    "margen_minimo": margen_minimo_pct,
                    "costo": costo,
                    "precio_venta": precio_venta,
                    "precio_minimo": precio_minimo,
                }

            return {
                "valido": True,
                "alerta": "",
                "margen_real": round(margen_real, 1),
                "margen_minimo": margen_minimo_pct,
                "costo": costo,
                "precio_venta": precio_venta,
                "precio_minimo": precio_minimo,
            }

    def validar_descuento(self, producto_id: int, precio_original: float, descuento_pct: float, margen_minimo_pct: float = 10.0) -> dict:
        """Valida que un descuento no rompa el margen minimo."""
        precio_final = precio_original * (1 - descuento_pct / 100)
        resultado = self.validar_margen(producto_id, precio_final, margen_minimo_pct)
        resultado["descuento_aplicado"] = descuento_pct
        resultado["precio_original"] = precio_original
        resultado["precio_con_descuento"] = round(precio_final, 2)
        return resultado

    def descuento_maximo_permitido(self, producto_id: int, precio_original: float, margen_minimo_pct: float = 10.0) -> float:
        """Calcula el descuento maximo que se puede aplicar sin romper el margen."""
        with get_db() as db:
            prod = db.get(Producto, producto_id)
            if not prod or not prod.precio_costo or prod.precio_costo <= 0:
                return 100.0  # sin costo, cualquier descuento es valido
            precio_minimo = prod.precio_costo * (1 + margen_minimo_pct / 100)
            if precio_original <= 0:
                return 0.0
            max_desc = ((precio_original - precio_minimo) / precio_original) * 100
            return round(max(0, max_desc), 2)

    # === RESUMEN DE RIESGO ===
    def resumen_riesgo(self) -> dict:
        """Dashboard de riesgo comercial."""
        with get_db() as db:
            total_clientes = db.query(Cliente).filter(Cliente.activo.is_(True)).count()
            bloqueados = db.query(Cliente).filter(Cliente.activo.is_(True), Cliente.credito_bloqueado.is_(True)).count()
            con_deuda = db.query(Cliente).filter(Cliente.activo.is_(True), Cliente.saldo > 0).count()

            # Total deuda
            total_deuda = db.query(func.sum(Cliente.saldo)).filter(
                Cliente.activo.is_(True), Cliente.saldo > 0
            ).scalar() or 0

            # Facturas vencidas totales
            fact_vencidas = db.query(FacturaVenta).filter(
                FacturaVenta.estado == "emitida",
                FacturaVenta.fecha_vencimiento.isnot(None),
                FacturaVenta.fecha_vencimiento < _hoy(),
            ).count()

            return {
                "total_clientes": total_clientes,
                "bloqueados": bloqueados,
                "con_deuda": con_deuda,
                "total_deuda": float(total_deuda),
                "facturas_vencidas": fact_vencidas,
            }


riesgo_venta_service = RiesgoVentaService()
