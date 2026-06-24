"""Servicio de precios venta - Re-export desde paquete modular."""
from services.precios import PreciosVentaService, precios_venta_service  # noqa: F401

__all__ = ["PreciosVentaService", "precios_venta_service"]
