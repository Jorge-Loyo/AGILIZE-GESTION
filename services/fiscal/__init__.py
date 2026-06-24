"""Servicio fiscal: selecciona conector segun pais y expone API unificada."""
from services.fiscal.conectores import (
    ConectorFiscalBase, ConectorFiscalAR, ConectorFiscalVE, ConectorFiscalGenerico,
)
from services.core.empresa_service import empresa_service


class FiscalService:
    """Servicio que delega al conector del pais configurado."""

    def _get_conector(self) -> ConectorFiscalBase:
        pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
        if pais == "Argentina":
            return ConectorFiscalAR()
        elif pais == "Venezuela":
            return ConectorFiscalVE()
        return ConectorFiscalGenerico()

    def autorizar_factura(self, factura_id: int) -> dict:
        """Envia factura al fisco del pais configurado."""
        return self._get_conector().autorizar_factura(factura_id)

    def consultar_estado(self, factura_id: int) -> dict:
        """Consulta estado fiscal de una factura."""
        return self._get_conector().consultar_estado(factura_id)

    def generar_qr(self, factura_id: int) -> str:
        """Genera QR fiscal si el pais lo requiere."""
        return self._get_conector().generar_qr(factura_id)

    def pais_actual(self) -> str:
        return empresa_service.obtener("cotizacion_pais") or "Venezuela"

    def requiere_fiscal(self) -> bool:
        """Indica si el pais actual requiere conexion fiscal."""
        pais = self.pais_actual()
        return pais in ("Argentina", "Venezuela")


fiscal_service = FiscalService()
