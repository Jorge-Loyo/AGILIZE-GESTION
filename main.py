import sys
from core.logging_config import logger


class AppController:
    def __init__(self):
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        from core.config import settings
        from ui.theme_manager import theme_manager
        from services.logo_service import get_dev_logo_path

        self.app = QApplication(sys.argv)
        self.app.setApplicationName(settings.APP_NAME)
        self.app.setApplicationVersion(settings.APP_VERSION)
        self.app.setQuitOnLastWindowClosed(False)

        # Icono de la aplicacion
        self.app.setWindowIcon(QIcon(get_dev_logo_path()))

        theme_manager.apply(self.app, theme_manager.DARK)

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


def main():
    logger.info("Iniciando Agilize Gestion")

    # Auto-migrar BD al iniciar
    try:
        from alembic.config import Config
        from alembic import command
        from core.config import BASE_DIR
        alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))
        alembic_cfg.set_main_option("script_location", str(BASE_DIR / "alembic"))
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        logger.warning(f"Auto-migracion: {e}")

    controller = AppController()
    controller.run()
    logger.info("Aplicacion cerrada")


if __name__ == "__main__":
    main()
