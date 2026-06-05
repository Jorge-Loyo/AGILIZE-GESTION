from datetime import datetime
from core.database import get_db
from models.cierre import CierreAsistencia, CierreLiquidacion


class CierreService:
    # === Asistencia ===

    def asistencia_cerrada(self, periodo: str) -> bool:
        with get_db() as db:
            cierre = db.query(CierreAsistencia).filter_by(periodo=periodo).first()
            return cierre.cerrado if cierre else False

    def cerrar_asistencia(self, periodo: str, usuario_id: int) -> CierreAsistencia:
        # Verificar si hay registros incompletos
        from models.asistencia import Asistencia
        anio, mes = int(periodo.split("-")[0]), int(periodo.split("-")[1])
        from datetime import date
        if mes == 12:
            desde = date(anio, mes, 1)
            hasta = date(anio + 1, 1, 1)
        else:
            desde = date(anio, mes, 1)
            hasta = date(anio, mes + 1, 1)

        with get_db() as db:
            incompletos = db.query(Asistencia).filter(
                Asistencia.fecha >= desde,
                Asistencia.fecha < hasta,
                Asistencia.incompleto == True,
            ).count()
            if incompletos > 0:
                raise ValueError(f"No se puede cerrar: hay {incompletos} registro(s) incompleto(s) en el periodo. Completalos antes de cerrar.")

        with get_db() as db:
            cierre = db.query(CierreAsistencia).filter_by(periodo=periodo).first()
            if cierre:
                cierre.cerrado = True
                cierre.cerrado_por = usuario_id
                cierre.fecha_cierre = datetime.now()
            else:
                cierre = CierreAsistencia(
                    periodo=periodo,
                    cerrado=True,
                    cerrado_por=usuario_id,
                    fecha_cierre=datetime.now(),
                )
                db.add(cierre)
            db.flush()
            db.refresh(cierre)
        from services.audit_service import registrar_auditoria
        registrar_auditoria("CIERRE", "cierres_asistencia", cierre.id, f"Cerrado periodo {periodo}")
        return cierre

    def reabrir_asistencia(self, periodo: str, usuario_id: int) -> CierreAsistencia | None:
        with get_db() as db:
            cierre = db.query(CierreAsistencia).filter_by(periodo=periodo).first()
            if not cierre:
                return None
            cierre.cerrado = False
            cierre.reabierto_por = usuario_id
            cierre.fecha_reapertura = datetime.now()
            db.flush()
            db.refresh(cierre)
        from services.audit_service import registrar_auditoria
        registrar_auditoria("REABRIR", "cierres_asistencia", cierre.id, f"Reabierto periodo {periodo}")
        return cierre

    def listar_cierres_asistencia(self) -> list[CierreAsistencia]:
        with get_db() as db:
            return db.query(CierreAsistencia).order_by(CierreAsistencia.periodo.desc()).all()

    # === Liquidación ===

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
