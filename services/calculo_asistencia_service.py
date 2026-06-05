from decimal import Decimal
from datetime import date
from core.database import get_db
from models.asistencia import Asistencia
from models.empleado import Empleado
from services.config_nomina_service import config_nomina_service


class CalculoAsistenciaService:
    def calcular_bruto_periodo(self, empleado_id: int, periodo: str) -> dict:
        """Calcula el sueldo bruto basado en asistencia real del período."""
        anio, mes = int(periodo.split("-")[0]), int(periodo.split("-")[1])
        if mes == 12:
            desde = date(anio, mes, 1)
            hasta = date(anio + 1, 1, 1)
        else:
            desde = date(anio, mes, 1)
            hasta = date(anio, mes + 1, 1)

        params = config_nomina_service.obtener_todos()
        mult_extra = params["mult_hora_extra"]
        mult_sabado = params["mult_hora_sabado"]
        mult_domingo = params["mult_hora_domingo"]
        mult_feriado = params["mult_hora_feriado"]

        with get_db() as db:
            emp = db.query(Empleado).get(empleado_id)
            if not emp:
                return self._vacio()

            valor_hora = emp.valor_hora or Decimal("0")
            valor_hora_extra = emp.valor_hora_extra if emp.valor_hora_extra else valor_hora

            registros = db.query(Asistencia).filter(
                Asistencia.empleado_id == empleado_id,
                Asistencia.fecha >= desde,
                Asistencia.fecha < hasta,
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
        }

    def _vacio(self):
        z = Decimal("0")
        return {
            "valor_hora": z, "hs_normales": z, "hs_extra": z,
            "hs_sabado": z, "hs_domingo": z, "hs_feriado": z,
            "monto_normales": z, "monto_extra": z, "monto_sabado": z,
            "monto_domingo": z, "monto_feriado": z, "bruto": z,
            "mult_extra": z, "mult_sabado": z, "mult_domingo": z,
            "mult_feriado": z, "dias_trabajados": 0,
        }


calculo_asistencia_service = CalculoAsistenciaService()
