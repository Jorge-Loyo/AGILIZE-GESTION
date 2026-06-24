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
    "conexiones": {"label": "Conexiones", "icon": "fa5s.plug"},
    "admin": {"label": "Configuracion", "icon": "fa5s.sliders-h"},
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
        # Todos los modulos disponibles
        for mod in ["ventas", "compras", "facturador", "inventario", "cuentas", "finanzas", "reportes", "herramientas", "conexiones"]:
            if mod not in modulos_accesibles:
                modulos_accesibles.append(mod)

        # Forzar orden
        orden = ["empleados", "ventas", "compras", "facturador", "inventario", "cuentas", "finanzas", "reportes", "herramientas", "conexiones", "admin"]
        modulos_data = []
        for codigo in orden:
            if codigo in modulos_accesibles and codigo in MODULOS_CONFIG:
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
        if codigo == "ventas":
            from modulos.ventas.views.ventas_view import VentasView
            view = VentasView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "compras":
            from modulos.compras.views.compras_view import ComprasView
            view = ComprasView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "facturador":
            from modulos.facturador.views.facturador_view import FacturadorView
            view = FacturadorView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "inventario":
            from modulos.inventario.views.inventario_view import InventarioView
            view = InventarioView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "datos":
            from modulos.datos.views.datos_view import DatosView
            view = DatosView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "cuentas":
            from modulos.cuentas.views.cuentas_view import CuentasView
            view = CuentasView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "finanzas":
            from modulos.finanzas.views.finanzas_view import FinanzasView
            view = FinanzasView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "reportes":
            from modulos.reportes.views.reportes_view import ReportesView
            view = ReportesView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "herramientas":
            from modulos.herramientas.views.herramientas_view import HerramientasView
            view = HerramientasView()
            view.volver_dashboard.connect(lambda: self.stack.setCurrentIndex(0))
            view.logout_signal.connect(self._logout)
            return view
        if codigo == "conexiones":
            from modulos.conexiones.views.conexiones_view import ConexionesView
            view = ConexionesView()
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
