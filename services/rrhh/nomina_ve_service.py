"""Servicio de liquidación dual (Bs/USD) para Casa Dulce Venezuela."""
from decimal import Decimal
from datetime import date
from core.database import get_db
from core.logging_config import logger
from models.empleado import Empleado
from models.liquidacion_dual import LiquidacionDual
from models.historial_dolar import HistorialDolar


class NominaVEService:

    def obtener_tasas_disponibles(self, periodo: str) -> list[dict]:
        """Retorna fechas+valores del historial_dolar del mes del periodo (YYYY-MM)."""
        año, mes = int(periodo[:4]), int(periodo[5:7])
        with get_db() as db:
            registros = db.query(HistorialDolar).filter(
                HistorialDolar.pais == "venezuela",
                HistorialDolar.fecha >= date(año, mes, 1),
                HistorialDolar.fecha <= date(año, mes + 1, 1) if mes < 12 else date(año + 1, 1, 1),
            ).order_by(HistorialDolar.fecha.desc()).all()
            return [{"fecha": r.fecha, "valor": r.valor} for r in registros]

    def calcular_preview(self, empleado_id: int, tasa_bcv: Decimal,
                         faltas: int = 0, bono_override: Decimal | None = None) -> dict:
        """Calcula preview sin guardar."""
        with get_db() as db:
            emp = db.query(Empleado).get(empleado_id)
            if not emp or emp.pago_total_usd <= 0:
                raise ValueError("Empleado sin configuración de pago dual USD")

            sueldo_legal_bs = emp.sueldo_mensual
            pago_total_usd = emp.pago_total_usd
            canasta_usd = emp.canasta_usd
            bono_usd = bono_override if bono_override is not None else emp.bono_empresa_usd

            sueldo_legal_usd = (sueldo_legal_bs / tasa_bcv).quantize(Decimal("0.0001"))
            complemento_usd = (pago_total_usd - canasta_usd - bono_usd - sueldo_legal_usd).quantize(Decimal("0.0001"))
            descuento_falta_dia = (pago_total_usd / Decimal("30")).quantize(Decimal("0.0001"))
            descuento_faltas_usd = (descuento_falta_dia * faltas).quantize(Decimal("0.0001"))

            neto_nomina_usd = (sueldo_legal_usd + complemento_usd + bono_usd - descuento_faltas_usd).quantize(Decimal("0.01"))
            neto_total_usd = (neto_nomina_usd + canasta_usd).quantize(Decimal("0.01"))
            neto_total_bs = (neto_total_usd * tasa_bcv).quantize(Decimal("0.01"))

            return {
                "sueldo_legal_bs": sueldo_legal_bs,
                "tasa_bcv": tasa_bcv,
                "sueldo_legal_usd": sueldo_legal_usd,
                "complemento_usd": complemento_usd,
                "bono_usd": bono_usd,
                "canasta_usd": canasta_usd,
                "faltas": faltas,
                "descuento_faltas_usd": descuento_faltas_usd,
                "neto_nomina_usd": neto_nomina_usd,
                "neto_total_usd": neto_total_usd,
                "neto_total_bs": neto_total_bs,
                "pago_total_usd": pago_total_usd,
            }

    def liquidar_dual(self, empleado_id: int, periodo: str, fecha_tasa: date,
                      tasa_bcv: Decimal, faltas: int = 0,
                      bono_override: Decimal | None = None,
                      conceptos_ids: list[int] | None = None) -> LiquidacionDual:
        """Genera liquidación legal (Bs) + dual (USD)."""
        from services.rrhh.nomina_service import nomina_service

        preview = self.calcular_preview(empleado_id, tasa_bcv, faltas, bono_override)

        # 1. Liquidación legal en Bs (sueldo_mensual - descuento faltas proporcional)
        sueldo_legal_bs = preview["sueldo_legal_bs"]
        descuento_legal_bs = Decimal("0")
        if faltas > 0:
            descuento_legal_bs = (sueldo_legal_bs / Decimal("30") * faltas).quantize(Decimal("0.01"))
        basico_legal = sueldo_legal_bs - descuento_legal_bs

        liquidacion_legal_id = None
        deducciones_legal_bs = Decimal("0")
        try:
            liq_legal = nomina_service.liquidar(
                empleado_id, periodo, basico_legal,
                conceptos_ids or [], tasa_cambio=tasa_bcv
            )
            liquidacion_legal_id = liq_legal.id
            deducciones_legal_bs = liq_legal.total_deducciones
        except Exception as e:
            logger.warning(f"Liquidación legal falló (se continúa con dual): {e}")

        deducciones_legal_usd = (deducciones_legal_bs / tasa_bcv).quantize(Decimal("0.0001")) if deducciones_legal_bs else Decimal("0")

        # 2. Guardar liquidación dual
        with get_db() as db:
            emp = db.query(Empleado).get(empleado_id)
            dual = LiquidacionDual(
                liquidacion_legal_id=liquidacion_legal_id,
                empleado_id=empleado_id,
                periodo=periodo,
                fecha=date.today(),
                tasa_bcv=tasa_bcv,
                fecha_tasa=fecha_tasa,
                sueldo_legal_bs=preview["sueldo_legal_bs"],
                pago_total_usd=preview["pago_total_usd"],
                canasta_usd=preview["canasta_usd"],
                bono_empresa_usd=preview["bono_usd"],
                sueldo_legal_usd=preview["sueldo_legal_usd"],
                complemento_usd=preview["complemento_usd"],
                faltas=faltas,
                descuento_faltas_usd=preview["descuento_faltas_usd"],
                deducciones_legal_bs=deducciones_legal_bs,
                deducciones_legal_usd=deducciones_legal_usd,
                neto_nomina_usd=preview["neto_nomina_usd"],
                neto_total_usd=preview["neto_total_usd"],
                neto_total_bs=preview["neto_total_bs"],
            )
            db.add(dual)
            db.flush()
            db.refresh(dual)

            from services.core.audit_service import registrar_auditoria
            registrar_auditoria("LIQUIDAR_DUAL", "liquidaciones_dual", dual.id,
                                f"Periodo {periodo} - Neto USD: {dual.neto_total_usd}")
            return dual

    def listar_duales(self, periodo: str = "", empleado_id: int | None = None) -> list[LiquidacionDual]:
        with get_db() as db:
            q = db.query(LiquidacionDual)
            if periodo:
                q = q.filter(LiquidacionDual.periodo == periodo)
            if empleado_id:
                q = q.filter(LiquidacionDual.empleado_id == empleado_id)
            return q.order_by(LiquidacionDual.fecha.desc()).all()

    def obtener_dual(self, dual_id: int) -> LiquidacionDual | None:
        with get_db() as db:
            return db.query(LiquidacionDual).get(dual_id)

    def es_dual(self, empleado_id: int) -> bool:
        """Retorna True si el empleado tiene configuración de pago dual."""
        with get_db() as db:
            emp = db.query(Empleado).get(empleado_id)
            return emp is not None and emp.pago_total_usd > 0


nomina_ve_service = NominaVEService()
