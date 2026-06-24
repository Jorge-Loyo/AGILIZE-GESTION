from decimal import Decimal
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.sac import SACRegistro, SACLiquidacion
from models.empleado import Empleado


class SACService:
    def registrar_mes(self, empleado_id: int, periodo: str, remuneracion_bruta: Decimal):
        """Registra la remuneración bruta de un mes para el cálculo de SAC."""
        anio = int(periodo.split("-")[0])
        mes = int(periodo.split("-")[1])
        semestre = 1 if mes <= 6 else 2

        with get_db() as db:
            existente = db.query(SACRegistro).filter_by(
                empleado_id=empleado_id, periodo=periodo
            ).first()
            if existente:
                existente.remuneracion_bruta = remuneracion_bruta
            else:
                db.add(SACRegistro(
                    empleado_id=empleado_id,
                    periodo=periodo,
                    semestre=semestre,
                    anio=anio,
                    remuneracion_bruta=remuneracion_bruta,
                ))

    def obtener_acumulado(self, empleado_id: int, anio: int, semestre: int) -> list[SACRegistro]:
        with get_db() as db:
            return (
                db.query(SACRegistro)
                .filter_by(empleado_id=empleado_id, anio=anio, semestre=semestre)
                .order_by(SACRegistro.periodo)
                .all()
            )

    def calcular_sac(self, empleado_id: int, anio: int, semestre: int, metodo: str) -> dict:
        """
        Calcula SAC según método:
        - "mayor": 50% de la mayor remuneración del semestre
        - "promedio": 50% del promedio de los 6 meses
        """
        registros = self.obtener_acumulado(empleado_id, anio, semestre)
        if not registros:
            return {"base": Decimal("0"), "monto_sac": Decimal("0"), "meses": 0}

        remuneraciones = [r.remuneracion_bruta for r in registros]
        meses = len(remuneraciones)

        if metodo == "mayor":
            base = max(remuneraciones)
        else:  # promedio
            base = sum(remuneraciones) / len(remuneraciones)

        # Proporcional si no tiene los 6 meses
        monto_sac = (base / 2) * Decimal(str(meses)) / Decimal("6")
        monto_sac = monto_sac.quantize(Decimal("0.01"))

        return {"base": base, "monto_sac": monto_sac, "meses": meses}

    def liquidar_sac(self, empleado_id: int, anio: int, semestre: int, metodo: str) -> SACLiquidacion:
        resultado = self.calcular_sac(empleado_id, anio, semestre, metodo)

        with get_db() as db:
            liq = SACLiquidacion(
                empleado_id=empleado_id,
                semestre=semestre,
                anio=anio,
                metodo=metodo,
                base_calculo=resultado["base"],
                monto_sac=resultado["monto_sac"],
            )
            db.add(liq)
            db.flush()
            db.refresh(liq)
            return liq

    def listar_liquidaciones_sac(self, anio: int | None = None) -> list[SACLiquidacion]:
        with get_db() as db:
            query = db.query(SACLiquidacion).options(joinedload(SACLiquidacion.empleado))
            if anio:
                query = query.filter(SACLiquidacion.anio == anio)
            return query.order_by(SACLiquidacion.anio.desc(), SACLiquidacion.semestre.desc()).all()

    def listar_empleados_activos(self) -> list[Empleado]:
        with get_db() as db:
            return db.query(Empleado).filter(Empleado.activo == True).order_by(Empleado.apellido).all()


sac_service = SACService()
