"""Paquete de servicios de inventario - Fachada unificada."""
from services.inventario.catalogo_service import CatalogoService
from services.inventario.stock_service import StockService
from services.inventario.lotes_service import LotesService
from services.inventario.series_service import SeriesService
from services.inventario.toma_service import TomaService
from services.inventario.valorizacion_service import ValorizacionService
from services.inventario.alertas_service import AlertasService


class InventarioService(
    CatalogoService,
    StockService,
    LotesService,
    SeriesService,
    TomaService,
    ValorizacionService,
    AlertasService,
):
    """Fachada unificada de inventario. Hereda de sub-servicios cohesivos."""
    pass


inventario_service = InventarioService()
