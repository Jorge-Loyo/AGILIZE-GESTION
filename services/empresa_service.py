from core.database import get_db
from models.empresa import DatosEmpresa


class EmpresaService:
    def obtener(self, clave: str) -> str:
        with get_db() as db:
            reg = db.query(DatosEmpresa).filter_by(clave=clave).first()
            return reg.valor if reg else ""

    def guardar(self, clave: str, valor: str):
        with get_db() as db:
            reg = db.query(DatosEmpresa).filter_by(clave=clave).first()
            if reg:
                reg.valor = valor
            else:
                db.add(DatosEmpresa(clave=clave, valor=valor))

    def obtener_todos(self) -> dict[str, str]:
        with get_db() as db:
            regs = db.query(DatosEmpresa).all()
            return {r.clave: r.valor for r in regs}

    def guardar_multiples(self, datos: dict[str, str]):
        for clave, valor in datos.items():
            self.guardar(clave, valor)


empresa_service = EmpresaService()
