"""Base compartida para sub-servicios de clientes."""
from datetime import date, timezone, datetime  # noqa: F401
from sqlalchemy import func  # noqa: F401
from sqlalchemy.orm import joinedload  # noqa: F401
from core.database import get_db  # noqa: F401
from models.datos import Cliente, DireccionEntregaCliente, ContactoCliente  # noqa: F401


def _hoy() -> date:
    return datetime.now(timezone.utc).date()
