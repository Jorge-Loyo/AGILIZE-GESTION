from core.database import get_db
from models.audit_log import AuditLog
from services.auth_service import auth_service


def registrar_auditoria(accion: str, tabla: str = "", registro_id: int | None = None, detalle: str = ""):
    """Registra una acción en el log de auditoría."""
    usuario_id = auth_service.current_user.id if auth_service.current_user else None
    with get_db() as db:
        log = AuditLog(
            usuario_id=usuario_id,
            accion=accion,
            tabla=tabla,
            registro_id=registro_id,
            detalle=detalle,
        )
        db.add(log)


def listar_auditoria(limit: int = 100) -> list[AuditLog]:
    with get_db() as db:
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
