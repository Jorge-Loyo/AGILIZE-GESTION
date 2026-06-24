"""Servicio de reportes y BI: KPIs y datos consolidados."""
from datetime import date, timedelta
from sqlalchemy import func
from core.database import get_db
from models.finanzas import Factura, MovimientoCaja, MovimientoBanco, CuentaBancaria
from models.comercial import Presupuesto, PedidoVenta, OrdenCompra
from models.datos import Cliente, Proveedor
from models.cuentas import MovimientoCuenta
from models.inventario import Producto, StockDeposito, MovimientoStock


class ReportesService:
    def kpis_generales(self) -> dict:
        with get_db() as db:
            hoy = date.today()
            mes_actual = hoy.strftime("%Y-%m")
            inicio_mes = hoy.replace(day=1)

            # Ventas del mes
            ventas_mes = db.query(func.sum(Factura.total)).filter(
                Factura.tipo_comprobante == "factura",
                Factura.tipo_entidad == "cliente",
                Factura.fecha >= inicio_mes,
                Factura.estado != "anulada",
            ).scalar() or 0

            # Compras del mes
            compras_mes = db.query(func.sum(OrdenCompra.total)).filter(
                OrdenCompra.fecha >= inicio_mes,
                OrdenCompra.estado != "cancelada",
            ).scalar() or 0

            # Presupuestos pendientes
            presupuestos_pend = db.query(Presupuesto).filter(
                Presupuesto.estado == "pendiente"
            ).count()

            # Pedidos pendientes
            pedidos_pend = db.query(PedidoVenta).filter(
                PedidoVenta.estado == "pendiente"
            ).count()

            # Total clientes
            total_clientes = db.query(Cliente).filter(Cliente.activo == True).count()

            # Total proveedores
            total_proveedores = db.query(Proveedor).filter(Proveedor.activo == True).count()

            # Productos activos
            total_productos = db.query(Producto).filter(Producto.activo == True).count()

            # Valor inventario
            valor_inventario = db.query(
                func.sum(StockDeposito.cantidad * Producto.precio_costo)
            ).join(Producto).scalar() or 0

            # Saldo bancos
            saldo_bancos = db.query(func.sum(CuentaBancaria.saldo)).filter(
                CuentaBancaria.activo == True
            ).scalar() or 0

            # Por cobrar
            por_cobrar = db.query(func.sum(MovimientoCuenta.monto)).filter(
                MovimientoCuenta.tipo_entidad == "cliente",
                MovimientoCuenta.tipo == "debe"
            ).scalar() or 0
            cobrado = db.query(func.sum(MovimientoCuenta.monto)).filter(
                MovimientoCuenta.tipo_entidad == "cliente",
                MovimientoCuenta.tipo == "haber"
            ).scalar() or 0

            # Por pagar
            por_pagar = db.query(func.sum(MovimientoCuenta.monto)).filter(
                MovimientoCuenta.tipo_entidad == "proveedor",
                MovimientoCuenta.tipo == "debe"
            ).scalar() or 0
            pagado = db.query(func.sum(MovimientoCuenta.monto)).filter(
                MovimientoCuenta.tipo_entidad == "proveedor",
                MovimientoCuenta.tipo == "haber"
            ).scalar() or 0

            return {
                "ventas_mes": float(ventas_mes),
                "compras_mes": float(compras_mes),
                "margen_mes": float(ventas_mes) - float(compras_mes),
                "presupuestos_pendientes": presupuestos_pend,
                "pedidos_pendientes": pedidos_pend,
                "total_clientes": total_clientes,
                "total_proveedores": total_proveedores,
                "total_productos": total_productos,
                "valor_inventario": float(valor_inventario),
                "saldo_bancos": float(saldo_bancos),
                "por_cobrar": float(por_cobrar) - float(cobrado),
                "por_pagar": float(por_pagar) - float(pagado),
            }

    def ventas_por_mes(self, meses: int = 6) -> list:
        """Retorna ventas totales por mes."""
        with get_db() as db:
            hoy = date.today()
            resultado = []
            for i in range(meses - 1, -1, -1):
                mes = (hoy.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
                fin_mes = (mes + timedelta(days=32)).replace(day=1)
                total = db.query(func.sum(Factura.total)).filter(
                    Factura.tipo_comprobante == "factura",
                    Factura.tipo_entidad == "cliente",
                    Factura.fecha >= mes,
                    Factura.fecha < fin_mes,
                    Factura.estado != "anulada",
                ).scalar() or 0
                resultado.append({"mes": mes.strftime("%b %Y"), "total": float(total)})
            return resultado

    def top_clientes(self, limite: int = 5) -> list:
        """Top clientes por facturacion."""
        with get_db() as db:
            resultados = db.query(
                Factura.entidad_nombre,
                func.sum(Factura.total).label("total")
            ).filter(
                Factura.tipo_comprobante == "factura",
                Factura.tipo_entidad == "cliente",
                Factura.estado != "anulada",
            ).group_by(Factura.entidad_nombre).order_by(
                func.sum(Factura.total).desc()
            ).limit(limite).all()
            return [{"nombre": r[0], "total": float(r[1])} for r in resultados]

    def productos_mas_vendidos(self, limite: int = 5) -> list:
        """Productos con mas movimientos de salida."""
        with get_db() as db:
            resultados = db.query(
                Producto.nombre,
                func.sum(MovimientoStock.cantidad).label("total")
            ).join(Producto).filter(
                MovimientoStock.tipo == "salida"
            ).group_by(Producto.nombre).order_by(
                func.sum(MovimientoStock.cantidad).desc()
            ).limit(limite).all()
            return [{"nombre": r[0], "cantidad": int(r[1])} for r in resultados]


reportes_service = ReportesService()
