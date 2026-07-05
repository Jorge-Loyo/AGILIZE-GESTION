from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QPushButton, QLabel, QStackedWidget, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
from ui.theme_manager import theme_manager


SUBMODULOS_RRHH = [
    {"codigo": "dashboard", "label": "Dashboard", "icon": "fa5s.chart-bar"},
    {"codigo": "empleados", "label": "Empleados", "icon": "fa5s.users"},
    {"codigo": "legajo", "label": "Legajo", "icon": "fa5s.folder-open"},
    {"codigo": "asistencia", "label": "Asistencia", "icon": "fa5s.clock"},
    {"codigo": "fichaje", "label": "Fichaje / Turnos", "icon": "fa5s.fingerprint"},
    {"codigo": "cierres", "label": "Cierres", "icon": "fa5s.lock"},
    {"codigo": "nomina", "label": "Nomina", "icon": "fa5s.money-bill-wave"},
    {"codigo": "reclutamiento", "label": "Reclutamiento", "icon": "fa5s.user-plus"},
    {"codigo": "config", "label": "Configuracion", "icon": "fa5s.cog"},
]


class RRHHView(QWidget):
    volver_dashboard = Signal()
    logout_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons: list[QPushButton] = []
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(4)

        # Boton volver
        btn_volver = QPushButton("  Menu")
        btn_volver.setIcon(qta.icon("fa5s.arrow-left", color="#8a8a8a"))
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.setStyleSheet("QPushButton { background-color: transparent; color: #8a8a8a; border: none; text-align: left; padding: 8px 12px; } QPushButton:hover { color: #F8F9FA; }")
        btn_volver.clicked.connect(self.volver_dashboard.emit)
        sidebar_layout.addWidget(btn_volver)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        lbl = QLabel("RRHH")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Botones de sub-modulos
        self.stack = QStackedWidget()

        for i, sub in enumerate(SUBMODULOS_RRHH):
            btn = QPushButton(f"  {sub['label']}")
            btn.setIcon(qta.icon(sub["icon"], color="#8a8a8a"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._navigate(idx))
            sidebar_layout.addWidget(btn)
            self._buttons.append(btn)

            page = self._create_submodule(sub["codigo"])
            self.stack.addWidget(page)

        sidebar_layout.addStretch()

        # Boton manual de uso
        btn_manual = QPushButton("  Manual de uso")
        btn_manual.setIcon(qta.icon("fa5s.question-circle", color="#D4AF37"))
        btn_manual.setCursor(Qt.PointingHandCursor)
        btn_manual.setStyleSheet("QPushButton { background-color: transparent; color: #D4AF37; border: 1px solid #D4AF37; border-radius: 4px; padding: 6px 10px; } QPushButton:hover { background-color: #D4AF37; color: #0f0f0f; }")
        btn_manual.clicked.connect(self._ver_manual)
        sidebar_layout.addWidget(btn_manual)

        # Boton cambiar tema
        btn_theme = QPushButton("  Cambiar modo")
        btn_theme.setIcon(qta.icon("fa5s.adjust", color="#8a8a8a"))
        btn_theme.setCursor(Qt.PointingHandCursor)
        btn_theme.clicked.connect(self._toggle_theme)
        sidebar_layout.addWidget(btn_theme)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 4, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Boton salir
        btn_logout = QPushButton("  Cerrar sesion")
        btn_logout.setIcon(qta.icon("fa5s.sign-out-alt", color="#000000"))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("QPushButton { background-color: #ef4444; color: #000000; } QPushButton:hover { background-color: #dc2626; }")
        btn_logout.clicked.connect(self.logout_signal.emit)
        sidebar_layout.addWidget(btn_logout)

        layout.addWidget(sidebar)
        layout.addWidget(self.stack)

        # Seleccionar primero
        if self._buttons:
            self._navigate(0)

    def _create_submodule(self, codigo: str) -> QWidget:
        if codigo == "dashboard":
            from modulos.rrhh.views.dashboard_rrhh_view import DashboardRRHHView
            return DashboardRRHHView()
        if codigo == "empleados":
            from modulos.rrhh.views.lista_empleados import EmpleadosView
            return EmpleadosView()
        if codigo == "asistencia":
            from modulos.rrhh.views.asistencia_view import AsistenciaView
            return AsistenciaView()
        if codigo == "cierres":
            from modulos.rrhh.views.cierres_view import CierresAsistenciaView
            return CierresAsistenciaView()
        if codigo == "nomina":
            from modulos.rrhh.views.nomina_view import NominaView
            return NominaView()
        if codigo == "config":
            from modulos.rrhh.views.config_rrhh_view import ConfigRRHHView
            return ConfigRRHHView()
        if codigo == "legajo":
            from modulos.rrhh.views.legajo_view import LegajoView
            return LegajoView()
        if codigo == "fichaje":
            from modulos.rrhh.views.fichaje_view import FichajeView
            return FichajeView()
        if codigo == "reclutamiento":
            from modulos.rrhh.views.reclutamiento_view import ReclutamientoView
            return ReclutamientoView()

        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 32, 32, 32)
        lbl = QLabel("En desarrollo")
        lbl.setObjectName("subtitle")
        lay.addWidget(lbl)
        lay.addStretch()
        return page

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == index)
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _toggle_theme(self):
        from PySide6.QtWidgets import QApplication
        theme_manager.toggle(QApplication.instance())

    def _ver_manual(self):
        from ui.manual_uso_view import ManualUsoView, MANUAL_RRHH
        # Agregar como página del stack si no existe
        if not hasattr(self, '_manual_idx'):
            manual = ManualUsoView(MANUAL_RRHH, "Manual - RRHH")
            self._manual_idx = self.stack.addWidget(manual)
        self.stack.setCurrentIndex(self._manual_idx)
        for btn in self._buttons:
            btn.setChecked(False)
            btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
