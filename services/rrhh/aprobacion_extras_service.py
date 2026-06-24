"""Servicio de aprobación de horas extra."""
from datetime import datetime
from decimal import Decimal
from core.database import get_db
from models.aprobacion_extras import AprobacionExtras
from models.asistencia import Asistencia
from models.empleado import Empleado
from sqlalchemy.orm import joinedload


def extras_requieren_aprobacion() -> bool:
    """Verifica si el módulo de aprobación está activo."""
    from services.empresa_service import empresa_service
    val = empresa_service.obtener("aprobacion_extras_activa")
    return val == "1" or val == "true"


class AprobacionExtrasService:
    def listar_pendientes(self) -> list[AprobacionExtras]:
        with get_db() as db:
            return db.query(AprobacionExtras).options(
                joinedload(AprobacionExtras.asistencia).joinedload(Asistencia.empleado)
            ).filter(
                AprobacionExtras.estado == "pendiente"
            ).order_by(AprobacionExtras.created_at.desc()).all()

    def listar_todas(self, estado: str = None) -> list[AprobacionExtras]:
        with get_db() as db:
            query = db.query(AprobacionExtras).options(
                joinedload(AprobacionExtras.asistencia).joinedload(Asistencia.empleado)
            )
            if estado:
                query = query.filter(AprobacionExtras.estado == estado)
            return query.order_by(AprobacionExtras.created_at.desc()).all()

    def crear_desde_asistencia(self, asistencia_id: int, horas_extra: Decimal):
        """Crea una solicitud de aprobación para horas extra detectadas."""
        if horas_extra <= 0:
            return
        with get_db() as db:
            # Evitar duplicados
            existente = db.query(AprobacionExtras).filter_by(asistencia_id=asistencia_id).first()
            if existente:
                existente.horas_extra = horas_extra
                existente.estado = "pendiente"
            else:
                ap = AprobacionExtras(
                    asistencia_id=asistencia_id,
                    horas_extra=horas_extra,
                    estado="pendiente",
                )
                db.add(ap)

    def aprobar(self, aprobacion_id: int, usuario_id: int) -> AprobacionExtras | None:
        with get_db() as db:
            ap = db.get(AprobacionExtras, aprobacion_id)
            if not ap:
                return None
            ap.estado = "aprobada"
            ap.aprobado_por = usuario_id
            ap.fecha_aprobacion = datetime.now()
            db.flush()
            db.refresh(ap)
        return ap

    def rechazar(self, aprobacion_id: int, usuario_id: int, motivo: str = "") -> AprobacionExtras | None:
        with get_db() as db:
            ap = db.get(AprobacionExtras, aprobacion_id)
            if not ap:
                return None
            ap.estado = "rechazada"
            ap.aprobado_por = usuario_id
            ap.fecha_aprobacion = datetime.now()
            ap.motivo_rechazo = motivo
            db.flush()
            db.refresh(ap)
        return ap

    def aprobar_masivo(self, ids: list[int], usuario_id: int):
        with get_db() as db:
            for ap_id in ids:
                ap = db.get(AprobacionExtras, ap_id)
                if ap and ap.estado == "pendiente":
                    ap.estado = "aprobada"
                    ap.aprobado_por = usuario_id
                    ap.fecha_aprobacion = datetime.now()


aprobacion_extras_service = AprobacionExtrasService()
