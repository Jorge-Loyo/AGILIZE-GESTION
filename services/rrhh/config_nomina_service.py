from decimal import Decimal
from core.database import get_db
from models.config_nomina import ConfigNomina

DEFAULTS = {
    "mult_hora_extra": (Decimal("1.50"), "Multiplicador hora extra (ej: 1.50 = 50% mas)"),
    "mult_hora_sabado": (Decimal("1.50"), "Multiplicador hora sabado"),
    "mult_hora_domingo": (Decimal("2.00"), "Multiplicador hora domingo"),
    "mult_hora_feriado": (Decimal("2.00"), "Multiplicador hora feriado trabajado"),
    "mult_feriado_no_trabajado": (Decimal("1.00"), "Multiplicador feriado no trabajado"),
}


class ConfigNominaService:
    def obtener(self, clave: str) -> Decimal:
        with get_db() as db:
            config = db.query(ConfigNomina).filter_by(clave=clave).first()
            if config:
                return config.valor
        return DEFAULTS.get(clave, (Decimal("1"), ""))[0]

    def obtener_todos(self) -> dict[str, Decimal]:
        resultado = {}
        with get_db() as db:
            configs = db.query(ConfigNomina).all()
            for c in configs:
                resultado[c.clave] = c.valor
        # Rellenar defaults faltantes
        for clave, (valor, _) in DEFAULTS.items():
            if clave not in resultado:
                resultado[clave] = valor
        return resultado

    def guardar(self, clave: str, valor: Decimal, descripcion: str = "") -> ConfigNomina:
        with get_db() as db:
            config = db.query(ConfigNomina).filter_by(clave=clave).first()
            if config:
                config.valor = valor
                if descripcion:
                    config.descripcion = descripcion
            else:
                desc = descripcion or DEFAULTS.get(clave, (None, ""))[1]
                config = ConfigNomina(clave=clave, valor=valor, descripcion=desc)
                db.add(config)
            db.flush()
            db.refresh(config)
            return config

    def inicializar_defaults(self):
        for clave, (valor, desc) in DEFAULTS.items():
            with get_db() as db:
                existente = db.query(ConfigNomina).filter_by(clave=clave).first()
                if not existente:
                    db.add(ConfigNomina(clave=clave, valor=valor, descripcion=desc))


config_nomina_service = ConfigNominaService()
