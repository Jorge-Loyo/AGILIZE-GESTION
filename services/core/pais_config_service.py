"""Configuracion centralizada por pais. Define monedas, conceptos de nomina y labels."""
from decimal import Decimal
from services.core.empresa_service import empresa_service

# Definicion de paises soportados
PAISES = {
    "venezuela": {
        "nombre": "Venezuela",
        "moneda_local": "Bs.",
        "moneda_extranjera": "USD",
        "simbolo_local": "Bs.",
        "simbolo_extranjero": "$",
        "iva": Decimal("16.00"),
        "id_fiscal_empresa": "RIF",
        "id_fiscal_persona": "C.I.",
        "id_fiscal_label": "RIF",
        "conceptos_nomina": [
            {"codigo": "SAL_COMP", "nombre": "Salario Complementario", "tipo": "haber", "categoria": "no_remunerativo", "calculo": "fijo", "base_calculo": "basico", "porcentaje": None, "monto_fijo": None, "aplica_a": "empleado", "orden": 1},
            {"codigo": "BONO_GUERRA", "nombre": "Bono de Guerra Complementario", "tipo": "haber", "categoria": "no_remunerativo", "calculo": "fijo", "base_calculo": "basico", "porcentaje": None, "monto_fijo": None, "aplica_a": "empleado", "orden": 2},
            {"codigo": "REEMBOLSO", "nombre": "Reembolso", "tipo": "haber", "categoria": "no_remunerativo", "calculo": "fijo", "base_calculo": "basico", "porcentaje": None, "monto_fijo": None, "aplica_a": "todos", "orden": 3},
            {"codigo": "TIEMPO_VIAJE", "nombre": "Tiempo de Viaje", "tipo": "haber", "categoria": "no_remunerativo", "calculo": "fijo", "base_calculo": "basico", "porcentaje": None, "monto_fijo": None, "aplica_a": "todos", "orden": 4},
            {"codigo": "SSO", "nombre": "Seguro Social Obligatorio (SSO)", "tipo": "deduccion", "categoria": "retencion", "calculo": "porcentaje", "base_calculo": "salario_legal", "porcentaje": Decimal("1.8462"), "monto_fijo": None, "aplica_a": "empleado", "orden": 10},
            {"codigo": "PARO", "nombre": "Paro Forzoso", "tipo": "deduccion", "categoria": "retencion", "calculo": "porcentaje", "base_calculo": "salario_legal", "porcentaje": Decimal("0.4615"), "monto_fijo": None, "aplica_a": "empleado", "orden": 11},
            {"codigo": "FAOV", "nombre": "Ahorro Habitacional (FAOV)", "tipo": "deduccion", "categoria": "retencion", "calculo": "porcentaje", "base_calculo": "total_devengado", "porcentaje": Decimal("1.0000"), "monto_fijo": None, "aplica_a": "todos", "orden": 12},
            {"codigo": "ISLR_EMP", "nombre": "I.S.L.R. Empleados", "tipo": "deduccion", "categoria": "retencion", "calculo": "porcentaje", "base_calculo": "total_devengado", "porcentaje": Decimal("1.3300"), "monto_fijo": None, "aplica_a": "empleado", "orden": 13},
            {"codigo": "ISLR_DIR", "nombre": "I.S.L.R. Directivos", "tipo": "deduccion", "categoria": "retencion", "calculo": "porcentaje", "base_calculo": "total_devengado", "porcentaje": Decimal("2.6300"), "monto_fijo": None, "aplica_a": "directivo", "orden": 14},
            {"codigo": "PREST_1", "nombre": "Descuento por Prestamos (1)", "tipo": "deduccion", "categoria": "retencion", "calculo": "fijo", "base_calculo": "basico", "porcentaje": None, "monto_fijo": Decimal("0"), "aplica_a": "todos", "orden": 15},
            {"codigo": "PREST_2", "nombre": "Descuento por Prestamos (2)", "tipo": "deduccion", "categoria": "retencion", "calculo": "fijo", "base_calculo": "basico", "porcentaje": None, "monto_fijo": Decimal("0"), "aplica_a": "todos", "orden": 16},
            {"codigo": "OTRAS_DED", "nombre": "Otras Deducciones", "tipo": "deduccion", "categoria": "retencion", "calculo": "fijo", "base_calculo": "basico", "porcentaje": None, "monto_fijo": Decimal("0"), "aplica_a": "todos", "orden": 17},
        ],
    },
    "argentina": {
        "nombre": "Argentina",
        "moneda_local": "ARS",
        "moneda_extranjera": "USD",
        "simbolo_local": "$",
        "simbolo_extranjero": "US$",
        "iva": Decimal("21.00"),
        "id_fiscal_empresa": "CUIT",
        "id_fiscal_persona": "DNI",
        "id_fiscal_label": "CUIL",
        "conceptos_nomina": [
            {"codigo": "JUBILACION", "nombre": "Jubilacion", "tipo": "deduccion", "categoria": "retencion", "calculo": "porcentaje", "base_calculo": "basico", "porcentaje": Decimal("11.0000"), "monto_fijo": None, "aplica_a": "todos", "orden": 10},
            {"codigo": "LEY19032", "nombre": "Ley 19032 (PAMI)", "tipo": "deduccion", "categoria": "retencion", "calculo": "porcentaje", "base_calculo": "basico", "porcentaje": Decimal("3.0000"), "monto_fijo": None, "aplica_a": "todos", "orden": 11},
            {"codigo": "OBRA_SOCIAL", "nombre": "Obra Social", "tipo": "deduccion", "categoria": "retencion", "calculo": "porcentaje", "base_calculo": "basico", "porcentaje": Decimal("3.0000"), "monto_fijo": None, "aplica_a": "todos", "orden": 12},
            {"codigo": "SINDICATO", "nombre": "Cuota Sindical", "tipo": "deduccion", "categoria": "retencion", "calculo": "porcentaje", "base_calculo": "basico", "porcentaje": Decimal("2.0000"), "monto_fijo": None, "aplica_a": "todos", "orden": 13},
            {"codigo": "GANANCIAS", "nombre": "Impuesto a las Ganancias", "tipo": "deduccion", "categoria": "retencion", "calculo": "porcentaje", "base_calculo": "basico", "porcentaje": Decimal("0.0000"), "monto_fijo": None, "aplica_a": "todos", "orden": 14},
            {"codigo": "PRESENTISMO", "nombre": "Presentismo", "tipo": "haber", "categoria": "remunerativo", "calculo": "porcentaje", "base_calculo": "basico", "porcentaje": Decimal("8.3300"), "monto_fijo": None, "aplica_a": "todos", "orden": 1},
            {"codigo": "ANTIGUEDAD", "nombre": "Antiguedad", "tipo": "haber", "categoria": "remunerativo", "calculo": "porcentaje", "base_calculo": "basico", "porcentaje": Decimal("1.0000"), "monto_fijo": None, "aplica_a": "todos", "orden": 2},
        ],
    },
}


def moneda() -> str:
    """Helper rapido: retorna simbolo de moneda local. Usar en f-strings."""
    pais = (empresa_service.obtener("cotizacion_pais") or "argentina").lower().strip()
    return PAISES.get(pais, PAISES["argentina"])["simbolo_local"]


def moneda_ext() -> str:
    """Helper rapido: retorna simbolo de moneda extranjera."""
    pais = (empresa_service.obtener("cotizacion_pais") or "argentina").lower().strip()
    return PAISES.get(pais, PAISES["argentina"])["simbolo_extranjero"]


class PaisConfigService:
    """Servicio que retorna configuracion segun el pais seleccionado."""

    def get_pais(self) -> str:
        """Retorna el pais configurado (lowercase)."""
        pais = empresa_service.obtener("cotizacion_pais") or "argentina"
        return pais.lower().strip()

    def get_config(self) -> dict:
        """Retorna la config completa del pais actual."""
        return PAISES.get(self.get_pais(), PAISES["argentina"])

    def get_moneda_local(self) -> str:
        return self.get_config()["simbolo_local"]

    def get_moneda_extranjera(self) -> str:
        return self.get_config()["simbolo_extranjero"]

    def get_iva(self) -> Decimal:
        return self.get_config()["iva"]

    def get_id_fiscal_label(self) -> str:
        """Label para el campo de identificacion fiscal (CUIT/RIF)."""
        return self.get_config()["id_fiscal_empresa"]

    def get_id_persona_label(self) -> str:
        """Label para DNI/CI."""
        return self.get_config()["id_fiscal_persona"]

    def get_conceptos_nomina(self) -> list[dict]:
        """Retorna los conceptos de nomina predefinidos para el pais."""
        return self.get_config()["conceptos_nomina"]

    def aplicar_pais(self, pais: str):
        """Guarda el pais y seedea los conceptos de nomina correspondientes."""
        pais_lower = pais.lower().strip()
        if pais_lower not in PAISES:
            raise ValueError(f"Pais no soportado: {pais}")

        empresa_service.guardar("cotizacion_pais", pais.capitalize())
        self._seedear_conceptos(pais_lower)

    def _seedear_conceptos(self, pais: str):
        """Inserta/actualiza conceptos de nomina del pais en la BD."""
        from core.database import get_db
        from models.nomina import ConceptoNomina

        conceptos_pais = PAISES[pais]["conceptos_nomina"]

        with get_db() as db:
            for c in conceptos_pais:
                existente = db.query(ConceptoNomina).filter_by(codigo=c["codigo"]).first()
                if existente:
                    # Actualizar
                    existente.nombre = c["nombre"]
                    existente.tipo = c["tipo"]
                    existente.categoria = c["categoria"]
                    existente.calculo = c["calculo"]
                    existente.base_calculo = c["base_calculo"]
                    existente.porcentaje = c["porcentaje"]
                    existente.monto_fijo = c["monto_fijo"]
                    existente.aplica_a = c["aplica_a"]
                    existente.orden = c["orden"]
                    existente.activo = True
                else:
                    db.add(ConceptoNomina(
                        codigo=c["codigo"], nombre=c["nombre"], tipo=c["tipo"],
                        categoria=c["categoria"], calculo=c["calculo"],
                        base_calculo=c["base_calculo"], porcentaje=c["porcentaje"],
                        monto_fijo=c["monto_fijo"], aplica_a=c["aplica_a"],
                        orden=c["orden"], activo=True,
                    ))

            # Desactivar conceptos que no son del pais actual
            codigos_pais = [c["codigo"] for c in conceptos_pais]
            otros = db.query(ConceptoNomina).filter(
                ConceptoNomina.codigo.notin_(codigos_pais)
            ).all()
            for o in otros:
                o.activo = False


pais_config_service = PaisConfigService()
