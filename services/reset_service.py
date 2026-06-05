"""Servicio para resetear la aplicacion a estado limpio."""
from core.database import get_db
from sqlalchemy import text


def resetear_aplicacion() -> str:
    """Limpia todos los datos operativos. Mantiene configuraciones, roles, permisos y usuarios."""
    with get_db() as db:
        tablas_limpiar = [
            "liquidacion_detalle",
            "liquidaciones",
            "sac_registros",
            "sac_liquidaciones",
            "adelantos",
            "asistencias",
            "ausencias",
            "permisos_empleado",
            "cierres_asistencia",
            "cierres_liquidacion",
            "audit_log",
            "empleados",
        ]
        for tabla in tablas_limpiar:
            db.execute(text(f"TRUNCATE {tabla} CASCADE"))

    return f"Aplicacion reseteada. Se limpiaron {len(tablas_limpiar)} tablas."
