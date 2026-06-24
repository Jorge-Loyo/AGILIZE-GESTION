"""Base compartida para sub-servicios de precios."""
from datetime import date, timezone, datetime, timedelta  # noqa: F401
from sqlalchemy import func  # noqa: F401
from core.database import get_db  # noqa: F401
from models import sucursal, usuario, empleado, rol, permiso  # noqa
from models.comercial_precios import (  # noqa: F401
    ListaPrecioVenta, ListaPrecioVentaItem, ReglaDescuento, TipoCambio,
)
from models.inventario import Producto  # noqa: F401


def _hoy() -> date:
    return datetime.now(timezone.utc).date()
