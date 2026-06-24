"""Sub-servicio: Credito y reportes de clientes."""
from services.clientes._base import *


class CreditoClienteService:
    def verificar_credito(self, cliente_id: int, monto_nuevo: float = 0) -> dict:
        with get_db() as db:
            cliente = db.get(Cliente, cliente_id)
            if not cliente:
                raise ValueError("Cliente no encontrado")
            deuda_actual = cliente.saldo or 0
            limite = cliente.limite_credito or 0
            disponible = limite - deuda_actual if limite > 0 else 0
            bloqueado = cliente.credito_bloqueado
            excede = (limite > 0 and (deuda_actual + monto_nuevo) > limite)
            puede = not bloqueado and (limite == 0 or not excede)
            return {
                "cliente": cliente.razon_social,
                "limite_credito": limite,
                "deuda_actual": deuda_actual,
                "disponible": max(0, disponible),
                "bloqueado": bloqueado,
                "puede_comprar": puede,
                "monto_consultado": monto_nuevo,
            }

    def bloquear_credito(self, cliente_id: int):
        with get_db() as db:
            cliente = db.get(Cliente, cliente_id)
            if cliente:
                cliente.credito_bloqueado = True

    def desbloquear_credito(self, cliente_id: int):
        with get_db() as db:
            cliente = db.get(Cliente, cliente_id)
            if cliente:
                cliente.credito_bloqueado = False

    def registrar_cargo(self, cliente_id: int, monto: float, referencia: str = ""):
        with get_db() as db:
            cliente = db.get(Cliente, cliente_id)
            if not cliente:
                raise ValueError("Cliente no encontrado")
            cliente.saldo += monto
            if cliente.limite_credito > 0 and cliente.saldo > cliente.limite_credito:
                cliente.credito_bloqueado = True

    def registrar_pago(self, cliente_id: int, monto: float, referencia: str = ""):
        with get_db() as db:
            cliente = db.get(Cliente, cliente_id)
            if not cliente:
                raise ValueError("Cliente no encontrado")
            cliente.saldo = max(0, cliente.saldo - monto)
            if cliente.limite_credito > 0 and cliente.saldo <= cliente.limite_credito:
                cliente.credito_bloqueado = False

    def clientes_con_deuda(self):
        with get_db() as db:
            return db.query(Cliente).filter(Cliente.activo.is_(True), Cliente.saldo > 0).order_by(Cliente.saldo.desc()).all()

    def clientes_bloqueados(self):
        with get_db() as db:
            return db.query(Cliente).filter(Cliente.activo.is_(True), Cliente.credito_bloqueado.is_(True)).all()

    def clientes_por_cobrador(self, cobrador_id: int):
        with get_db() as db:
            return db.query(Cliente).filter(Cliente.activo.is_(True), Cliente.cobrador_id == cobrador_id).order_by(Cliente.razon_social).all()
