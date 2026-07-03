from decimal import Decimal
from datetime import date
from sqlalchemy import func, distinct
from core.database import get_db
from models.empleado import Empleado
from models.asistencia import Asistencia
from models.nomina import Liquidacion
from models.adelanto import Adelanto
from models.cierre import CierreAsistencia
from models.vacaciones import Vacaciones


class DashboardService:
    def obtener_metricas(self, periodo: str = None) -> dict:
        """Metricas por periodo. Si no se pasa, usa el mes actual."""
        if not periodo:
            periodo = date.today().strftime("%Y-%m")

        from services.rrhh.periodo_service import rango_de_periodo
        desde, hasta = rango_de_periodo(periodo)

        with get_db() as db:
            empleados_activos = db.query(func.count(Empleado.id)).filter(Empleado.activo == True).scalar() or 0

            horas_mes = db.query(
                func.coalesce(func.sum(Asistencia.horas_normales), 0),
                func.coalesce(func.sum(Asistencia.horas_extra), 0),
            ).filter(Asistencia.fecha >= desde, Asistencia.fecha <= hasta).first()

            liquidaciones_mes = db.query(func.count(Liquidacion.id)).filter(
                Liquidacion.periodo == periodo
            ).scalar() or 0

            adelantos_pendientes = db.query(
                func.coalesce(func.sum(Adelanto.saldo_pendiente), 0)
            ).filter(Adelanto.completado == False).scalar() or Decimal("0")

            asistencia_cerrada = db.query(CierreAsistencia).filter_by(
                periodo=periodo, cerrado=True
            ).first() is not None

            # Empleados que ficharon en el periodo
            emp_con_asistencia = db.query(func.count(distinct(Asistencia.empleado_id))).filter(
                Asistencia.fecha >= desde, Asistencia.fecha <= hasta
            ).scalar() or 0

        return {
            "empleados_activos": empleados_activos,
            "horas_normales_mes": horas_mes[0],
            "horas_extra_mes": horas_mes[1],
            "liquidaciones_mes": liquidaciones_mes,
            "pendientes_liquidar": max(0, empleados_activos - liquidaciones_mes),
            "adelantos_pendientes": adelantos_pendientes,
            "periodo_actual": periodo,
            "asistencia_cerrada": asistencia_cerrada,
            "emp_con_asistencia": emp_con_asistencia,
        }

    def obtener_metricas_globales(self) -> dict:
        """Metricas globales independientes del periodo."""
        hoy = date.today()
        with get_db() as db:
            total_activos = db.query(func.count(Empleado.id)).filter(Empleado.activo == True).scalar() or 0
            total_inactivos = db.query(func.count(Empleado.id)).filter(Empleado.activo == False).scalar() or 0

            gasto_acumulado = db.query(
                func.coalesce(func.sum(Liquidacion.neto), 0)
            ).scalar() or Decimal("0")

            # Adelantos con saldo pendiente
            adelantos_activos = db.query(func.count(Adelanto.id)).filter(
                Adelanto.completado == False
            ).scalar() or 0

            deuda_adelantos = db.query(
                func.coalesce(func.sum(Adelanto.saldo_pendiente), 0)
            ).filter(Adelanto.completado == False).scalar() or Decimal("0")

            # Vacaciones pendientes/aprobadas
            vacaciones_pend = db.query(func.count(Vacaciones.id)).filter(
                Vacaciones.estado == "pendiente"
            ).scalar() or 0

            # Antigüedad promedio
            fechas_ingreso = db.query(Empleado.fecha_ingreso).filter(
                Empleado.activo == True, Empleado.fecha_ingreso.isnot(None)
            ).all()

        if fechas_ingreso:
            dias_total = sum((hoy - f[0]).days for f in fechas_ingreso)
            antig_promedio_meses = (dias_total / len(fechas_ingreso)) / 30
        else:
            antig_promedio_meses = 0

        return {
            "total_activos": total_activos,
            "total_inactivos": total_inactivos,
            "gasto_acumulado": gasto_acumulado,
            "adelantos_activos": adelantos_activos,
            "deuda_adelantos": deuda_adelantos,
            "vacaciones_pendientes": vacaciones_pend,
            "antiguedad_promedio_meses": antig_promedio_meses,
        }

    def listar_periodos_disponibles(self) -> list[str]:
        """Retorna periodos que tienen datos (asistencia o liquidaciones)."""
        with get_db() as db:
            periodos_asist = db.query(
                distinct(func.to_char(Asistencia.fecha, 'YYYY-MM'))
            ).all()
            periodos_liq = db.query(distinct(Liquidacion.periodo)).all()

        todos = set()
        for p in periodos_asist:
            if p[0]:
                todos.add(p[0])
        for p in periodos_liq:
            if p[0]:
                todos.add(p[0])

        # Agregar periodo actual
        todos.add(date.today().strftime("%Y-%m"))
        return sorted(todos, reverse=True)


dashboard_service = DashboardService()
