from datetime import datetime, date
from core.database import get_db
from models.cierre import CierreAsistencia, CierreLiquidacion
from models.asistencia import Asistencia


class CierreService:
    # === Asistencia ===

    def asistencia_cerrada(self, periodo: str) -> bool:
        """Verifica si el periodo completo esta cerrado (ambas quincenas)."""
        with get_db() as db:
            cierres = db.query(CierreAsistencia).filter_by(periodo=periodo, cerrado=True).all()
            return len(cierres) >= 2

    def fecha_en_cierre(self, fecha: date) -> bool:
        """Verifica si una fecha esta dentro de un rango cerrado."""
        with get_db() as db:
            cierres = db.query(CierreAsistencia).filter(
                CierreAsistencia.cerrado == True,
                CierreAsistencia.fecha_desde <= fecha,
                CierreAsistencia.fecha_hasta >= fecha,
            ).first()
            return cierres is not None

    def cerrar_asistencia_rango(self, desde: date, hasta: date, usuario_id: int) -> CierreAsistencia:
        """Cierra asistencia por rango de fechas."""
        # Verificar incompletos en el rango
        with get_db() as db:
            incompletos = db.query(Asistencia).filter(
                Asistencia.fecha >= desde,
                Asistencia.fecha <= hasta,
                Asistencia.incompleto == True,
            ).count()
            if incompletos > 0:
                raise ValueError(f"Hay {incompletos} registro(s) incompleto(s) en el rango. Completalos antes de cerrar.")

        periodo = desde.strftime("%Y-%m")
        quincena = 1 if desde.day <= 15 else 2

        with get_db() as db:
            cierre = CierreAsistencia(
                periodo=periodo,
                quincena=quincena,
                fecha_desde=desde,
                fecha_hasta=hasta,
                cerrado=True,
                cerrado_por=usuario_id,
                fecha_cierre=datetime.now(),
            )
            db.add(cierre)
            db.flush()
            db.refresh(cierre)

        from services.core.audit_service import registrar_auditoria
        registrar_auditoria("CIERRE", "cierres_asistencia", cierre.id, f"Cerrado {desde} a {hasta}")
        return cierre

    def reabrir_cierre(self, cierre_id: int, usuario_id: int):
        """Reabre un cierre por ID."""
        with get_db() as db:
            cierre = db.get(CierreAsistencia, cierre_id)
            if not cierre:
                return
            cierre.cerrado = False
            cierre.reabierto_por = usuario_id
            cierre.fecha_reapertura = datetime.now()

        from services.core.audit_service import registrar_auditoria
        registrar_auditoria("REABRIR", "cierres_asistencia", cierre_id, "Reabierto")

    def listar_cierres_asistencia(self) -> list[CierreAsistencia]:
        with get_db() as db:
            return db.query(CierreAsistencia).order_by(
                CierreAsistencia.fecha_desde.desc()
            ).all()

    # === Liquidacion ===

    def liquidacion_cerrada(self, empleado_id: int, periodo: str) -> bool:
        with get_db() as db:
            cierre = db.query(CierreLiquidacion).filter_by(
                empleado_id=empleado_id, periodo=periodo
            ).first()
            return cierre.cerrado if cierre else False

    def cerrar_liquidacion(self, empleado_id: int, periodo: str) -> CierreLiquidacion:
        with get_db() as db:
            cierre = db.query(CierreLiquidacion).filter_by(
                empleado_id=empleado_id, periodo=periodo
            ).first()
            if cierre:
                cierre.cerrado = True
                cierre.fecha_cierre = datetime.now()
            else:
                cierre = CierreLiquidacion(
                    empleado_id=empleado_id,
                    periodo=periodo,
                    cerrado=True,
                    fecha_cierre=datetime.now(),
                )
                db.add(cierre)
            db.flush()
            db.refresh(cierre)
            return cierre


cierre_service = CierreService()
