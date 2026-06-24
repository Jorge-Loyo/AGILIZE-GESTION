from datetime import date, time, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.asistencia import Asistencia, Feriado, TipoDia
from models.empleado import Empleado

JORNADA_DEFAULT = Decimal("8")


class AsistenciaService:
    def registrar(self, empleado_id: int, fecha: date, hora_entrada: time, hora_salida: time, incompleto: bool = False) -> Asistencia:
        # Validar cierre
        from services.rrhh.cierre_service import cierre_service
        if cierre_service.fecha_en_cierre(fecha):
            raise ValueError(f"La fecha {fecha.strftime('%d/%m/%Y')} esta en un periodo cerrado. No se puede editar.")

        tipo_dia = self._determinar_tipo_dia(fecha)
        es_feriado = tipo_dia == TipoDia.FERIADO
        horas_totales = self._calcular_horas(hora_entrada, hora_salida)
        jornada = self._get_jornada_empleado(empleado_id)

        if incompleto:
            horas_normales = Decimal("0")
            horas_extra = Decimal("0")
        elif tipo_dia in (TipoDia.SABADO, TipoDia.DOMINGO, TipoDia.FERIADO):
            horas_normales = Decimal("0")
            horas_extra = horas_totales
        else:
            horas_normales = min(horas_totales, jornada)
            horas_extra = max(horas_totales - jornada, Decimal("0"))

        with get_db() as db:
            # Actualizar si ya existe registro para ese día
            existente = db.query(Asistencia).filter_by(empleado_id=empleado_id, fecha=fecha).first()
            if existente:
                existente.hora_entrada = hora_entrada
                existente.hora_salida = hora_salida
                existente.tipo_dia = tipo_dia.value
                existente.horas_normales = horas_normales
                existente.horas_extra = horas_extra
                existente.es_feriado = es_feriado
                existente.incompleto = incompleto
                db.flush()
                db.refresh(existente)
                return existente

            asistencia = Asistencia(
                empleado_id=empleado_id,
                fecha=fecha,
                hora_entrada=hora_entrada,
                hora_salida=hora_salida,
                tipo_dia=tipo_dia.value,
                horas_normales=horas_normales,
                horas_extra=horas_extra,
                es_feriado=es_feriado,
                incompleto=incompleto,
            )
            db.add(asistencia)
            db.flush()
            db.refresh(asistencia)
            return asistencia

    def listar(self, empleado_id: int | None = None, desde: date | None = None, hasta: date | None = None) -> list[Asistencia]:
        with get_db() as db:
            query = db.query(Asistencia).options(joinedload(Asistencia.empleado))
            if empleado_id:
                query = query.filter(Asistencia.empleado_id == empleado_id)
            if desde:
                query = query.filter(Asistencia.fecha >= desde)
            if hasta:
                query = query.filter(Asistencia.fecha <= hasta)
            return query.order_by(Asistencia.fecha.desc()).all()

    def resumen_periodo(self, empleado_id: int, desde: date, hasta: date) -> dict:
        registros = self.listar(empleado_id=empleado_id, desde=desde, hasta=hasta)
        total_normales = sum(r.horas_normales for r in registros)
        total_extra = sum(r.horas_extra for r in registros)
        dias_trabajados = len(registros)
        dias_feriado = sum(1 for r in registros if r.es_feriado)
        return {
            "dias_trabajados": dias_trabajados,
            "dias_feriado": dias_feriado,
            "horas_normales": total_normales,
            "horas_extra": total_extra,
            "horas_totales": total_normales + total_extra,
        }

    def listar_empleados_activos(self) -> list[Empleado]:
        with get_db() as db:
            return db.query(Empleado).filter(Empleado.activo == True).order_by(Empleado.apellido).all()

    def listar_feriados(self, anio: int | None = None) -> list[Feriado]:
        with get_db() as db:
            query = db.query(Feriado)
            if anio:
                query = query.filter(Feriado.fecha >= date(anio, 1, 1), Feriado.fecha <= date(anio, 12, 31))
            return query.order_by(Feriado.fecha).all()

    def agregar_feriado(self, fecha: date, descripcion: str) -> Feriado:
        with get_db() as db:
            feriado = Feriado(fecha=fecha, descripcion=descripcion)
            db.add(feriado)
            db.flush()
            db.refresh(feriado)
            return feriado

    def _get_jornada_empleado(self, empleado_id: int) -> Decimal:
        with get_db() as db:
            emp = db.get(Empleado, empleado_id)
            if emp and emp.horas_jornada:
                return emp.horas_jornada
        return JORNADA_DEFAULT

    def _determinar_tipo_dia(self, fecha: date) -> TipoDia:
        with get_db() as db:
            es_feriado = db.query(Feriado).filter_by(fecha=fecha).first()
            if es_feriado:
                return TipoDia.FERIADO

        weekday = fecha.weekday()
        if weekday == 5:
            return TipoDia.SABADO
        if weekday == 6:
            return TipoDia.DOMINGO
        return TipoDia.NORMAL

    def _calcular_horas(self, entrada: time, salida: time) -> Decimal:
        dt_entrada = datetime.combine(date.today(), entrada)
        dt_salida = datetime.combine(date.today(), salida)
        if dt_salida <= dt_entrada:
            dt_salida += timedelta(days=1)  # Turno nocturno
        diff = (dt_salida - dt_entrada).total_seconds() / 3600
        return Decimal(str(round(diff, 2)))


asistencia_service = AsistenciaService()
