"""Paquete de servicios de clientes - Fachada unificada."""
from services.clientes.crud_service import CrudClienteService
from services.clientes.direcciones_service import DireccionesContactosService
from services.clientes.credito_service import CreditoClienteService


class ClienteService(CrudClienteService, DireccionesContactosService, CreditoClienteService):
    """Fachada unificada de clientes."""
    pass


cliente_service = ClienteService()
