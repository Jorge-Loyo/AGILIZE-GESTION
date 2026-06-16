"""Servicio para obtener periodos y empleados pendientes de liquidar."""
from sqlalchemy import func, distinct
from sqlalchemy.orm import joinedload
from datetime import date
from core.database import get_db
from models.asistencia import Asistencia
from models.empleado import Empleado
from models.cierre import CierreLiquidacion
from services.periodo_service import obtener_frecuencia, periodo_actual, rango_de_periodo, generar_periodos_mes


class LiquidacionPendienteService:
    def periodos_con_asistencia(self) -> list[str]:
        """Retorna periodos (YYYY-MM) que tienen registros de asistencia."""
        with get_db() as db:
            fechas = db.query(
                distinct(func.to_char(Asistencia.fecha, 'YYYY-MM'))
            ).order_by(func.to_char(Asistencia.fecha, 'YYYY-MM').desc()).all()
            return [f[0] for f in fechas]

    def periodos_pendientes(self) -> list[str]:
        """Retorna periodos que tienen empleados sin liquidar."""
        hoy = date.today()
        # Generar periodos del mes actual segun frecuencia
        periodos_mes_actual = generar_periodos_mes(hoy.year, hoy.month)

        periodos = self.periodos_con_asistencia()
        # Agregar periodos del mes actual que no esten
        for p in periodos_mes_actual:
            if p not in periodos:
                periodos.insert(0, p)

        pendientes = []
        for periodo in periodos:
            resumen = self.resumen_periodo(periodo)
            if resumen["pendientes"] > 0:
                pendientes.append(periodo)
        return pendientes

    def empleados_pendientes(self, periodo: str) -> list[Empleado]:
        """Retorna empleados activos que no fueron liquidados en el periodo."""
        desde, hasta = rango_de_periodo(periodo)

        with get_db() as db:
            todos = db.query(Empleado).options(
                joinedload(Empleado.departamento)
            ).filter(Empleado.activo == True).all()

            emp_ids_liquidados = set(e[0] for e in db.query(
                CierreLiquidacion.empleado_id
            ).filter(
                CierreLiquidacion.periodo == periodo,
                CierreLiquidacion.cerrado == True,
            ).all())

            emp_ids_con_asistencia = set(e[0] for e in db.query(
                distinct(Asistencia.empleado_id)
            ).filter(
                Asistencia.fecha >= desde,
                Asistencia.fecha <= hasta,
            ).all())

            pendientes = []
            for emp in todos:
                if emp.id in emp_ids_liquidados:
                    continue
                if emp.tipo_liquidacion == "mensual":
                    pendientes.append(emp)
                elif emp.id in emp_ids_con_asistencia:
                    pendientes.append(emp)

            return pendientes

    def resumen_periodo(self, periodo: str) -> dict:
        """Resumen: total activos, liquidados, pendientes."""
        desde, hasta = rango_de_periodo(periodo)

        with get_db() as db:
            total_activos = db.query(func.count(Empleado.id)).filter(
                Empleado.activo == True
            ).scalar() or 0

            total_liquidados = db.query(func.count(CierreLiquidacion.id)).filter(
                CierreLiquidacion.periodo == periodo,
                CierreLiquidacion.cerrado == True,
            ).scalar() or 0

            con_asistencia = db.query(func.count(distinct(Asistencia.empleado_id))).filter(
                Asistencia.fecha >= desde,
                Asistencia.fecha <= hasta,
            ).scalar() or 0

            mensuales = db.query(func.count(Empleado.id)).filter(
                Empleado.activo == True,
                Empleado.tipo_liquidacion == "mensual",
            ).scalar() or 0

            total_a_liquidar = mensuales + con_asistencia
            pendientes = max(0, total_a_liquidar - total_liquidados)

        return {
            "periodo": periodo,
            "total_activos": total_activos,
            "total_a_liquidar": total_a_liquidar,
            "liquidados": total_liquidados,
            "pendientes": pendientes,
            "completo": pendientes == 0 and total_a_liquidar > 0,
        }

    def info_pendiente(self, empleado_id: int, periodo: str) -> dict:
        """Info de qué falta para poder liquidar a un empleado."""
        desde, hasta = rango_de_periodo(periodo)

        with get_db() as db:
            emp = db.get(Empleado, empleado_id)
            if not emp:
                return {"puede_liquidar": False, "motivo": "Empleado no encontrado"}

            if emp.tipo_liquidacion == "mensual":
                if not emp.sueldo_mensual or emp.sueldo_mensual <= 0:
                    return {"puede_liquidar": False, "motivo": "Falta configurar sueldo mensual"}
                return {"puede_liquidar": True, "motivo": ""}

            # Por hora
            if not emp.valor_hora or emp.valor_hora <= 0:
                return {"puede_liquidar": False, "motivo": "Falta configurar valor hora"}

            tiene_asist = db.query(Asistencia).filter(
                Asistencia.empleado_id == empleado_id,
                Asistencia.fecha >= desde,
                Asistencia.fecha <= hasta,
            ).first()

            if not tiene_asist:
                return {"puede_liquidar": False, "motivo": "Sin asistencia en el periodo"}

            return {"puede_liquidar": True, "motivo": ""}


liquidacion_pendiente_service = LiquidacionPendienteService()
