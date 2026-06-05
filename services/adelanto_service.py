from datetime import date
from decimal import Decimal
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.adelanto import Adelanto
from models.asistencia import Asistencia
from models.empleado import Empleado


class AdelantoService:
    def listar(self, empleado_id: int | None = None) -> list[Adelanto]:
        with get_db() as db:
            query = db.query(Adelanto).options(joinedload(Adelanto.empleado))
            if empleado_id:
                query = query.filter(Adelanto.empleado_id == empleado_id)
            return query.order_by(Adelanto.fecha.desc()).all()

    def crear(self, empleado_id: int, monto: Decimal, cuotas: int, motivo: str) -> Adelanto:
        with get_db() as db:
            adelanto = Adelanto(
                empleado_id=empleado_id,
                fecha=date.today(),
                monto=monto,
                cuotas=max(cuotas, 1),
                cuotas_descontadas=0,
                monto_descontado=Decimal("0"),
                saldo_pendiente=monto,
                motivo=motivo,
                completado=False,
            )
            db.add(adelanto)
            db.flush()
            db.refresh(adelanto)
            return adelanto

    def saldo_pendiente_empleado(self, empleado_id: int) -> Decimal:
        with get_db() as db:
            adelantos = db.query(Adelanto).filter_by(
                empleado_id=empleado_id, completado=False
            ).all()
            return sum(a.saldo_pendiente for a in adelantos)

    def descontar_en_liquidacion(self, empleado_id: int) -> Decimal:
        """Descuenta una cuota de cada adelanto pendiente. Retorna total descontado."""
        total = Decimal("0")
        with get_db() as db:
            adelantos = db.query(Adelanto).filter_by(
                empleado_id=empleado_id, completado=False
            ).all()
            for a in adelantos:
                cuota = a.monto_cuota
                # Última cuota: ajustar al saldo pendiente
                if a.saldo_pendiente <= cuota:
                    cuota = a.saldo_pendiente
                    a.completado = True
                a.cuotas_descontadas += 1
                a.monto_descontado += cuota
                a.saldo_pendiente -= cuota
                total += cuota
            db.flush()
        return total

    def info_empleado_periodo(self, empleado_id: int, periodo: str) -> dict:
        """Calcula horas trabajadas y monto generado en un período para mostrar en adelantos."""
        anio, mes = int(periodo.split("-")[0]), int(periodo.split("-")[1])
        from datetime import date as d
        if mes == 12:
            desde = d(anio, mes, 1)
            hasta = d(anio + 1, 1, 1)
        else:
            desde = d(anio, mes, 1)
            hasta = d(anio, mes + 1, 1)

        with get_db() as db:
            registros = db.query(Asistencia).filter(
                Asistencia.empleado_id == empleado_id,
                Asistencia.fecha >= desde,
                Asistencia.fecha < hasta,
            ).all()

            horas_normales = sum(r.horas_normales for r in registros)
            horas_extra = sum(r.horas_extra for r in registros)

            emp = db.query(Empleado).get(empleado_id)
            valor_hora = emp.valor_hora if emp and emp.valor_hora else Decimal("0")

            monto_generado = (horas_normales + horas_extra) * valor_hora
            saldo_adelantos = self.saldo_pendiente_empleado(empleado_id)

        return {
            "horas_normales": horas_normales,
            "horas_extra": horas_extra,
            "horas_totales": horas_normales + horas_extra,
            "valor_hora": valor_hora,
            "monto_generado": monto_generado.quantize(Decimal("0.01")),
            "saldo_adelantos": saldo_adelantos,
        }

    def eliminar(self, adelanto_id: int) -> bool:
        with get_db() as db:
            adelanto = db.query(Adelanto).get(adelanto_id)
            if not adelanto:
                return False
            db.delete(adelanto)
            return True


adelanto_service = AdelantoService()
