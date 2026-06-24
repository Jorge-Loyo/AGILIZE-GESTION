"""Servicio de inventario - Re-export desde paquete modular."""
from services.inventario import InventarioService, inventario_service  # noqa: F401

__all__ = ["InventarioService", "inventario_service"]
