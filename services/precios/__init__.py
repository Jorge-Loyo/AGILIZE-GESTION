"""Paquete de servicios de precios - Fachada unificada."""
from services.precios.listas_service import ListasPrecioService
from services.precios.descuentos_service import DescuentosService
from services.precios.moneda_service import MonedaService


class PreciosVentaService(ListasPrecioService, DescuentosService, MonedaService):
    """Fachada unificada de precios de venta."""
    pass


precios_venta_service = PreciosVentaService()
