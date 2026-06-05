from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.empleado import Empleado, Departamento, Cargo


class EmpleadoService:
    def listar(self, busqueda: str = "", solo_activos: bool = True) -> list[Empleado]:
        with get_db() as db:
            query = db.query(Empleado).options(joinedload(Empleado.departamento), joinedload(Empleado.cargo))
            if solo_activos:
                query = query.filter(Empleado.activo == True)
            if busqueda:
                filtro = f"%{busqueda}%"
                query = query.filter(
                    or_(
                        Empleado.nombre.ilike(filtro),
                        Empleado.apellido.ilike(filtro),
                        Empleado.dni.ilike(filtro),
                        Empleado.cuil.ilike(filtro),
                    )
                )
            return query.order_by(Empleado.apellido, Empleado.nombre).all()

    def obtener(self, empleado_id: int) -> Empleado | None:
        with get_db() as db:
            return (
                db.query(Empleado)
                .options(joinedload(Empleado.departamento), joinedload(Empleado.cargo))
                .get(empleado_id)
            )

    def crear(self, datos: dict) -> Empleado:
        with get_db() as db:
            # Generar legajo si no tiene
            if not datos.get("legajo"):
                count = db.query(Empleado).count()
                datos["legajo"] = str(count + 1)
            empleado = Empleado(**datos)
            db.add(empleado)
            db.flush()
            db.refresh(empleado)
        from services.audit_service import registrar_auditoria
        registrar_auditoria("CREATE", "empleados", empleado.id, f"{empleado.apellido}, {empleado.nombre}")
        return empleado

    def actualizar(self, empleado_id: int, datos: dict) -> Empleado | None:
        with get_db() as db:
            empleado = db.query(Empleado).get(empleado_id)
            if not empleado:
                return None
            for key, value in datos.items():
                setattr(empleado, key, value)
            db.flush()
            db.refresh(empleado)
        from services.audit_service import registrar_auditoria
        registrar_auditoria("UPDATE", "empleados", empleado_id, f"Actualizado")
        return empleado

    def eliminar(self, empleado_id: int) -> bool:
        """Baja lógica (no borra de la BD)."""
        with get_db() as db:
            empleado = db.query(Empleado).get(empleado_id)
            if not empleado:
                return False
            empleado.activo = False
        from services.audit_service import registrar_auditoria
        registrar_auditoria("DELETE", "empleados", empleado_id, "Baja logica")
        return True

    def listar_departamentos(self) -> list[Departamento]:
        with get_db() as db:
            return db.query(Departamento).filter(Departamento.activo == True).order_by(Departamento.nombre).all()

    def listar_cargos(self) -> list[Cargo]:
        with get_db() as db:
            return db.query(Cargo).filter(Cargo.activo == True).order_by(Cargo.nombre).all()

    def crear_departamento(self, nombre: str) -> Departamento:
        with get_db() as db:
            dep = Departamento(nombre=nombre)
            db.add(dep)
            db.flush()
            db.refresh(dep)
            return dep

    def crear_cargo(self, nombre: str) -> Cargo:
        with get_db() as db:
            cargo = Cargo(nombre=nombre)
            db.add(cargo)
            db.flush()
            db.refresh(cargo)
            return cargo


empleado_service = EmpleadoService()
