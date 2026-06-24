from sqlalchemy.orm import joinedload
from core.database import get_db
from core.auth import hash_password
from models.usuario import Usuario
from models.rol import Rol


class AdminService:
    def listar_usuarios(self) -> list[Usuario]:
        with get_db() as db:
            return db.query(Usuario).options(joinedload(Usuario.rol)).order_by(Usuario.username).all()

    def crear_usuario(self, datos: dict) -> Usuario:
        with get_db() as db:
            datos["password_hash"] = hash_password(datos.pop("password"))
            usuario = Usuario(**datos)
            db.add(usuario)
            db.flush()
            db.refresh(usuario)
            return usuario

    def actualizar_usuario(self, usuario_id: int, datos: dict) -> Usuario | None:
        with get_db() as db:
            usuario = db.get(Usuario, usuario_id)
            if not usuario:
                return None
            if "password" in datos:
                pwd = datos.pop("password")
                if pwd:
                    usuario.password_hash = hash_password(pwd)
            for key, value in datos.items():
                setattr(usuario, key, value)
            db.flush()
            db.refresh(usuario)
            return usuario

    def desactivar_usuario(self, usuario_id: int) -> bool:
        with get_db() as db:
            usuario = db.get(Usuario, usuario_id)
            if not usuario:
                return False
            usuario.activo = not usuario.activo
            return True

    def listar_roles(self) -> list[Rol]:
        with get_db() as db:
            return db.query(Rol).filter(Rol.activo == True).order_by(Rol.nombre).all()

    def crear_rol(self, nombre: str, descripcion: str = "") -> Rol:
        with get_db() as db:
            rol = Rol(nombre=nombre, descripcion=descripcion)
            db.add(rol)
            db.flush()
            db.refresh(rol)
            return rol


admin_service = AdminService()
