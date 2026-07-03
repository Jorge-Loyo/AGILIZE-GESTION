"""Import all models so SQLAlchemy relationships resolve correctly."""
from models.base import Base  # noqa
from models.rol import Rol  # noqa
from models.usuario import Usuario  # noqa
from models.sucursal import Sucursal  # noqa
from models.empleado import Empleado  # noqa
from models.asistencia import Asistencia  # noqa
from models.nomina import ConceptoNomina, Liquidacion, LiquidacionDetalle  # noqa
from models.adelanto import Adelanto  # noqa
from models.cierre import CierreAsistencia  # noqa
from models.vacaciones import Vacaciones  # noqa
from models.historico_sueldo import HistoricoSueldo  # noqa
from models.permiso import Permiso  # noqa
from models.empresa import DatosEmpresa  # noqa
from models.audit_log import AuditLog  # noqa
from models.sac import SACRegistro, SACLiquidacion  # noqa
from models.aprobacion_extras import AprobacionExtras  # noqa
from models.config_nomina import ConfigNomina  # noqa
