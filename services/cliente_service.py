"""Servicio de clientes - Re-export desde paquete modular."""
from services.clientes import ClienteService, cliente_service  # noqa: F401

__all__ = ["ClienteService", "cliente_service"]
