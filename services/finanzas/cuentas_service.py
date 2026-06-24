"""Servicio de cuentas corrientes: debe y haber de clientes y proveedores."""
from datetime import date
from sqlalchemy import func
from core.database import get_db
from models.cuentas import MovimientoCuenta
from models.datos import Cliente, Proveedor
from services.core.auth_service import auth_service


class CuentasService:
    def registrar_debe(self, tipo_entidad: str, entidad_id: int, monto: float,
                       concepto: str, comprobante: str = "", notas: str = ""):
        """Registra un DEBE (lo que nos deben o lo que debemos)."""
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        with get_db() as db:
            saldo_actual = self._calcular_saldo(db, tipo_entidad, entidad_id)
            nuevo_saldo = saldo_actual + monto
            mov = MovimientoCuenta(
                tipo_entidad=tipo_entidad,
                entidad_id=entidad_id,
                fecha=date.today(),
                tipo="debe",
                concepto=concepto,
                comprobante=comprobante,
                monto=monto,
                saldo=nuevo_saldo,
                notas=notas,
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(mov)
            self._actualizar_saldo_entidad(db, tipo_entidad, entidad_id, nuevo_saldo)

    def registrar_haber(self, tipo_entidad: str, entidad_id: int, monto: float,
                        concepto: str, comprobante: str = "", notas: str = ""):
        """Registra un HABER (pago recibido o pago realizado)."""
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        with get_db() as db:
            saldo_actual = self._calcular_saldo(db, tipo_entidad, entidad_id)
            nuevo_saldo = saldo_actual - monto
            mov = MovimientoCuenta(
                tipo_entidad=tipo_entidad,
                entidad_id=entidad_id,
                fecha=date.today(),
                tipo="haber",
                concepto=concepto,
                comprobante=comprobante,
                monto=monto,
                saldo=nuevo_saldo,
                notas=notas,
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(mov)
            self._actualizar_saldo_entidad(db, tipo_entidad, entidad_id, nuevo_saldo)

    def obtener_saldo(self, tipo_entidad: str, entidad_id: int) -> float:
        with get_db() as db:
            return self._calcular_saldo(db, tipo_entidad, entidad_id)

    def listar_movimientos(self, tipo_entidad: str, entidad_id: int = None, limite: int = 200):
        with get_db() as db:
            q = db.query(MovimientoCuenta).filter(MovimientoCuenta.tipo_entidad == tipo_entidad)
            if entidad_id:
                q = q.filter(MovimientoCuenta.entidad_id == entidad_id)
            return q.order_by(MovimientoCuenta.fecha.desc(), MovimientoCuenta.id.desc()).limit(limite).all()

    def resumen_clientes(self):
        """Retorna lista de clientes con saldo."""
        with get_db() as db:
            clientes = db.query(Cliente).filter(Cliente.activo == True).order_by(Cliente.razon_social).all()
            resultado = []
            for c in clientes:
                saldo = self._calcular_saldo(db, "cliente", c.id)
                resultado.append({"id": c.id, "razon_social": c.razon_social, "saldo": saldo})
            return resultado

    def resumen_proveedores(self):
        """Retorna lista de proveedores con saldo."""
        with get_db() as db:
            proveedores = db.query(Proveedor).filter(Proveedor.activo == True).order_by(Proveedor.razon_social).all()
            resultado = []
            for p in proveedores:
                saldo = self._calcular_saldo(db, "proveedor", p.id)
                resultado.append({"id": p.id, "razon_social": p.razon_social, "saldo": saldo})
            return resultado

    def resumen_general(self) -> dict:
        with get_db() as db:
            total_debe_cli = db.query(func.sum(MovimientoCuenta.monto)).filter(
                MovimientoCuenta.tipo_entidad == "cliente", MovimientoCuenta.tipo == "debe"
            ).scalar() or 0
            total_haber_cli = db.query(func.sum(MovimientoCuenta.monto)).filter(
                MovimientoCuenta.tipo_entidad == "cliente", MovimientoCuenta.tipo == "haber"
            ).scalar() or 0
            total_debe_prov = db.query(func.sum(MovimientoCuenta.monto)).filter(
                MovimientoCuenta.tipo_entidad == "proveedor", MovimientoCuenta.tipo == "debe"
            ).scalar() or 0
            total_haber_prov = db.query(func.sum(MovimientoCuenta.monto)).filter(
                MovimientoCuenta.tipo_entidad == "proveedor", MovimientoCuenta.tipo == "haber"
            ).scalar() or 0
            return {
                "saldo_clientes": total_debe_cli - total_haber_cli,
                "saldo_proveedores": total_debe_prov - total_haber_prov,
                "total_por_cobrar": total_debe_cli - total_haber_cli,
                "total_por_pagar": total_debe_prov - total_haber_prov,
            }

    @staticmethod
    def _calcular_saldo(db, tipo_entidad: str, entidad_id: int) -> float:
        ultimo = db.query(MovimientoCuenta).filter(
            MovimientoCuenta.tipo_entidad == tipo_entidad,
            MovimientoCuenta.entidad_id == entidad_id
        ).order_by(MovimientoCuenta.id.desc()).first()
        return ultimo.saldo if ultimo else 0.0

    @staticmethod
    def _actualizar_saldo_entidad(db, tipo_entidad: str, entidad_id: int, saldo: float):
        if tipo_entidad == "cliente":
            cli = db.get(Cliente, entidad_id)
            if cli:
                cli.saldo = saldo
        elif tipo_entidad == "proveedor":
            pass  # Proveedores no tienen campo saldo por ahora


cuentas_service = CuentasService()
