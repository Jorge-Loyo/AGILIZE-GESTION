"""Servicio de gestion de cajas POS: turnos, movimientos, arqueo."""
from datetime import date, datetime, timezone
import json
from sqlalchemy import func
from core.database import get_db
from models import sucursal, usuario, empleado, rol, permiso  # noqa
from models.caja_pos import CajaPOS, TurnoCaja, MovimientoCajaPOS
from services.core.auth_service import auth_service


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _hoy() -> date:
    return _ahora().date()


class CajaPOSService:
    # === CAJAS ===
    def listar_cajas(self):
        with get_db() as db:
            return db.query(CajaPOS).filter(CajaPOS.activo.is_(True)).order_by(CajaPOS.codigo).all()

    def crear_caja(self, codigo: str, nombre: str, sucursal_id: int = None) -> CajaPOS:
        with get_db() as db:
            caja = CajaPOS(codigo=codigo[:20].upper(), nombre=nombre[:100], sucursal_id=sucursal_id)
            db.add(caja)
            db.flush()
            return caja

    # === TURNOS ===
    def abrir_turno(self, caja_id: int, fondo_inicial: float = 0) -> TurnoCaja:
        """Abre turno/sesion de caja. Verifica que no haya turno abierto."""
        with get_db() as db:
            # Verificar que no haya turno abierto en esta caja
            turno_abierto = db.query(TurnoCaja).filter(
                TurnoCaja.caja_id == caja_id,
                TurnoCaja.estado == "abierto",
            ).first()
            if turno_abierto:
                raise ValueError("Ya hay un turno abierto en esta caja. Cierre primero.")

            turno = TurnoCaja(
                caja_id=caja_id,
                cajero_id=auth_service.current_user.id if auth_service.current_user else 0,
                fecha=_hoy(),
                hora_apertura=_ahora(),
                fondo_inicial=fondo_inicial,
                estado="abierto",
            )
            db.add(turno)
            db.flush()
            return turno

    def turno_activo(self, caja_id: int = None) -> TurnoCaja | None:
        """Obtiene turno abierto actual. Si no se pasa caja, busca por cajero."""
        with get_db() as db:
            q = db.query(TurnoCaja).filter(TurnoCaja.estado == "abierto")
            if caja_id:
                q = q.filter(TurnoCaja.caja_id == caja_id)
            elif auth_service.current_user:
                q = q.filter(TurnoCaja.cajero_id == auth_service.current_user.id)
            return q.first()

    # === MOVIMIENTOS ===
    def registrar_venta(self, turno_id: int, monto: float, medio_pago: str, referencia: str = "", detalle_medios: dict = None):
        """Registra venta en la caja. Para pagos partidos, detalle_medios es un dict."""
        with get_db() as db:
            turno = db.get(TurnoCaja, turno_id)
            if not turno or turno.estado != "abierto":
                raise ValueError("Turno no activo")

            # Guardar detalle de medios para pagos mixtos
            detalle_json = json.dumps(detalle_medios) if detalle_medios else ""

            mov = MovimientoCajaPOS(
                turno_id=turno_id, tipo="venta", medio_pago=medio_pago,
                monto=monto, referencia=referencia[:100],
                detalle_medios=detalle_json, hora=_ahora(),
            )
            db.add(mov)

            # Actualizar totales del turno
            if detalle_medios:
                # Pago partido: sumar por cada medio
                for medio, m in detalle_medios.items():
                    self._sumar_medio(turno, medio, m)
            else:
                self._sumar_medio(turno, medio_pago, monto)

    def registrar_retiro(self, turno_id: int, monto: float, motivo: str = ""):
        """Retiro de efectivo de la caja (para depositar, etc)."""
        if monto <= 0:
            raise ValueError("Monto debe ser mayor a 0")
        with get_db() as db:
            turno = db.get(TurnoCaja, turno_id)
            if not turno or turno.estado != "abierto":
                raise ValueError("Turno no activo")
            mov = MovimientoCajaPOS(
                turno_id=turno_id, tipo="retiro", medio_pago="efectivo",
                monto=monto, referencia=motivo[:100], hora=_ahora(),
            )
            db.add(mov)
            turno.retiros += monto

    def registrar_ingreso(self, turno_id: int, monto: float, motivo: str = ""):
        """Ingreso de efectivo a la caja (cambio, etc)."""
        if monto <= 0:
            raise ValueError("Monto debe ser mayor a 0")
        with get_db() as db:
            turno = db.get(TurnoCaja, turno_id)
            if not turno or turno.estado != "abierto":
                raise ValueError("Turno no activo")
            mov = MovimientoCajaPOS(
                turno_id=turno_id, tipo="ingreso", medio_pago="efectivo",
                monto=monto, referencia=motivo[:100], hora=_ahora(),
            )
            db.add(mov)
            turno.ingresos += monto

    def _sumar_medio(self, turno: TurnoCaja, medio: str, monto: float):
        if "efectivo" in medio:
            turno.total_efectivo += monto
        elif "debito" in medio:
            turno.total_tarjeta_debito += monto
        elif "credito" in medio:
            turno.total_tarjeta_credito += monto
        elif "transferencia" in medio:
            turno.total_transferencia += monto
        else:
            turno.total_otros += monto

    # === CIERRE / ARQUEO ===
    def calcular_esperado(self, turno_id: int) -> dict:
        """Calcula cuanto efectivo deberia haber en la caja."""
        with get_db() as db:
            turno = db.get(TurnoCaja, turno_id)
            if not turno:
                raise ValueError("Turno no encontrado")
            esperado = turno.fondo_inicial + turno.total_efectivo + turno.ingresos - turno.retiros
            return {
                "fondo_inicial": turno.fondo_inicial,
                "ventas_efectivo": turno.total_efectivo,
                "ingresos": turno.ingresos,
                "retiros": turno.retiros,
                "efectivo_esperado": round(esperado, 2),
            }

    def cerrar_turno(self, turno_id: int, efectivo_contado: float, observaciones: str = "") -> dict:
        """
        Cierra turno con arqueo.
        El cajero cuenta el efectivo CIEGO (sin saber cuanto deberia haber).
        El sistema calcula la diferencia.
        """
        with get_db() as db:
            turno = db.get(TurnoCaja, turno_id)
            if not turno:
                raise ValueError("Turno no encontrado")
            if turno.estado != "abierto":
                raise ValueError("Turno ya cerrado")

            esperado = turno.fondo_inicial + turno.total_efectivo + turno.ingresos - turno.retiros
            diferencia = round(efectivo_contado - esperado, 2)

            turno.hora_cierre = _ahora()
            turno.efectivo_esperado = round(esperado, 2)
            turno.efectivo_contado = efectivo_contado
            turno.diferencia = diferencia
            turno.observaciones = observaciones[:500]
            turno.estado = "con_diferencia" if diferencia != 0 else "cerrado"

            total_ventas = turno.total_efectivo + turno.total_tarjeta_debito + turno.total_tarjeta_credito + turno.total_transferencia + turno.total_otros

            return {
                "estado": turno.estado,
                "total_ventas": round(total_ventas, 2),
                "ventas_efectivo": turno.total_efectivo,
                "ventas_tarjeta_debito": turno.total_tarjeta_debito,
                "ventas_tarjeta_credito": turno.total_tarjeta_credito,
                "ventas_transferencia": turno.total_transferencia,
                "fondo_inicial": turno.fondo_inicial,
                "retiros": turno.retiros,
                "ingresos": turno.ingresos,
                "efectivo_esperado": round(esperado, 2),
                "efectivo_contado": efectivo_contado,
                "diferencia": diferencia,
                "sobrante": diferencia > 0,
                "faltante": diferencia < 0,
            }

    # === CONSULTAS ===
    def movimientos_turno(self, turno_id: int):
        with get_db() as db:
            return db.query(MovimientoCajaPOS).filter(
                MovimientoCajaPOS.turno_id == turno_id
            ).order_by(MovimientoCajaPOS.hora.desc()).all()

    def historial_turnos(self, caja_id: int = None, limite: int = 50):
        with get_db() as db:
            q = db.query(TurnoCaja)
            if caja_id:
                q = q.filter(TurnoCaja.caja_id == caja_id)
            return q.order_by(TurnoCaja.fecha.desc(), TurnoCaja.id.desc()).limit(limite).all()

    def resumen_caja_hoy(self, caja_id: int) -> dict:
        """Resumen del dia para una caja."""
        with get_db() as db:
            turnos = db.query(TurnoCaja).filter(
                TurnoCaja.caja_id == caja_id, TurnoCaja.fecha == _hoy()
            ).all()
            total_ventas = sum(t.total_efectivo + t.total_tarjeta_debito + t.total_tarjeta_credito + t.total_transferencia + t.total_otros for t in turnos)
            return {
                "turnos": len(turnos),
                "total_ventas": round(total_ventas, 2),
                "turno_abierto": any(t.estado == "abierto" for t in turnos),
            }


caja_pos_service = CajaPOSService()
