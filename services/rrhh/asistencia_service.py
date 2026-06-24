from datetime import date, time, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.asistencia import Asistencia, Feriado, TipoDia, TurnoLaboral, FichajePIN
from models.empleado import Empleado
from models.sucursal import Sucursal  # noqa: resolver relationship

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
        emp_data = self._get_empleado_horario(empleado_id)

        # Calcular tardanza y salida anticipada
        tardanza = 0
        salida_anticipada = 0
        if emp_data and not incompleto:
            tardanza = self._calcular_tardanza(hora_entrada, emp_data["hora_entrada"], emp_data["tolerancia"])
            salida_anticipada = self._calcular_salida_anticipada(hora_salida, emp_data["hora_salida"])

        # Clasificar horas extra
        tipo_extra = ""
        if incompleto:
            horas_normales = Decimal("0")
            horas_extra = Decimal("0")
        elif tipo_dia == TipoDia.DOMINGO or es_feriado:
            horas_normales = Decimal("0")
            horas_extra = horas_totales
            tipo_extra = "100"  # 100% recargo
        elif tipo_dia == TipoDia.SABADO:
            horas_normales = Decimal("0")
            horas_extra = horas_totales
            tipo_extra = "50"  # 50% recargo
        else:
            horas_normales = min(horas_totales, jornada)
            horas_extra = max(horas_totales - jornada, Decimal("0"))
            if horas_extra > 0:
                tipo_extra = "nocturna" if self._es_horario_nocturno(hora_entrada, hora_salida) else "50"

        with get_db() as db:
            existente = db.query(Asistencia).filter_by(empleado_id=empleado_id, fecha=fecha).first()
            if existente:
                existente.hora_entrada = hora_entrada
                existente.hora_salida = hora_salida
                existente.tipo_dia = tipo_dia.value
                existente.horas_normales = horas_normales
                existente.horas_extra = horas_extra
                existente.es_feriado = es_feriado
                existente.incompleto = incompleto
                existente.tardanza_minutos = tardanza
                existente.salida_anticipada_minutos = salida_anticipada
                existente.tipo_extra = tipo_extra
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
                tardanza_minutos=tardanza,
                salida_anticipada_minutos=salida_anticipada,
                tipo_extra=tipo_extra,
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

    def _get_empleado_horario(self, empleado_id: int) -> dict | None:
        with get_db() as db:
            emp = db.get(Empleado, empleado_id)
            if not emp:
                return None
            h_e = time.fromisoformat(emp.hora_entrada) if emp.hora_entrada else time(8, 0)
            h_s = time.fromisoformat(emp.hora_salida) if emp.hora_salida else time(17, 0)
            return {"hora_entrada": h_e, "hora_salida": h_s, "tolerancia": 10}

    def _calcular_tardanza(self, hora_real: time, hora_esperada: time, tolerancia: int) -> int:
        """Calcula minutos de tardanza (descontando tolerancia)."""
        dt_real = datetime.combine(date.today(), hora_real)
        dt_esperada = datetime.combine(date.today(), hora_esperada) + timedelta(minutes=tolerancia)
        if dt_real > dt_esperada:
            return int((dt_real - dt_esperada).total_seconds() / 60)
        return 0

    def _calcular_salida_anticipada(self, hora_real: time, hora_esperada: time) -> int:
        """Calcula minutos de salida anticipada."""
        dt_real = datetime.combine(date.today(), hora_real)
        dt_esperada = datetime.combine(date.today(), hora_esperada)
        if dt_real < dt_esperada:
            return int((dt_esperada - dt_real).total_seconds() / 60)
        return 0

    def _es_horario_nocturno(self, entrada: time, salida: time) -> bool:
        """Determina si las horas extra son en horario nocturno (21:00-06:00)."""
        return entrada.hour >= 21 or salida.hour <= 6


asistencia_service = AsistenciaService()


# === TURNOS ===
class TurnoService:
    def listar_turnos(self):
        with get_db() as db:
            return db.query(TurnoLaboral).filter(TurnoLaboral.activo.is_(True)).order_by(TurnoLaboral.codigo).all()

    def crear_turno(self, codigo: str, nombre: str, hora_entrada: time, hora_salida: time,
                    tolerancia_entrada: int = 10, es_nocturno: bool = False) -> TurnoLaboral:
        with get_db() as db:
            horas = self._calcular_horas_turno(hora_entrada, hora_salida)
            turno = TurnoLaboral(
                codigo=codigo[:20].upper(), nombre=nombre[:100],
                hora_entrada=hora_entrada, hora_salida=hora_salida,
                tolerancia_entrada=tolerancia_entrada, es_nocturno=es_nocturno,
                horas_jornada=horas,
            )
            db.add(turno)
            db.flush()
            return turno

    def _calcular_horas_turno(self, entrada: time, salida: time) -> Decimal:
        dt_e = datetime.combine(date.today(), entrada)
        dt_s = datetime.combine(date.today(), salida)
        if dt_s <= dt_e:
            dt_s += timedelta(days=1)
        return Decimal(str(round((dt_s - dt_e).total_seconds() / 3600, 2)))


turno_service = TurnoService()


# === FICHAJE PIN ===
class FichajeService:
    """Fichaje desde la app por PIN o codigo de empleado."""

    def fichar(self, empleado_id: int, tipo: str = "entrada", metodo: str = "pin", dispositivo: str = "") -> FichajePIN:
        """Registra fichaje. tipo: 'entrada' o 'salida'."""
        if tipo not in ("entrada", "salida"):
            raise ValueError("Tipo debe ser 'entrada' o 'salida'")
        ahora = datetime.now()
        with get_db() as db:
            emp = db.get(Empleado, empleado_id)
            if not emp or not emp.activo:
                raise ValueError("Empleado no encontrado o inactivo")
            fichaje = FichajePIN(
                empleado_id=empleado_id, fecha=ahora.date(),
                hora=ahora.time().replace(microsecond=0),
                tipo=tipo, metodo=metodo[:20], dispositivo=dispositivo[:50],
            )
            db.add(fichaje)
            db.flush()

            # Si es salida, auto-registrar asistencia completa
            if tipo == "salida":
                entrada = db.query(FichajePIN).filter(
                    FichajePIN.empleado_id == empleado_id,
                    FichajePIN.fecha == ahora.date(),
                    FichajePIN.tipo == "entrada",
                ).order_by(FichajePIN.hora.desc()).first()
                if entrada:
                    asistencia_service.registrar(
                        empleado_id, ahora.date(),
                        entrada.hora, fichaje.hora,
                    )
            return fichaje

    def fichar_por_legajo(self, legajo: str, tipo: str = "entrada", dispositivo: str = "") -> dict:
        """Fichaje usando numero de legajo (para terminal de fichaje)."""
        with get_db() as db:
            emp = db.query(Empleado).filter(Empleado.legajo == legajo, Empleado.activo.is_(True)).first()
            if not emp:
                raise ValueError(f"Legajo '{legajo}' no encontrado")
        fichaje = self.fichar(emp.id, tipo, "pin", dispositivo)
        return {"empleado": f"{emp.apellido}, {emp.nombre}", "tipo": tipo, "hora": str(fichaje.hora)}

    def fichajes_hoy(self, empleado_id: int = None):
        hoy = date.today()
        with get_db() as db:
            q = db.query(FichajePIN).filter(FichajePIN.fecha == hoy)
            if empleado_id:
                q = q.filter(FichajePIN.empleado_id == empleado_id)
            return q.order_by(FichajePIN.hora.desc()).all()


fichaje_service = FichajeService()
