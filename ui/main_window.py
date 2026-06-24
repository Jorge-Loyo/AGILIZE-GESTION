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
    "empleados": {"label": "RRHH", "icon": "fa5s.user-friends"},
    "ventas": {"label": "Ventas", "icon": "fa5s.cash-register"},
    "compras": {"label": "Compras", "icon": "fa5s.truck-loading"},
    "facturador": {"label": "Facturador", "icon": "fa5s.barcode"},
    "inventario": {"label": "Inventario", "icon": "fa5s.warehouse"},
    "cuentas": {"label": "Cuentas", "icon": "fa5s.file-invoice-dollar"},
    "finanzas": {"label": "Finanzas", "icon": "fa5s.chart-pie"},
    "reportes": {"label": "Reportes", "icon": "fa5s.tachometer-alt"},
    "herramientas": {"label": "Herramientas", "icon": "fa5s.tools"},
    "importador": {"label": "Importador", "icon": "fa5s.file-import"},
    "administrador": {"label": "Admin.", "icon": "fa5s.th-list"},
    "conexiones": {"label": "Conexiones", "icon": "fa5s.plug"},
    "admin": {"label": "Configuracion", "icon": "fa5s.sliders-h"},
}


class MainWindow(QMainWindow):
    logout_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agilize Gestion")
        self.setMinimumSize(1100, 700)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self._busqueda = BusquedaGlobalWidget()
        self._busqueda.empleado_selected.connect(self._on_busqueda_empleado)
        central_layout.addWidget(self._busqueda)

        self.stack = QStackedWidget()
        central_layout.addWidget(self.stack)
        self.setCentralWidget(central)

        shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        shortcut.activated.connect(self._busqueda.toggle)

        modulos_accesibles = auth_service.modulos_accesibles()
        for mod in ["ventas", "compras", "facturador", "inventario", "cuentas", "finanzas", "reportes", "herramientas", "importador", "administrador", "conexiones"]:
            if mod not in modulos_accesibles:
                modulos_accesibles.append(mod)

        orden = ["compras", "inventario", "ventas", "facturador", "empleados", "cuentas", "finanzas", "reportes", "herramientas", "importador", "administrador", "conexiones", "admin"]
        modulos_data = []
        for codigo in orden:
            if codigo in modulos_accesibles and codigo in MODULOS_CONFIG:
                config = MODULOS_CONFIG[codigo]
                modulos_data.append({"codigo": codigo, "label": config["label"], "icon": config["icon"]})

        self._dashboard = DashboardView(modulos_data)
        self._dashboard.modulo_selected.connect(self._abrir_modulo)
        self._dashboard.logout_signal.connect(self._logout)
        self.stack.addWidget(self._dashboard)

        self._modulo_pages: dict[str, int] = {}

    def _abrir_modulo(self, codigo: str):
        if codigo not in self._modulo_pages:
            page = self._get_module_content(codigo)
            idx = self.stack.addWidget(page)
            self._modulo_pages[codigo] = idx
        self.stack.setCurrentIndex(self._modulo_pages[codigo])

    def _get_module_content(self, codigo: str) -> QWidget:
        view = None
        if codigo == "empleados":
            from modulos.rrhh.views.rrhh_view import RRHHView
            view = RRHHView()
        elif codigo == "ventas":
            from modulos.ventas.views.ventas_view import VentasView
            view = VentasView()
        elif codigo == "compras":
            from modulos.compras.views.compras_view import ComprasView
            view = ComprasView()
        elif codigo == "facturador":
            from modulos.facturador.views.facturador_view import FacturadorView
            view = FacturadorView()
        elif codigo == "inventario":
            from modulos.inventario.views.inventario_view import InventarioView
            view = InventarioView()
        elif codigo == "cuentas":
            from modulos.cuentas.views.cuentas_view import CuentasView
            view = CuentasView()
        elif codigo == "finanzas":
            from modulos.finanzas.views.finanzas_view import FinanzasView
            view = FinanzasView()
        elif codigo == "reportes":
            from modulos.reportes.views.reportes_view import ReportesView
            view = ReportesView()
        elif codigo == "herramientas":
            from modulos.herramientas.views.herramientas_view import HerramientasView
            view = HerramientasView()
        elif codigo == "importador":
            from modulos.importador.views.importador_view import ImportadorView
            view = ImportadorView()
        elif codigo == "administrador":
            from modulos.administrador.views.administrador_view import AdministradorView
            view = AdministradorView()
        elif codigo == "conexiones":
            from modulos.conexiones.views.conexiones_view import ConexionesView
            view = ConexionesView()
        elif codigo == "admin":
            from modulos.configuracion.views.config_global_view import ConfigGlobalView
            view = ConfigGlobalView()

        if view and hasattr(view, 'volver_dashboard'):
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
        if view and hasattr(view, 'logout_signal'):
            view.logout_signal.connect(self._logout)

        if view:
            return view

        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.addWidget(QLabel("Modulo en desarrollo"))
        lay.addStretch()
        return page

    def _logout(self):
        auth_service.logout()
        self.logout_signal.emit()

    def _on_busqueda_empleado(self, empleado_id: int):
        from modulos.rrhh.views.detalle_empleado_dialog import EmpleadoDetalleDialog
        dialog = EmpleadoDetalleDialog(empleado_id, parent=self)
        dialog.exec()

    def closeEvent(self, event):
        if auth_service.current_user:
            from PySide6.QtWidgets import QApplication, QMessageBox
            resp = QMessageBox.question(
                self, "Cerrar", "Seguro que quieres cerrar la aplicacion?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if resp == QMessageBox.No:
                event.ignore()
                return
            QApplication.instance().quit()
        event.accept()
