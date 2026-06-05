from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base, TimestampMixin
from decimal import Decimal


class ConfigNomina(Base, TimestampMixin):
    """Parámetros globales de liquidación."""
    __tablename__ = "config_nomina"

    id: Mapped[int] = mapped_column(primary_key=True)
    clave: Mapped[str] = mapped_column(String(50), unique=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    descripcion: Mapped[str] = mapped_column(String(200), default="")


# Claves predefinidas:
# mult_hora_extra       -> multiplicador hora extra (ej: 1.5 = 50% más)
# mult_hora_feriado     -> multiplicador hora feriado (ej: 2.0 = 100% más)
# mult_hora_sabado      -> multiplicador hora sábado (ej: 1.5)
# mult_hora_domingo     -> multiplicador hora domingo (ej: 2.0)
