from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QPushButton, QLabel, QStackedWidget, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
from ui.theme_manager import theme_manager


SUBMODULOS_FINANZAS = [
    {"codigo": "facturacion", "label": "Facturacion", "icon": "fa5s.file-invoice"},
    {"codigo": "impuestos", "label": "Contabilidad", "icon": "fa5s.book"},
    {"codigo": "caja", "label": "Caja", "icon": "fa5s.cash-register"},
    {"codigo": "reportes_fin", "label": "Bancos", "icon": "fa5s.university"},
    {"codigo": "historial_dolar", "label": "Historial Dolar", "icon": "fa5s.dollar-sign"},
]


class FinanzasView(QWidget):
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
        btn_volver.setStyleSheet("QPushButton { background-color: transparent; color: #8a8a8a; border: none; text-align: left; padding: 8px 12px; } QPushButton:hover { color: #F8F9FA; }")
        btn_volver.clicked.connect(self.volver_dashboard.emit)
        sidebar_layout.addWidget(btn_volver)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))
        lbl = QLabel("Finanzas")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl)

        # Mostrar pais configurado
        try:
            from services.core.empresa_service import empresa_service
            pais = empresa_service.obtener("cotizacion_pais") or "Sin configurar"
        except Exception:
            pais = "Sin configurar"
        lbl_pais = QLabel(f"Pais: {pais}")
        lbl_pais.setStyleSheet("font-size: 10px; color: #888;")
        lbl_pais.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl_pais)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.stack = QStackedWidget()
        for i, sub in enumerate(SUBMODULOS_FINANZAS):
            btn = QPushButton(f"  {sub['label']}")
            btn.setIcon(qta.icon(sub["icon"], color="#8a8a8a"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._navigate(idx))
            sidebar_layout.addWidget(btn)
            self._buttons.append(btn)
            self.stack.addWidget(self._create_submodule(sub["codigo"]))

        sidebar_layout.addStretch()
        btn_theme = QPushButton("  Cambiar modo")
        btn_theme.setIcon(qta.icon("fa5s.adjust", color="#8a8a8a"))
        btn_theme.setCursor(Qt.PointingHandCursor)
        btn_theme.clicked.connect(lambda: theme_manager.toggle(__import__('PySide6.QtWidgets', fromlist=['QApplication']).QApplication.instance()))
        sidebar_layout.addWidget(btn_theme)
        sidebar_layout.addSpacerItem(QSpacerItem(0, 4, QSizePolicy.Minimum, QSizePolicy.Fixed))
        btn_logout = QPushButton("  Cerrar sesion")
        btn_logout.setIcon(qta.icon("fa5s.sign-out-alt", color="#ffffff"))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_logout.clicked.connect(self.logout_signal.emit)
        sidebar_layout.addWidget(btn_logout)

        layout.addWidget(sidebar)
        layout.addWidget(self.stack)
        if self._buttons:
            self._navigate(0)

    def _create_submodule(self, codigo: str) -> QWidget:
        if codigo == "facturacion":
            from modulos.finanzas.views.facturacion_view import FacturacionView
            return FacturacionView()
        if codigo == "impuestos":
            from modulos.finanzas.views.contabilidad_view import ContabilidadView
            return ContabilidadView()
        if codigo == "caja":
            from modulos.finanzas.views.caja_view import CajaView
            return CajaView()
        if codigo == "reportes_fin":
            from modulos.finanzas.views.bancos_view import BancosView
            return BancosView()
        if codigo == "historial_dolar":
            from modulos.finanzas.views.historial_dolar_view import HistorialDolarView
            return HistorialDolarView()
        return QWidget()

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == index)
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
