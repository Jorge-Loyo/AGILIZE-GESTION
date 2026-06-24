from decimal import Decimal
from datetime import date
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.nomina import ConceptoNomina, Liquidacion, LiquidacionDetalle
from models.empleado import Empleado


class NominaService:
    def listar_conceptos(self, solo_activos: bool = True) -> list[ConceptoNomina]:
        with get_db() as db:
            query = db.query(ConceptoNomina)
            if solo_activos:
                query = query.filter(ConceptoNomina.activo == True)
            return query.order_by(ConceptoNomina.tipo, ConceptoNomina.nombre).all()

    def crear_concepto(self, datos: dict) -> ConceptoNomina:
        with get_db() as db:
            concepto = ConceptoNomina(**datos)
            db.add(concepto)
            db.flush()
            db.refresh(concepto)
            return concepto

    def listar_liquidaciones(self, periodo: str = "", empleado_id: int | None = None) -> list[Liquidacion]:
        with get_db() as db:
            query = db.query(Liquidacion).options(joinedload(Liquidacion.empleado))
            if periodo:
                query = query.filter(Liquidacion.periodo == periodo)
            if empleado_id:
                query = query.filter(Liquidacion.empleado_id == empleado_id)
            return query.order_by(Liquidacion.fecha_liquidacion.desc()).all()

    def liquidar(self, empleado_id: int, periodo: str, sueldo_basico: Decimal, conceptos_ids: list[int]) -> Liquidacion:
        from services.rrhh.cierre_service import cierre_service

        # Validar que no esté ya liquidado
        if cierre_service.liquidacion_cerrada(empleado_id, periodo):
            raise ValueError(f"El período {periodo} ya fue liquidado para este empleado.")

        with get_db() as db:
            conceptos = db.query(ConceptoNomina).filter(
                ConceptoNomina.id.in_(conceptos_ids),
                ConceptoNomina.activo == True,
            ).all()

            total_haberes = sueldo_basico
            total_deducciones = Decimal("0")
            detalles = []

            # Obtener dias trabajados para conceptos por_dia
            from services.rrhh.calculo_asistencia_service import calculo_asistencia_service
            calc_asist = calculo_asistencia_service.calcular_bruto_periodo(empleado_id, periodo)
            dias_trabajados = calc_asist["dias_trabajados"]

            for c in conceptos:
                if getattr(c, 'calculo', '') == "por_dia" and c.monto_fijo:
                    monto = c.monto_fijo * Decimal(str(dias_trabajados))
                elif c.porcentaje:
                    monto = sueldo_basico * c.porcentaje / Decimal("100")
                elif c.monto_fijo:
                    monto = c.monto_fijo
                else:
                    continue

                monto = monto.quantize(Decimal("0.01"))

                if c.tipo == "haber":
                    total_haberes += monto
                else:
                    total_deducciones += monto

                detalles.append(LiquidacionDetalle(
                    concepto_id=c.id,
                    tipo=c.tipo,
                    monto=monto,
                ))

            # Descontar adelantos pendientes
            from services.rrhh.adelanto_service import adelanto_service
            descuento_adelantos = adelanto_service.descontar_en_liquidacion(empleado_id)
            if descuento_adelantos > 0:
                total_deducciones += descuento_adelantos

            neto = total_haberes - total_deducciones

            liq = Liquidacion(
                empleado_id=empleado_id,
                periodo=periodo,
                fecha_liquidacion=date.today(),
                sueldo_basico=sueldo_basico,
                total_haberes=total_haberes,
                total_deducciones=total_deducciones,
                neto=neto,
                detalles=detalles,
            )
            db.add(liq)
            db.flush()
            db.refresh(liq)

            # Registrar remuneración bruta para SAC
            from services.rrhh.sac_service import sac_service
            sac_service.registrar_mes(empleado_id, periodo, total_haberes)

            # Cerrar liquidación del período
            cierre_service.cerrar_liquidacion(empleado_id, periodo)

            # Auditoria
            from services.core.audit_service import registrar_auditoria
            registrar_auditoria("LIQUIDAR", "liquidaciones", liq.id, f"Periodo {periodo} - Neto: {neto}")

            return liq


nomina_service = NominaService()
