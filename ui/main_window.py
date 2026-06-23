from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QLabel, QStackedWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QShortcut, QKeySequence
from services.auth_service import auth_service
from ui.theme_manager import theme_manager
from ui.dashboard_view import DashboardView
from ui.busqueda_global import BusquedaGlobalWidget


MODULOS_CONFIG = {
    "empleados": {"label": "RRHH", "icon": "fa5s.users"},
    "herramientas": {"label": "Herramientas", "icon": "fa5s.toolbox"},
    "admin": {"label": "Configuracion", "icon": "fa5s.cog"},
}


class MainWindow(QMainWindow):
    logout_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agilize Gestión")
        self.setMinimumSize(1100, 700)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Búsqueda global
        self._busqueda = BusquedaGlobalWidget()
        self._busqueda.empleado_selected.connect(self._on_busqueda_empleado)
        central_layout.addWidget(self._busqueda)

        self.stack = QStackedWidget()
        central_layout.addWidget(self.stack)
        self.setCentralWidget(central)

        # Shortcut Ctrl+K
        shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        shortcut.activated.connect(self._busqueda.toggle)

        # Página 0: Dashboard
        modulos_accesibles = auth_service.modulos_accesibles()
        # Herramientas siempre disponible para cualquier usuario con acceso
        if "herramientas" not in modulos_accesibles:
            modulos_accesibles.append("herramientas")
        modulos_data = []
        for codigo in modulos_accesibles:
            if codigo not in MODULOS_CONFIG:
                continue
            config = MODULOS_CONFIG[codigo]
            modulos_data.append({"codigo": codigo, "label": config["label"], "icon": config["icon"]})

        self._dashboard = DashboardView(modulos_data)
        self._dashboard.modulo_selected.connect(self._abrir_modulo)
        self._dashboard.logout_signal.connect(self._logout)
        self.stack.addWidget(self._dashboard)

        # Páginas de módulos se crean bajo demanda
        self._modulo_pages: dict[str, int] = {}

    def _abrir_modulo(self, codigo: str):
        if codigo not in self._modulo_pages:
            page = self._get_module_content(codigo)
            idx = self.stack.addWidget(page)
            self._modulo_pages[codigo] = idx

        self.stack.setCurrentIndex(self._modulo_pages[codigo])

    def _get_module_content(self, codigo: str) -> QWidget:
        if codigo == "empleados":
            from modulos.rrhh.views.rrhh_view import RRHHView
            view = RRHHView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "herramientas":
            from modulos.herramientas.views.herramientas_view import HerramientasView
            view = HerramientasView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "admin":
            from modulos.configuracion.views.config_global_view import ConfigGlobalView
            view = ConfigGlobalView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view

        # Placeholder
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 32, 32, 32)
        lbl = QLabel("Modulo en desarrollo")
        lbl.setObjectName("subtitle")
        lay.addWidget(lbl)
        lay.addStretch()
        return page

    def _logout(self):
        auth_service.logout()
        self.logout_signal.emit()

    def _on_busqueda_empleado(self, empleado_id: int):
        """Abre el detalle del empleado desde la búsqueda global."""
        from modulos.rrhh.views.detalle_empleado_dialog import EmpleadoDetalleDialog
        dialog = EmpleadoDetalleDialog(empleado_id, parent=self)
        dialog.exec()

    def closeEvent(self, event):
        if auth_service.current_user:
            from PySide6.QtWidgets import QApplication, QMessageBox
            resp = QMessageBox.question(
                self, "Cerrar",
                "Seguro que quieres cerrar la aplicacion?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if resp == QMessageBox.No:
                event.ignore()
                return
            QApplication.instance().quit()
        event.accept()
