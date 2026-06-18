import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Agregar raiz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import settings
from models.base import Base
from models.usuario import Usuario  # noqa: F401
from models.rol import Rol  # noqa: F401
from models.permiso import Modulo, Permiso, RolPermiso, UsuarioPermiso  # noqa: F401
from models.audit_log import AuditLog  # noqa: F401
from models.empleado import Empleado, Departamento, Cargo  # noqa: F401
from models.nomina import ConceptoNomina, Liquidacion, LiquidacionDetalle  # noqa: F401
from models.asistencia import Asistencia, Feriado  # noqa: F401
from models.adelanto import Adelanto  # noqa: F401
from models.sac import SACRegistro, SACLiquidacion  # noqa: F401
from models.cierre import CierreAsistencia, CierreLiquidacion  # noqa: F401
from models.config_nomina import ConfigNomina  # noqa: F401
from models.permiso_empleado import TipoPermiso, PermisoEmpleado, Ausencia  # noqa: F401
from models.empresa import DatosEmpresa  # noqa: F401
from models.sucursal import Sucursal  # noqa: F401
from models.historico_sueldo import HistoricoSueldo  # noqa: F401
from models.vacaciones import Vacaciones  # noqa: F401
from models.aprobacion_extras import AprobacionExtras  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name, encoding="utf-8")
    except Exception:
        pass

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
