import sys
from core.logging_config import logger


class AppController:
    def __init__(self):
        from PySide6.QtWidgets import QApplication, QMessageBox, QLabel, QVBoxLayout
        from PySide6.QtGui import QIcon
        from core.config import settings
        from ui.theme_manager import theme_manager
        from services.logo_service import get_app_icon_path

        # Windows: forzar que el icono se muestre en la barra de tareas
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('agilize.gestion.app')
        except Exception:
            pass

        self.app = QApplication(sys.argv)
        self.app.setApplicationName(settings.APP_NAME)
        self.app.setApplicationVersion(settings.APP_VERSION)
        self.app.setQuitOnLastWindowClosed(False)

        # Icono de la aplicacion
        logo = get_app_icon_path()
        if logo:
            self.app.setWindowIcon(QIcon(logo))

        theme_manager.apply(self.app, theme_manager.DARK)

        # Verificar conexion a BD
        try:
            from core.database import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as e:
            from PySide6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox
            error_msg = str(e)
            dlg = QDialog()
            dlg.setWindowTitle("Error de Conexion - Agilize Gestion")
            dlg.setMinimumSize(600, 350)
            lay = QVBoxLayout(dlg)
            lay.addWidget(QLabel(
                "No se pudo conectar a la base de datos.\n"
                "Verifica que PostgreSQL este corriendo.\n"
            ))
            txt = QTextEdit()
            txt.setPlainText(error_msg)
            txt.setReadOnly(True)
            txt.setStyleSheet("font-family: Consolas; font-size: 11px;")
            lay.addWidget(txt)
            btns = QDialogButtonBox(QDialogButtonBox.Ok)
            btns.accepted.connect(dlg.accept)
            lay.addWidget(btns)
            dlg.exec()
            sys.exit(1)

        self._login_window = None
        self._main_window = None

    def run(self):
        self._show_login()
        sys.exit(self.app.exec())

    def _show_login(self):
        from ui.login_view import LoginView

        if self._main_window:
            self._main_window.close()
            self._main_window = None

        self._login_window = LoginView()
        self._login_window.login_success.connect(self._on_login_success)
        self._login_window.show()

    def _on_login_success(self):
        from ui.main_window import MainWindow

        self._login_window.close()
        self._login_window = None

        self._main_window = MainWindow()
        self._main_window.showMaximized()
        self._main_window.logout_signal.connect(self._show_login)


def _run_seed():
    """Crea datos iniciales: roles, permisos y usuario master."""
    try:
        from core.database import get_db, engine
        from core.auth import hash_password
        from models.rol import Rol
        from models.usuario import Usuario
        from models.permiso import Modulo, Permiso, RolPermiso

        with get_db() as db:
            # Verificar si ya hay datos
            if db.query(Rol).first():
                return

            # Rol admin
            rol_admin = Rol(nombre="Administrador", descripcion="Acceso total al sistema")
            db.add(rol_admin)
            db.flush()

            # Modulos y permisos
            modulos = [
                {"codigo": "empleados", "nombre": "Gestion de Empleados", "icono": "people", "orden": 1},
                {"codigo": "nomina", "nombre": "Nomina y Liquidaciones", "icono": "payments", "orden": 2},
                {"codigo": "admin", "nombre": "Administracion del Sistema", "icono": "settings", "orden": 99},
            ]
            for m in modulos:
                modulo = Modulo(**m)
                db.add(modulo)
                db.flush()
                for accion in ["ver", "crear", "editar", "eliminar", "exportar"]:
                    permiso = Permiso(modulo_id=modulo.id, accion=accion)
                    db.add(permiso)
                    db.flush()
                    db.add(RolPermiso(rol_id=rol_admin.id, permiso_id=permiso.id))

            # Usuario master
            master = Usuario(
                username="master",
                password_hash=hash_password("master2025"),
                nombre_completo="Administrador",
                email="admin@agilize.com",
                rol_id=rol_admin.id,
            )
            db.add(master)

        # Configurar password de desarrollador por defecto
        try:
            from services.empresa_service import empresa_service
            if not empresa_service.obtener("dev_password"):
                empresa_service.guardar("dev_password", "agilize2025")
        except Exception:
            pass

        logger.info("Seed completado: usuario master creado")
    except Exception as e:
        logger.error(f"Error en seed: {e}")


def main():
    logger.info("Iniciando Agilize Gestion")

    # Iniciar PostgreSQL portable si existe
    try:
        from scripts.pg_launcher import start_postgres_if_needed
        start_postgres_if_needed()
    except Exception:
        pass

    # Auto-migrar BD al iniciar
    try:
        from alembic.config import Config
        from alembic import command
        from core.config import BASE_DIR
        import configparser

        ini_path = str(BASE_DIR / "alembic.ini")
        alembic_cfg = Config(ini_path)
        alembic_cfg.config_file_name = ini_path
        alembic_cfg.file_config = configparser.ConfigParser()
        with open(ini_path, "r", encoding="utf-8") as f:
            alembic_cfg.file_config.read_file(f)
        alembic_cfg.set_main_option("script_location", str(BASE_DIR / "alembic"))
        from core.config import settings
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        logger.warning(f"Auto-migracion fallo: {e}")
        # Fallback: crear tablas directamente si no existen
        try:
            from core.database import engine
            from sqlalchemy import inspect, text
            inspector = inspect(engine)
            if "usuarios" not in inspector.get_table_names():
                logger.info("Creando tablas desde modelos...")
                from models.base import Base
                from models import usuario, rol, permiso, audit_log, empleado  # noqa
                from models import nomina, asistencia, adelanto, sac, cierre  # noqa
                from models import config_nomina, permiso_empleado, empresa  # noqa
                from models import sucursal, historico_sueldo, vacaciones  # noqa
                from models import aprobacion_extras  # noqa
                Base.metadata.create_all(engine)
                logger.info("Tablas creadas. Ejecutando seed...")
                _run_seed()
        except Exception as e2:
            logger.error(f"Error creando tablas: {e2}")

    controller = AppController()
    controller.run()
    logger.info("Aplicacion cerrada")


if __name__ == "__main__":
    main()
