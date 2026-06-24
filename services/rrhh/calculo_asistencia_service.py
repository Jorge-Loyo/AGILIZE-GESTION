from decimal import Decimal
from datetime import date, timedelta
from core.database import get_db
from models.asistencia import Asistencia
from models.empleado import Empleado
from services.rrhh.config_nomina_service import config_nomina_service


class CalculoAsistenciaService:
    def calcular_bruto_periodo(self, empleado_id: int, periodo: str) -> dict:
        """Calcula el sueldo bruto basado en asistencia real del período."""
        from services.rrhh.periodo_service import rango_de_periodo
        desde, hasta = rango_de_periodo(periodo)
        # hasta es inclusivo, para queries usamos <= hasta

        with get_db() as db:
            emp = db.get(Empleado, empleado_id)
            if not emp:
                return self._vacio()

            # Si es empleado mensual, usar cálculo por sueldo mensual
            if emp.tipo_liquidacion == "mensual":
                return self._calcular_mensual(emp, periodo, desde, hasta, db)

            return self._calcular_por_hora(emp, periodo, desde, hasta, db)

    def _calcular_por_hora(self, emp, periodo, desde, hasta, db) -> dict:
        """Cálculo estándar por horas fichadas."""
        params = config_nomina_service.obtener_todos()
        mult_extra = params["mult_hora_extra"]
        mult_sabado = params["mult_hora_sabado"]
        mult_domingo = params["mult_hora_domingo"]
        mult_feriado = params["mult_hora_feriado"]

        valor_hora = emp.valor_hora or Decimal("0")
        valor_hora_extra = emp.valor_hora_extra if emp.valor_hora_extra else valor_hora

        registros = db.query(Asistencia).filter(
            Asistencia.empleado_id == emp.id,
            Asistencia.fecha >= desde,
            Asistencia.fecha <= hasta,
        ).all()

        hs_normales = Decimal("0")
        hs_extra = Decimal("0")
        hs_sabado = Decimal("0")
        hs_domingo = Decimal("0")
        hs_feriado = Decimal("0")

        for r in registros:
            if r.tipo_dia == "feriado":
                hs_feriado += r.horas_normales + r.horas_extra
            elif r.tipo_dia == "sabado":
                hs_sabado += r.horas_normales + r.horas_extra
            elif r.tipo_dia == "domingo":
                hs_domingo += r.horas_normales + r.horas_extra
            else:
                hs_normales += r.horas_normales
                hs_extra += r.horas_extra

        monto_normales = (hs_normales * valor_hora).quantize(Decimal("0.01"))
        monto_extra = (hs_extra * valor_hora_extra * mult_extra).quantize(Decimal("0.01"))
        monto_sabado = (hs_sabado * valor_hora_extra * mult_sabado).quantize(Decimal("0.01"))
        monto_domingo = (hs_domingo * valor_hora_extra * mult_domingo).quantize(Decimal("0.01"))
        monto_feriado = (hs_feriado * valor_hora_extra * mult_feriado).quantize(Decimal("0.01"))

        bruto = monto_normales + monto_extra + monto_sabado + monto_domingo + monto_feriado

        return {
            "tipo_liquidacion": "por_hora",
            "valor_hora": valor_hora,
            "hs_normales": hs_normales,
            "hs_extra": hs_extra,
            "hs_sabado": hs_sabado,
            "hs_domingo": hs_domingo,
            "hs_feriado": hs_feriado,
            "monto_normales": monto_normales,
            "monto_extra": monto_extra,
            "monto_sabado": monto_sabado,
            "monto_domingo": monto_domingo,
            "monto_feriado": monto_feriado,
            "bruto": bruto,
            "mult_extra": mult_extra,
            "mult_sabado": mult_sabado,
            "mult_domingo": mult_domingo,
            "mult_feriado": mult_feriado,
            "dias_trabajados": len(registros),
            "sueldo_mensual": Decimal("0"),
            "faltas": 0,
            "descuento_faltas": Decimal("0"),
        }

    def _calcular_mensual(self, emp, periodo, desde, hasta, db) -> dict:
        """Cálculo para empleados mensuales: sueldo - descuento por faltas."""
        from models.permiso_empleado import Ausencia
        from services.rrhh.periodo_service import obtener_frecuencia

        sueldo = emp.sueldo_mensual or Decimal("0")
        freq = obtener_frecuencia()

        # Dias laborales del empleado
        dias_str = emp.dias_laborales or "lun,mar,mie,jue,vie"
        dias_lab = [d.strip().lower() for d in dias_str.split(",")]
        dia_map = {"lun": 0, "mar": 1, "mie": 2, "jue": 3, "vie": 4, "sab": 5, "dom": 6}
        dias_semana_lab = [dia_map.get(d, -1) for d in dias_lab if d in dia_map]

        # Contar dias laborales en el rango del periodo
        dias_periodo = 0
        d = desde
        while d <= hasta:
            if d.weekday() in dias_semana_lab:
                dias_periodo += 1
            d += timedelta(days=1)

        # Para quincenal/semanal/diario: proporcionar sueldo
        if freq == "mensual":
            sueldo_periodo = sueldo
        else:
            # Dias laborales del mes completo
            import calendar
            dias_mes = 0
            for dia in range(1, calendar.monthrange(desde.year, desde.month)[1] + 1):
                if date(desde.year, desde.month, dia).weekday() in dias_semana_lab:
                    dias_mes += 1
            sueldo_periodo = (sueldo * Decimal(str(dias_periodo)) / Decimal(str(dias_mes))).quantize(Decimal("0.01")) if dias_mes > 0 else Decimal("0")

        # Contar faltas (ausencias injustificadas en el rango)
        faltas = db.query(Ausencia).filter(
            Ausencia.empleado_id == emp.id,
            Ausencia.fecha >= desde,
            Ausencia.fecha <= hasta,
            Ausencia.justificada == False,
        ).count()

        # Sueldo diario y descuento
        sueldo_diario = (sueldo_periodo / Decimal(str(dias_periodo))).quantize(Decimal("0.01")) if dias_periodo > 0 else Decimal("0")
        descuento = (sueldo_diario * Decimal(str(faltas))).quantize(Decimal("0.01"))

        # Feriados del periodo: se pagan siempre (ya incluidos en sueldo)
        # Si se trabajan, se pagan DOBLE (adicional al sueldo)
        from models.asistencia import Feriado
        feriados_periodo = db.query(Feriado).filter(
            Feriado.fecha >= desde,
            Feriado.fecha <= hasta,
        ).all()
        fechas_feriado = set(f.fecha for f in feriados_periodo)

        # Horas extra y feriados trabajados (registrados en asistencias)
        registros_extra = db.query(Asistencia).filter(
            Asistencia.empleado_id == emp.id,
            Asistencia.fecha >= desde,
            Asistencia.fecha <= hasta,
        ).all()

        params = config_nomina_service.obtener_todos()
        mult_extra = params["mult_hora_extra"]
        mult_feriado = params["mult_hora_feriado"]
        jornada = emp.horas_jornada or Decimal("8")
        valor_hora_extra = emp.valor_hora_extra if emp.valor_hora_extra else (sueldo_diario / jornada).quantize(Decimal("0.01"))

        hs_extra = Decimal("0")
        hs_feriado_trabajado = Decimal("0")
        fechas_feriado_con_registro = set()

        for r in registros_extra:
            if r.tipo_dia == "feriado" or r.fecha in fechas_feriado:
                hs_feriado_trabajado += r.horas_normales + r.horas_extra
                fechas_feriado_con_registro.add(r.fecha)
            else:
                hs_extra += r.horas_extra

        # Feriados NO trabajados: se pagan la jornada completa (ya incluida en sueldo, no sumar)
        # Feriados TRABAJADOS: se paga adicional con multiplicador (es el "doble")
        monto_extra = (hs_extra * valor_hora_extra * mult_extra).quantize(Decimal("0.01"))
        monto_feriado = (hs_feriado_trabajado * valor_hora_extra * mult_feriado).quantize(Decimal("0.01"))

        # Total feriados en periodo (para info)
        total_feriados = len(fechas_feriado)
        feriados_trabajados = len(fechas_feriado_con_registro)

        bruto = sueldo_periodo - descuento + monto_extra + monto_feriado

        return {
            "tipo_liquidacion": "mensual",
            "valor_hora": Decimal("0"),
            "hs_normales": Decimal("0"),
            "hs_extra": hs_extra,
            "hs_sabado": Decimal("0"),
            "hs_domingo": Decimal("0"),
            "hs_feriado": hs_feriado_trabajado,
            "monto_normales": Decimal("0"),
            "monto_extra": monto_extra,
            "monto_sabado": Decimal("0"),
            "monto_domingo": Decimal("0"),
            "monto_feriado": monto_feriado,
            "bruto": bruto,
            "mult_extra": mult_extra,
            "mult_sabado": Decimal("0"),
            "mult_domingo": Decimal("0"),
            "mult_feriado": mult_feriado,
            "dias_trabajados": dias_periodo - faltas,
            "sueldo_mensual": sueldo_periodo,
            "faltas": faltas,
            "descuento_faltas": descuento,
            "feriados_periodo": total_feriados,
            "feriados_trabajados": feriados_trabajados,
        }

    def _vacio(self):
        z = Decimal("0")
        return {
            "tipo_liquidacion": "por_hora",
            "valor_hora": z, "hs_normales": z, "hs_extra": z,
            "hs_sabado": z, "hs_domingo": z, "hs_feriado": z,
            "monto_normales": z, "monto_extra": z, "monto_sabado": z,
            "monto_domingo": z, "monto_feriado": z, "bruto": z,
            "mult_extra": z, "mult_sabado": z, "mult_domingo": z,
            "mult_feriado": z, "dias_trabajados": 0,
            "sueldo_mensual": z, "faltas": 0, "descuento_faltas": z,
        }


calculo_asistencia_service = CalculoAsistenciaService()
