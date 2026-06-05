from decimal import Decimal
from datetime import date
from sqlalchemy import func
from core.database import get_db
from models.empleado import Empleado
from models.asistencia import Asistencia
from models.nomina import Liquidacion
from models.adelanto import Adelanto
from models.cierre import CierreAsistencia


class DashboardService:
    def obtener_metricas(self) -> dict:
        periodo_actual = date.today().strftime("%Y-%m")
        anio = date.today().year
        mes = date.today().month

        if mes == 12:
            desde = date(anio, mes, 1)
            hasta = date(anio + 1, 1, 1)
        else:
            desde = date(anio, mes, 1)
            hasta = date(anio, mes + 1, 1)

        with get_db() as db:
            empleados_activos = db.query(func.count(Empleado.id)).filter(Empleado.activo == True).scalar() or 0

            horas_mes = db.query(
                func.coalesce(func.sum(Asistencia.horas_normales), 0),
                func.coalesce(func.sum(Asistencia.horas_extra), 0),
            ).filter(Asistencia.fecha >= desde, Asistencia.fecha < hasta).first()

            liquidaciones_mes = db.query(func.count(Liquidacion.id)).filter(
                Liquidacion.periodo == periodo_actual
            ).scalar() or 0

            adelantos_pendientes = db.query(
                func.coalesce(func.sum(Adelanto.saldo_pendiente), 0)
            ).filter(Adelanto.completado == False).scalar() or Decimal("0")

            asistencia_cerrada = db.query(CierreAsistencia).filter_by(
                periodo=periodo_actual, cerrado=True
            ).first() is not None

        return {
            "empleados_activos": empleados_activos,
            "horas_normales_mes": horas_mes[0],
            "horas_extra_mes": horas_mes[1],
            "liquidaciones_mes": liquidaciones_mes,
            "pendientes_liquidar": empleados_activos - liquidaciones_mes,
            "adelantos_pendientes": adelantos_pendientes,
            "periodo_actual": periodo_actual,
            "asistencia_cerrada": asistencia_cerrada,
        }


dashboard_service = DashboardService()
