"""Servicio financiero: contabilidad, facturacion, bancos y caja."""
from datetime import date
from sqlalchemy import func
from core.database import get_db
from models.finanzas import (
    CuentaContable, Asiento, AsientoDetalle,
    Factura, FacturaDetalle,
    CuentaBancaria, MovimientoBanco,
    Caja, MovimientoCaja,
)
from services.auth_service import auth_service


class FinanzasService:
    # === PLAN DE CUENTAS ===
    def listar_cuentas(self):
        with get_db() as db:
            return db.query(CuentaContable).filter(
                CuentaContable.activo == True
            ).order_by(CuentaContable.codigo).all()

    def crear_cuenta(self, codigo: str, nombre: str, tipo: str, padre_id: int = None, es_grupo: bool = False):
        with get_db() as db:
            cuenta = CuentaContable(codigo=codigo, nombre=nombre, tipo=tipo, padre_id=padre_id, es_grupo=es_grupo)
            db.add(cuenta)
            db.flush()
            return cuenta

    def seed_plan_cuentas(self):
        """Crea plan de cuentas basico si no existe."""
        with get_db() as db:
            if db.query(CuentaContable).first():
                return
            cuentas = [
                ("1", "ACTIVO", "activo", None, True),
                ("1.1", "Activo Corriente", "activo", "1", True),
                ("1.1.01", "Caja", "activo", "1.1", False),
                ("1.1.02", "Bancos", "activo", "1.1", False),
                ("1.1.03", "Cuentas por Cobrar", "activo", "1.1", False),
                ("1.1.04", "Inventario", "activo", "1.1", False),
                ("2", "PASIVO", "pasivo", None, True),
                ("2.1", "Pasivo Corriente", "pasivo", "2", True),
                ("2.1.01", "Cuentas por Pagar", "pasivo", "2.1", False),
                ("2.1.02", "Impuestos por Pagar", "pasivo", "2.1", False),
                ("3", "PATRIMONIO", "patrimonio", None, True),
                ("3.1", "Capital", "patrimonio", "3", False),
                ("3.2", "Resultados Acumulados", "patrimonio", "3", False),
                ("4", "INGRESOS", "ingreso", None, True),
                ("4.1", "Ventas", "ingreso", "4", False),
                ("4.2", "Otros Ingresos", "ingreso", "4", False),
                ("5", "EGRESOS", "egreso", None, True),
                ("5.1", "Costo de Ventas", "egreso", "5", False),
                ("5.2", "Gastos Operativos", "egreso", "5", False),
                ("5.3", "Gastos Administrativos", "egreso", "5", False),
            ]
            id_map = {}
            for codigo, nombre, tipo, padre_cod, es_grupo in cuentas:
                padre_id = id_map.get(padre_cod)
                c = CuentaContable(codigo=codigo, nombre=nombre, tipo=tipo, padre_id=padre_id, es_grupo=es_grupo)
                db.add(c)
                db.flush()
                id_map[codigo] = c.id

    # === ASIENTOS ===
    def crear_asiento(self, fecha: date, concepto: str, detalles: list, tipo: str = "manual", referencia: str = ""):
        """detalles: [{"cuenta_id": int, "debe": float, "haber": float, "descripcion": str}]"""
        total_debe = sum(d.get("debe", 0) for d in detalles)
        total_haber = sum(d.get("haber", 0) for d in detalles)
        if abs(total_debe - total_haber) > 0.01:
            raise ValueError(f"Asiento descuadrado: Debe={total_debe:.2f} Haber={total_haber:.2f}")
        with get_db() as db:
            ultimo = db.query(func.max(Asiento.numero)).scalar() or 0
            asiento = Asiento(
                numero=ultimo + 1, fecha=fecha, concepto=concepto,
                tipo=tipo, referencia=referencia,
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(asiento)
            db.flush()
            for d in detalles:
                detalle = AsientoDetalle(
                    asiento_id=asiento.id, cuenta_id=d["cuenta_id"],
                    debe=d.get("debe", 0), haber=d.get("haber", 0),
                    descripcion=d.get("descripcion", ""),
                )
                db.add(detalle)
            return asiento

    def listar_asientos(self, limite: int = 100):
        with get_db() as db:
            return db.query(Asiento).filter(Asiento.anulado == False).order_by(Asiento.fecha.desc(), Asiento.numero.desc()).limit(limite).all()

    def anular_asiento(self, asiento_id: int):
        with get_db() as db:
            asiento = db.get(Asiento, asiento_id)
            if asiento:
                asiento.anulado = True

    # === FACTURACION ===
    def crear_factura(self, datos: dict, items: list) -> Factura:
        """datos: {tipo_comprobante, letra, fecha, tipo_entidad, entidad_id, ...}
           items: [{"descripcion", "cantidad", "precio_unitario"}]"""
        with get_db() as db:
            # Calcular proximo numero
            ultimo = db.query(func.max(Factura.numero)).filter(
                Factura.tipo_comprobante == datos.get("tipo_comprobante"),
                Factura.letra == datos.get("letra", ""),
                Factura.punto_venta == datos.get("punto_venta", 1),
            ).scalar() or 0

            subtotal = sum(i["cantidad"] * i["precio_unitario"] for i in items)
            imp_pct = datos.get("impuesto_porcentaje", 0)
            imp_monto = round(subtotal * imp_pct / 100, 2)
            total = subtotal + imp_monto

            factura = Factura(
                tipo_comprobante=datos["tipo_comprobante"],
                letra=datos.get("letra", ""),
                punto_venta=datos.get("punto_venta", 1),
                numero=ultimo + 1,
                fecha=datos.get("fecha", date.today()),
                tipo_entidad=datos.get("tipo_entidad", "cliente"),
                entidad_id=datos.get("entidad_id", 0),
                entidad_nombre=datos.get("entidad_nombre", ""),
                entidad_documento=datos.get("entidad_documento", ""),
                subtotal=subtotal,
                impuesto_porcentaje=imp_pct,
                impuesto_monto=imp_monto,
                total=total,
                moneda=datos.get("moneda", ""),
                observaciones=datos.get("observaciones", ""),
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(factura)
            db.flush()

            for item in items:
                det = FacturaDetalle(
                    factura_id=factura.id,
                    descripcion=item["descripcion"],
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio_unitario"],
                    subtotal=round(item["cantidad"] * item["precio_unitario"], 2),
                )
                db.add(det)

            return factura

    def listar_facturas(self, tipo_entidad: str = None, limite: int = 100):
        with get_db() as db:
            q = db.query(Factura)
            if tipo_entidad:
                q = q.filter(Factura.tipo_entidad == tipo_entidad)
            return q.order_by(Factura.fecha.desc(), Factura.id.desc()).limit(limite).all()

    # === BANCOS ===
    def listar_cuentas_bancarias(self):
        with get_db() as db:
            return db.query(CuentaBancaria).filter(CuentaBancaria.activo == True).order_by(CuentaBancaria.banco).all()

    def crear_cuenta_bancaria(self, banco: str, tipo_cuenta: str, numero: str, moneda: str = "", saldo_inicial: float = 0):
        with get_db() as db:
            cuenta = CuentaBancaria(banco=banco, tipo_cuenta=tipo_cuenta, numero=numero, moneda=moneda, saldo=saldo_inicial)
            db.add(cuenta)
            db.flush()
            return cuenta

    def registrar_movimiento_banco(self, cuenta_id: int, tipo: str, concepto: str, monto: float, referencia: str = ""):
        with get_db() as db:
            cuenta = db.get(CuentaBancaria, cuenta_id)
            if not cuenta:
                raise ValueError("Cuenta bancaria no encontrada")
            if tipo in ("deposito", "credito", "transferencia_in"):
                cuenta.saldo += monto
            else:
                cuenta.saldo -= monto
            mov = MovimientoBanco(
                cuenta_bancaria_id=cuenta_id, fecha=date.today(), tipo=tipo,
                concepto=concepto, referencia=referencia, monto=monto,
                saldo=cuenta.saldo,
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(mov)
            return mov

    def listar_movimientos_banco(self, cuenta_id: int, limite: int = 100):
        with get_db() as db:
            return db.query(MovimientoBanco).filter(
                MovimientoBanco.cuenta_bancaria_id == cuenta_id
            ).order_by(MovimientoBanco.fecha.desc(), MovimientoBanco.id.desc()).limit(limite).all()

    def conciliar_movimiento(self, movimiento_id: int):
        with get_db() as db:
            mov = db.get(MovimientoBanco, movimiento_id)
            if mov:
                mov.conciliado = not mov.conciliado

    # === CAJA ===
    def abrir_caja(self, monto_apertura: float):
        with get_db() as db:
            caja_abierta = db.query(Caja).filter(Caja.estado == "abierta").first()
            if caja_abierta:
                raise ValueError("Ya hay una caja abierta. Cierre primero.")
            caja = Caja(
                fecha=date.today(), apertura=monto_apertura, estado="abierta",
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(caja)
            db.flush()
            return caja

    def cerrar_caja(self, monto_cierre: float):
        with get_db() as db:
            caja = db.query(Caja).filter(Caja.estado == "abierta").first()
            if not caja:
                raise ValueError("No hay caja abierta.")
            caja.cierre = monto_cierre
            caja.estado = "cerrada"
            return caja

    def caja_actual(self):
        with get_db() as db:
            return db.query(Caja).filter(Caja.estado == "abierta").first()

    def registrar_movimiento_caja(self, tipo: str, concepto: str, monto: float, referencia: str = ""):
        with get_db() as db:
            caja = db.query(Caja).filter(Caja.estado == "abierta").first()
            if not caja:
                raise ValueError("No hay caja abierta.")
            mov = MovimientoCaja(
                caja_id=caja.id, tipo=tipo, concepto=concepto, monto=monto,
                referencia=referencia,
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(mov)
            return mov

    def resumen_caja(self):
        with get_db() as db:
            caja = db.query(Caja).filter(Caja.estado == "abierta").first()
            if not caja:
                return None
            ingresos = db.query(func.sum(MovimientoCaja.monto)).filter(
                MovimientoCaja.caja_id == caja.id, MovimientoCaja.tipo == "ingreso"
            ).scalar() or 0
            egresos = db.query(func.sum(MovimientoCaja.monto)).filter(
                MovimientoCaja.caja_id == caja.id, MovimientoCaja.tipo == "egreso"
            ).scalar() or 0
            return {
                "apertura": caja.apertura,
                "ingresos": float(ingresos),
                "egresos": float(egresos),
                "saldo_actual": caja.apertura + float(ingresos) - float(egresos),
                "fecha": caja.fecha,
            }


finanzas_service = FinanzasService()
