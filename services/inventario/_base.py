"""Base compartida para sub-servicios de inventario."""
from datetime import date, timezone, datetime, timedelta  # noqa: F401
from sqlalchemy import func  # noqa: F401
from sqlalchemy.orm import joinedload  # noqa: F401
from core.database import get_db  # noqa: F401
from models import usuario, rol, permiso, empleado, sucursal  # noqa: resolver relationships
from models.inventario import (  # noqa: F401
    CategoriaProducto, SubcategoriaProducto, MarcaProducto,
    UnidadMedida, ConversionUOM, CodigoBarraProducto, KitDetalle,
    Producto, Deposito, UbicacionDeposito, StockDeposito, MovimientoStock,
    LoteProducto, NumeroSerie, TomaInventario, TomaInventarioDetalle,
)
from services.auth_service import auth_service  # noqa: F401


def _hoy() -> date:
    return datetime.now(timezone.utc).date()
