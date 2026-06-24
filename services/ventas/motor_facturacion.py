"""Motor de facturacion unificado.
Backend compartido para POS (mostrador) y Facturacion Central (B2B).
Genera facturas, descuenta stock, registra en cuenta corriente y caja.
"""
from datetime import date, timezone, datetime
from sqlalchemy import func
from core.database import get_db
from models import sucursal, usuario, empleado, rol, permiso  # noqa
from models.comercial import FacturaVenta, FacturaVentaDetalle, RemitoSalida, PedidoVenta
from models.datos import Cliente
from models.inventario import Producto, StockDeposito
from services.core.auth_service import auth_service
from services.core.empresa_service import empresa_service


def _hoy() -> date:
    return datetime.now(timezone.utc).date()


def _usuario_id():
    return auth_service.current_user.id if auth_service.current_user else None


class MotorFacturacion:
    """Motor unificado de facturacion. Usado por POS y Facturacion Central."""

    def _get_iva(self) -> float:
        pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
        return 16.0 if pais == "Venezuela" else 21.0

    def _siguiente_numero(self, db, tipo_comprobante: str = "A", punto_venta: str = "0001") -> str:
        """Genera siguiente numero de factura: A-0001-00000001"""
        ultimo = db.query(FacturaVenta).filter(
            FacturaVenta.tipo_comprobante == tipo_comprobante,
            FacturaVenta.numero.ilike(f"{tipo_comprobante}-{punto_venta}-%"),
        ).order_by(FacturaVenta.id.desc()).first()
        if ultimo:
            partes = ultimo.numero.split("-")
            num = int(partes[-1]) + 1 if len(partes) == 3 else 1
        else:
            num = 1
        return f"{tipo_comprobante}-{punto_venta}-{num:08d}"

    # === FACTURACION POS (rapida) ===
    def facturar_pos(self, items: list, medio_pago: str = "efectivo",
                     monto_recibido: float = 0, cliente_id: int = None,
                     punto_venta: str = "0001", deposito_ids: dict = None) -> dict:
        """
        Facturacion rapida para POS/mostrador.
        items: [{"codigo": "X", "nombre": "Y", "cantidad": 1, "precio": 10, "deposito_id": 1}]
        Retorna: {"factura_numero", "total", "vuelto", "exito"}
        """
        if not items:
            raise ValueError("No hay items para facturar")

        iva_pct = self._get_iva()
        subtotal = sum(i["cantidad"] * i["precio"] for i in items)
        iva = round(subtotal * iva_pct / 100, 2)
        total = subtotal + iva
        vuelto = max(0, monto_recibido - total) if monto_recibido > 0 else 0

        # Tipo comprobante: B si consumidor final (AR), o sin letra (VE)
        pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
        tipo = "B" if (pais == "Argentina" and not cliente_id) else "A"

        with get_db() as db:
            numero = self._siguiente_numero(db, tipo, punto_venta)

            # Datos cliente
            cliente_nombre = "Consumidor Final"
            cliente_cuit = ""
            if cliente_id:
                cli = db.get(Cliente, cliente_id)
                if cli:
                    cliente_nombre = cli.razon_social
                    cliente_cuit = cli.cuit_rif

            factura = FacturaVenta(
                numero=numero,
                tipo_comprobante=tipo,
                fecha=_hoy(),
                fecha_vencimiento=_hoy(),
                cliente_id=cliente_id,
                cliente_nombre=cliente_nombre,
                cliente_cuit=cliente_cuit,
                condicion_pago=medio_pago,
                subtotal=subtotal,
                subtotal_neto=subtotal,
                iva_porcentaje=iva_pct,
                iva_monto=iva,
                total=total,
                estado="cobrada" if medio_pago == "efectivo" else "emitida",
                usuario_id=_usuario_id(),
            )
            db.add(factura)
            db.flush()

            for item in items:
                db.add(FacturaVentaDetalle(
                    factura_id=factura.id,
                    descripcion=f"{item['codigo']} - {item['nombre']}" if item.get('codigo') else item['nombre'],
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio"],
                    subtotal=round(item["cantidad"] * item["precio"], 2),
                ))

            # Descontar stock
            for item in items:
                dep_id = item.get("deposito_id")
                if dep_id:
                    self._descontar_stock(db, item.get("codigo", ""), dep_id, item["cantidad"])

            # Registrar en cuenta corriente si es a credito
            if cliente_id and medio_pago != "efectivo":
                cli = db.get(Cliente, cliente_id)
                if cli:
                    cli.saldo = (cli.saldo or 0) + total

        return {
            "factura_numero": numero,
            "total": total,
            "vuelto": round(vuelto, 2),
            "medio_pago": medio_pago,
            "exito": True,
        }

    # === FACTURACION CENTRAL (B2B) ===
    def facturar_central(self, cliente_id: int, items: list,
                         tipo_comprobante: str = "A", condicion_pago: str = "contado",
                         dias_pago: int = 0, descuento_pct: float = 0,
                         pedido_id: int = None, remito_id: int = None,
                         punto_venta: str = "0001", observaciones: str = "") -> dict:
        """
        Facturacion administrativa/B2B con todas las opciones.
        """
        if not items:
            raise ValueError("No hay items para facturar")
        if not cliente_id:
            raise ValueError("Debe seleccionar un cliente")

        iva_pct = self._get_iva()
        subtotal_bruto = sum(i["cantidad"] * i["precio"] for i in items)
        descuento_monto = round(subtotal_bruto * descuento_pct / 100, 2)
        subtotal_neto = subtotal_bruto - descuento_monto
        iva = round(subtotal_neto * iva_pct / 100, 2)
        total = subtotal_neto + iva

        with get_db() as db:
            # Validar cliente
            cli = db.get(Cliente, cliente_id)
            if not cli:
                raise ValueError("Cliente no encontrado")

            # Validar credito
            if cli.credito_bloqueado:
                raise ValueError(f"Cliente '{cli.razon_social}' tiene credito bloqueado")
            if cli.limite_credito > 0 and ((cli.saldo or 0) + total) > cli.limite_credito:
                raise ValueError(f"Excede limite de credito. Disponible: ${max(0, cli.limite_credito - (cli.saldo or 0)):,.2f}")

            numero = self._siguiente_numero(db, tipo_comprobante, punto_venta)

            from datetime import timedelta
            fecha_vto = _hoy() + timedelta(days=dias_pago) if dias_pago > 0 else _hoy()

            factura = FacturaVenta(
                numero=numero,
                tipo_comprobante=tipo_comprobante,
                fecha=_hoy(),
                fecha_vencimiento=fecha_vto,
                cliente_id=cliente_id,
                cliente_nombre=cli.razon_social,
                cliente_cuit=cli.cuit_rif or "",
                pedido_id=pedido_id,
                remito_id=remito_id,
                condicion_pago=condicion_pago,
                subtotal=subtotal_bruto,
                descuento=descuento_monto,
                subtotal_neto=subtotal_neto,
                iva_porcentaje=iva_pct,
                iva_monto=iva,
                total=total,
                estado="emitida",
                observaciones=observaciones[:500],
                usuario_id=_usuario_id(),
            )
            db.add(factura)
            db.flush()

            for item in items:
                db.add(FacturaVentaDetalle(
                    factura_id=factura.id,
                    descripcion=item.get("descripcion", item.get("nombre", "")),
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio"],
                    descuento=item.get("descuento", 0),
                    subtotal=round(item["cantidad"] * item["precio"], 2),
                ))

            # Cargar a cuenta corriente
            if condicion_pago != "contado":
                cli.saldo = (cli.saldo or 0) + total

            # Marcar pedido como facturado
            if pedido_id:
                pedido = db.get(PedidoVenta, pedido_id)
                if pedido:
                    pedido.estado = "facturado"

        return {
            "factura_numero": numero,
            "total": total,
            "descuento": descuento_monto,
            "condicion_pago": condicion_pago,
            "vencimiento": fecha_vto.strftime("%d/%m/%Y"),
            "exito": True,
        }

    # === IMPORTAR DOCUMENTOS PREVIOS ===
    def items_desde_pedido(self, pedido_id: int) -> list:
        """Obtiene items de un pedido para importar a factura."""
        with get_db() as db:
            from models.comercial import PedidoVentaDetalle
            detalles = db.query(PedidoVentaDetalle).filter(PedidoVentaDetalle.pedido_id == pedido_id).all()
            return [{"descripcion": d.descripcion, "cantidad": d.cantidad, "precio": d.precio_unitario} for d in detalles]

    def items_desde_remito(self, remito_id: int) -> list:
        """Obtiene items de un remito para importar a factura."""
        with get_db() as db:
            from models.comercial import RemitoSalidaDetalle
            detalles = db.query(RemitoSalidaDetalle).filter(RemitoSalidaDetalle.remito_id == remito_id).all()
            return [{"descripcion": d.descripcion, "cantidad": d.cantidad, "precio": d.precio_unitario} for d in detalles]

    def pedidos_pendientes_cliente(self, cliente_id: int) -> list:
        """Lista pedidos del cliente que no han sido facturados."""
        with get_db() as db:
            return db.query(PedidoVenta).filter(
                PedidoVenta.cliente_id == cliente_id,
                PedidoVenta.estado.in_(["pendiente", "en_proceso", "despachado"]),
            ).order_by(PedidoVenta.fecha.desc()).all()

    def remitos_pendientes_cliente(self, cliente_id: int) -> list:
        """Lista remitos del cliente que no han sido facturados."""
        with get_db() as db:
            # Remitos que no tienen factura vinculada
            facturados = db.query(FacturaVenta.remito_id).filter(FacturaVenta.remito_id.isnot(None)).subquery()
            return db.query(RemitoSalida).filter(
                RemitoSalida.cliente_id == cliente_id,
                RemitoSalida.estado == "entregado",
                ~RemitoSalida.id.in_(facturados),
            ).order_by(RemitoSalida.fecha.desc()).all()

    # === UTILIDADES ===
    def _descontar_stock(self, db, codigo: str, deposito_id: int, cantidad: int):
        """Descuenta stock del deposito."""
        prod = db.query(Producto).filter(Producto.codigo == codigo).first()
        if not prod:
            return
        sd = db.query(StockDeposito).filter(
            StockDeposito.producto_id == prod.id,
            StockDeposito.deposito_id == deposito_id,
        ).first()
        if sd and sd.cantidad >= cantidad:
            sd.cantidad -= cantidad

    def listar_facturas_venta(self, cliente_id: int = None, limite: int = 100):
        with get_db() as db:
            q = db.query(FacturaVenta)
            if cliente_id:
                q = q.filter(FacturaVenta.cliente_id == cliente_id)
            return q.order_by(FacturaVenta.fecha.desc(), FacturaVenta.id.desc()).limit(limite).all()


motor_facturacion = MotorFacturacion()
