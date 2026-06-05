from sqlalchemy.orm import Session
from core.auth import verify_password
from core.database import get_db
from models.usuario import Usuario
from models.rol import Rol
from models.permiso import Modulo, Permiso, RolPermiso, UsuarioPermiso


class AuthService:
    def __init__(self):
        self.current_user: Usuario | None = None
        self.permisos: dict[str, list[str]] = {}  # {"empleados": ["ver", "crear", ...]}

    def login(self, username: str, password: str) -> tuple[bool, str]:
        with get_db() as db:
            user = db.query(Usuario).filter_by(username=username, activo=True).first()
            if not user:
                return False, "Usuario no encontrado"
            if not verify_password(password, user.password_hash):
                return False, "Contraseña incorrecta"

            self.current_user = user
            self._cargar_permisos(db, user)

        from services.audit_service import registrar_auditoria
        registrar_auditoria("LOGIN", "usuarios", user.id, f"Login: {username}")
        return True, "Login exitoso"

    def _cargar_permisos(self, db: Session, user: Usuario):
        """Carga permisos del rol + overrides del usuario."""
        self.permisos = {}

        # Permisos del rol
        rol_perms = (
            db.query(Permiso, Modulo)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .join(Modulo, Modulo.id == Permiso.modulo_id)
            .filter(RolPermiso.rol_id == user.rol_id, Modulo.activo == True)
            .all()
        )
        for permiso, modulo in rol_perms:
            self.permisos.setdefault(modulo.codigo, []).append(permiso.accion)

        # Overrides del usuario
        overrides = (
            db.query(UsuarioPermiso, Permiso, Modulo)
            .join(Permiso, Permiso.id == UsuarioPermiso.permiso_id)
            .join(Modulo, Modulo.id == Permiso.modulo_id)
            .filter(UsuarioPermiso.usuario_id == user.id)
            .all()
        )
        for override, permiso, modulo in overrides:
            if override.concedido:
                self.permisos.setdefault(modulo.codigo, []).append(permiso.accion)
            else:
                if modulo.codigo in self.permisos:
                    try:
                        self.permisos[modulo.codigo].remove(permiso.accion)
                    except ValueError:
                        pass

    def tiene_permiso(self, modulo: str, accion: str) -> bool:
        return accion in self.permisos.get(modulo, [])

    def modulos_accesibles(self) -> list[str]:
        return [m for m, acciones in self.permisos.items() if "ver" in acciones]

    def logout(self):
        self.current_user = None
        self.permisos = {}


auth_service = AuthService()
