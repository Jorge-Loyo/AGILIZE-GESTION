from decimal import Decimal
from datetime import date, datetime, timezone
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.nomina import ConceptoNomina, Liquidacion, LiquidacionDetalle
from models.empleado import Empleado
from models.sucursal import Sucursal  # noqa


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


class LiquidacionMasivaService:
    """Procesamiento masivo de nomina para toda la plantilla."""

    def liquidar_masivo(self, periodo: str, conceptos_ids: list = None, solo_tipo: str = None) -> dict:
        """
        Liquida toda la plantilla activa para un periodo.
        solo_tipo: 'por_hora' o 'mensual' (None = todos)
        Retorna resumen.
        """
        with get_db() as db:
            q = db.query(Empleado).filter(Empleado.activo.is_(True))
            if solo_tipo:
                q = q.filter(Empleado.tipo_liquidacion == solo_tipo)
            empleados = q.all()

        if not conceptos_ids:
            conceptos_ids = [c.id for c in nomina_service.listar_conceptos()]

        liquidados = 0
        errores = []
        total_neto = Decimal("0")

        for emp in empleados:
            try:
                basico = emp.sueldo_mensual if emp.tipo_liquidacion == "mensual" else Decimal("0")
                if emp.tipo_liquidacion == "por_hora":
                    from services.rrhh.calculo_asistencia_service import calculo_asistencia_service
                    calc = calculo_asistencia_service.calcular_bruto_periodo(emp.id, periodo)
                    basico = Decimal(str(calc.get("bruto", 0)))

                # Filtrar conceptos que aplican a este tipo
                conceptos_filtrados = self._filtrar_conceptos(conceptos_ids, emp.tipo_liquidacion)

                liq = nomina_service.liquidar(emp.id, periodo, basico, conceptos_filtrados)
                total_neto += liq.neto
                liquidados += 1
            except Exception as e:
                errores.append({"empleado": f"{emp.apellido}, {emp.nombre}", "error": str(e)})

        return {
            "periodo": periodo,
            "liquidados": liquidados,
            "errores": len(errores),
            "total_neto": float(total_neto),
            "detalle_errores": errores,
        }

    def _filtrar_conceptos(self, conceptos_ids: list, tipo_liquidacion: str) -> list:
        """Filtra conceptos que aplican al tipo de liquidacion del empleado."""
        with get_db() as db:
            conceptos = db.query(ConceptoNomina).filter(
                ConceptoNomina.id.in_(conceptos_ids),
                ConceptoNomina.activo.is_(True),
            ).all()
            return [
                c.id for c in conceptos
                if c.aplica_a == "todos" or c.aplica_a == tipo_liquidacion
            ]

    def generar_recibos_masivo(self, periodo: str) -> dict:
        """Genera PDF de recibos para todas las liquidaciones del periodo."""
        from services.rrhh.recibo_pdf_service import recibo_pdf_service
        liquidaciones = nomina_service.listar_liquidaciones(periodo=periodo)
        generados = 0
        for liq in liquidaciones:
            try:
                recibo_pdf_service.generar(liq.id)
                generados += 1
            except Exception:
                pass
        return {"periodo": periodo, "generados": generados, "total": len(liquidaciones)}

    def resumen_periodo(self, periodo: str) -> dict:
        """Resumen de un periodo liquidado."""
        liquidaciones = nomina_service.listar_liquidaciones(periodo=periodo)
        total_bruto = sum(float(l.total_haberes) for l in liquidaciones)
        total_deducciones = sum(float(l.total_deducciones) for l in liquidaciones)
        total_neto = sum(float(l.neto) for l in liquidaciones)
        return {
            "periodo": periodo,
            "empleados_liquidados": len(liquidaciones),
            "total_bruto": round(total_bruto, 2),
            "total_deducciones": round(total_deducciones, 2),
            "total_neto": round(total_neto, 2),
        }


liquidacion_masiva_service = LiquidacionMasivaService()
