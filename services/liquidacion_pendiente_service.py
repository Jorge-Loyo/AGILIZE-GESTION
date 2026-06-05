"""Servicio para obtener periodos y empleados pendientes de liquidar."""
from sqlalchemy import func, distinct
from core.database import get_db
from models.asistencia import Asistencia
from models.empleado import Empleado
from models.cierre import CierreLiquidacion


class LiquidacionPendienteService:
    def periodos_con_asistencia(self) -> list[str]:
        """Retorna periodos (YYYY-MM) que tienen registros de asistencia."""
        with get_db() as db:
            fechas = db.query(
                distinct(func.to_char(Asistencia.fecha, 'YYYY-MM'))
            ).order_by(func.to_char(Asistencia.fecha, 'YYYY-MM').desc()).all()
            return [f[0] for f in fechas]

    def periodos_pendientes(self) -> list[str]:
        """Retorna periodos que tienen asistencia pero no todos liquidados."""
        periodos = self.periodos_con_asistencia()
        pendientes = []
        for periodo in periodos:
            resumen = self.resumen_periodo(periodo)
            if resumen["pendientes"] > 0:
                pendientes.append(periodo)
        return pendientes

    def empleados_pendientes(self, periodo: str) -> list[Empleado]:
        """Retorna empleados con asistencia en el periodo que no fueron liquidados."""
        anio, mes = int(periodo.split("-")[0]), int(periodo.split("-")[1])
        from datetime import date
        if mes == 12:
            desde = date(anio, mes, 1)
            hasta = date(anio + 1, 1, 1)
        else:
            desde = date(anio, mes, 1)
            hasta = date(anio, mes + 1, 1)

        with get_db() as db:
            # Empleados con asistencia en el periodo
            emp_ids_asistencia = db.query(distinct(Asistencia.empleado_id)).filter(
                Asistencia.fecha >= desde,
                Asistencia.fecha < hasta,
            ).all()
            emp_ids_asistencia = [e[0] for e in emp_ids_asistencia]

            # Empleados ya liquidados en el periodo
            emp_ids_liquidados = db.query(CierreLiquidacion.empleado_id).filter(
                CierreLiquidacion.periodo == periodo,
                CierreLiquidacion.cerrado == True,
            ).all()
            emp_ids_liquidados = [e[0] for e in emp_ids_liquidados]

            # Pendientes
            ids_pendientes = [eid for eid in emp_ids_asistencia if eid not in emp_ids_liquidados]

            if not ids_pendientes:
                return []

            from sqlalchemy.orm import joinedload
            return db.query(Empleado).options(
                joinedload(Empleado.departamento)
            ).filter(Empleado.id.in_(ids_pendientes)).all()

    def resumen_periodo(self, periodo: str) -> dict:
        """Resumen: total con asistencia, liquidados, pendientes."""
        anio, mes = int(periodo.split("-")[0]), int(periodo.split("-")[1])
        from datetime import date
        if mes == 12:
            desde = date(anio, mes, 1)
            hasta = date(anio + 1, 1, 1)
        else:
            desde = date(anio, mes, 1)
            hasta = date(anio, mes + 1, 1)

        with get_db() as db:
            total_asistencia = db.query(func.count(distinct(Asistencia.empleado_id))).filter(
                Asistencia.fecha >= desde,
                Asistencia.fecha < hasta,
            ).scalar() or 0

            total_liquidados = db.query(func.count(CierreLiquidacion.id)).filter(
                CierreLiquidacion.periodo == periodo,
                CierreLiquidacion.cerrado == True,
            ).scalar() or 0

        return {
            "periodo": periodo,
            "total_con_asistencia": total_asistencia,
            "liquidados": total_liquidados,
            "pendientes": total_asistencia - total_liquidados,
            "completo": total_asistencia == total_liquidados and total_asistencia > 0,
        }


liquidacion_pendiente_service = LiquidacionPendienteService()
