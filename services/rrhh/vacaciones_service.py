"""Servicio de Vacaciones — Ley 20.744 Argentina."""
from datetime import date, datetime
from core.database import get_db
from models.vacaciones import Vacaciones
from models.empleado import Empleado


def calcular_dias_por_antiguedad(fecha_ingreso: date) -> int:
    """Calcula días de vacaciones según antigüedad (Ley 20.744)."""
    hoy = date.today()
    antiguedad = (hoy - fecha_ingreso).days / 365.25
    if antiguedad > 20:
        return 35
    if antiguedad > 10:
        return 28
    if antiguedad > 5:
        return 21
    return 14


class VacacionesService:
    def listar(self, empleado_id: int = None, periodo: int = None) -> list[Vacaciones]:
        with get_db() as db:
            query = db.query(Vacaciones)
            if empleado_id:
                query = query.filter(Vacaciones.empleado_id == empleado_id)
            if periodo:
                query = query.filter(Vacaciones.periodo_anual == periodo)
            return query.order_by(Vacaciones.periodo_anual.desc(), Vacaciones.fecha_desde.desc()).all()

    def obtener_saldo(self, empleado_id: int, periodo: int) -> dict:
        """Retorna días correspondientes, tomados y disponibles."""
        with get_db() as db:
            emp = db.get(Empleado, empleado_id)
            if not emp or not emp.fecha_ingreso:
                return {"correspondientes": 0, "tomados": 0, "disponibles": 0}

            correspondientes = calcular_dias_por_antiguedad(emp.fecha_ingreso)

            tomados = 0
            registros = db.query(Vacaciones).filter(
                Vacaciones.empleado_id == empleado_id,
                Vacaciones.periodo_anual == periodo,
                Vacaciones.estado.in_(["aprobada", "tomada"]),
            ).all()
            for r in registros:
                tomados += r.dias_tomados

        return {
            "correspondientes": correspondientes,
            "tomados": tomados,
            "disponibles": correspondientes - tomados,
        }

    def solicitar(self, empleado_id: int, periodo: int, fecha_desde: date, fecha_hasta: date, observaciones: str = "") -> Vacaciones:
        dias = (fecha_hasta - fecha_desde).days + 1
        saldo = self.obtener_saldo(empleado_id, periodo)
        if dias > saldo["disponibles"]:
            raise ValueError(f"Dias solicitados ({dias}) exceden disponibles ({saldo['disponibles']})")

        with get_db() as db:
            vac = Vacaciones(
                empleado_id=empleado_id,
                periodo_anual=periodo,
                dias_correspondientes=saldo["correspondientes"],
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                dias_tomados=dias,
                estado="pendiente",
                observaciones=observaciones,
            )
            db.add(vac)
            db.flush()
            db.refresh(vac)
        return vac

    def aprobar(self, vacaciones_id: int, usuario_id: int) -> Vacaciones | None:
        with get_db() as db:
            vac = db.get(Vacaciones, vacaciones_id)
            if not vac:
                return None
            vac.estado = "aprobada"
            vac.aprobado_por = usuario_id
            vac.fecha_aprobacion = datetime.now()
            db.flush()
            db.refresh(vac)
        return vac

    def tomar(self, vacaciones_id: int) -> Vacaciones | None:
        with get_db() as db:
            vac = db.get(Vacaciones, vacaciones_id)
            if not vac:
                return None
            vac.estado = "tomada"
            db.flush()
            db.refresh(vac)
        return vac

    def cancelar(self, vacaciones_id: int) -> Vacaciones | None:
        with get_db() as db:
            vac = db.get(Vacaciones, vacaciones_id)
            if not vac:
                return None
            vac.estado = "cancelada"
            db.flush()
            db.refresh(vac)
        return vac


vacaciones_service = VacacionesService()
