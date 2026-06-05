from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base, TimestampMixin


class DatosEmpresa(Base, TimestampMixin):
    """Datos legales e informativos de la empresa."""
    __tablename__ = "datos_empresa"

    id: Mapped[int] = mapped_column(primary_key=True)
    clave: Mapped[str] = mapped_column(String(50), unique=True)
    valor: Mapped[str] = mapped_column(Text, default="")


# Claves:
# razon_social, cuit, direccion, telefono, email, localidad, provincia
# actividad, convenio_colectivo, nro_establecimiento
# nombre_app, logo_path
# dev_nombre, dev_email, dev_web
