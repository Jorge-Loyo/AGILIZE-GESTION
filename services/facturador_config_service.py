"""Servicio de configuracion de facturadores."""
from core.database import get_db
from models.facturador import ConfigFacturador


class FacturadorConfigService:
    def listar(self):
        with get_db() as db:
            return db.query(ConfigFacturador).filter(ConfigFacturador.activo == True).order_by(ConfigFacturador.codigo).all()

    def obtener_por_codigo(self, codigo: str):
        with get_db() as db:
            return db.query(ConfigFacturador).filter(
                ConfigFacturador.codigo == codigo.upper(),
                ConfigFacturador.activo == True
            ).first()

    def crear(self, codigo: str, nombre: str, sucursal_id: int = None, depositos_ids: str = ""):
        with get_db() as db:
            f = ConfigFacturador(
                codigo=codigo.upper(), nombre=nombre,
                sucursal_id=sucursal_id, depositos_ids=depositos_ids
            )
            db.add(f)
            db.flush()
            return f

    def actualizar(self, facturador_id: int, datos: dict):
        with get_db() as db:
            f = db.get(ConfigFacturador, facturador_id)
            if not f:
                raise ValueError("Facturador no encontrado")
            for k, v in datos.items():
                setattr(f, k, v)

    def get_depositos_ids(self, config: ConfigFacturador) -> list:
        """Retorna lista de IDs de depositos asignados."""
        if not config or not config.depositos_ids:
            return []
        return [int(x.strip()) for x in config.depositos_ids.split(",") if x.strip().isdigit()]


facturador_config_service = FacturadorConfigService()
