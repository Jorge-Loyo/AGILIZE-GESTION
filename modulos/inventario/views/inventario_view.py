from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QPushButton, QLabel, QStackedWidget, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
from ui.theme_manager import theme_manager


SUBMODULOS_INVENTARIO = [
    {"codigo": "dashboard_inv", "label": "Dashboard", "icon": "fa5s.chart-bar"},
    {"codigo": "productos", "label": "Productos", "icon": "fa5s.box"},
    {"codigo": "depositos", "label": "Depositos", "icon": "fa5s.warehouse"},
    {"codigo": "movimientos", "label": "Movimientos", "icon": "fa5s.exchange-alt"},
]


class InventarioView(QWidget):
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

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(4)

        btn_volver = QPushButton("  Menu")
        btn_volver.setIcon(qta.icon("fa5s.arrow-left", color="#8a8a8a"))
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.setStyleSheet(
            "QPushButton { background-color: transparent; color: #8a8a8a; "
            "border: none; text-align: left; padding: 8px 12px; } "
            "QPushButton:hover { color: #F8F9FA; }"
        )
        btn_volver.clicked.connect(self.volver_dashboard.emit)
        sidebar_layout.addWidget(btn_volver)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        lbl = QLabel("Inventario")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.stack = QStackedWidget()

        for i, sub in enumerate(SUBMODULOS_INVENTARIO):
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

        btn_theme = QPushButton("  Cambiar modo")
        btn_theme.setIcon(qta.icon("fa5s.adjust", color="#8a8a8a"))
        btn_theme.setCursor(Qt.PointingHandCursor)
        btn_theme.clicked.connect(self._toggle_theme)
        sidebar_layout.addWidget(btn_theme)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 4, QSizePolicy.Minimum, QSizePolicy.Fixed))

        btn_logout = QPushButton("  Cerrar sesion")
        btn_logout.setIcon(qta.icon("fa5s.sign-out-alt", color="#ffffff"))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet(
            "QPushButton { background-color: #ef4444; } "
            "QPushButton:hover { background-color: #dc2626; }"
        )
        btn_logout.clicked.connect(self.logout_signal.emit)
        sidebar_layout.addWidget(btn_logout)

        layout.addWidget(sidebar)
        layout.addWidget(self.stack)

        if self._buttons:
            self._navigate(0)

    def _create_submodule(self, codigo: str) -> QWidget:
        if codigo == "dashboard_inv":
            from modulos.inventario.views.dashboard_inv_view import DashboardInventarioView
            return DashboardInventarioView()
        if codigo == "productos":
            from modulos.inventario.views.productos_view import ProductosView
            return ProductosView()
        if codigo == "depositos":
            from modulos.inventario.views.depositos_view import DepositosView
            return DepositosView()
        if codigo == "movimientos":
            from modulos.inventario.views.movimientos_view import MovimientosView
            return MovimientosView()

        page = QWidget()
        lay = QVBoxLayout(page)
        lay.addWidget(QLabel("En desarrollo"))
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
