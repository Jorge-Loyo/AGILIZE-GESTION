from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QPushButton, QLabel, QStackedWidget, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
from ui.theme_manager import theme_manager


SUBMODULOS_COMPRAS = [
    {"codigo": "proveedores", "label": "Proveedores", "icon": "fa5s.truck"},
    {"codigo": "requisiciones", "label": "Requerimientos", "icon": "fa5s.hand-paper"},
    {"codigo": "req_sugerido", "label": "Req. Sugerido", "icon": "fa5s.magic"},
    {"codigo": "ordenes_compra", "label": "Ordenes de Compra", "icon": "fa5s.clipboard-list"},
    {"codigo": "recepcion", "label": "Recepcion", "icon": "fa5s.dolly"},
    {"codigo": "facturas_compra", "label": "Facturas", "icon": "fa5s.file-invoice"},
    {"codigo": "precios", "label": "Listas de Precios", "icon": "fa5s.tags"},
    {"codigo": "cotizaciones", "label": "Cotizaciones", "icon": "fa5s.balance-scale"},
    {"codigo": "aprobaciones", "label": "Aprobaciones", "icon": "fa5s.user-check"},
    {"codigo": "trazabilidad", "label": "Trazabilidad", "icon": "fa5s.project-diagram"},
    {"codigo": "reportes", "label": "Reportes KPI", "icon": "fa5s.chart-line"},
]


class ComprasView(QWidget):
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
        lbl = QLabel("Compras")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl)
        sidebar_layout.addSpacerItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.stack = QStackedWidget()
        for i, sub in enumerate(SUBMODULOS_COMPRAS):
            btn = QPushButton(f"  {sub['label']}")
            btn.setIcon(qta.icon(sub["icon"], color="#8a8a8a"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._navigate(idx))
            sidebar_layout.addWidget(btn)
            self._buttons.append(btn)
            self.stack.addWidget(self._create_submodule(sub["codigo"]))

        sidebar_layout.addStretch()
        btn_manual = QPushButton("  Manual de uso")
        btn_manual.setIcon(qta.icon("fa5s.question-circle", color="#D4AF37"))
        btn_manual.setCursor(Qt.PointingHandCursor)
        btn_manual.setStyleSheet("QPushButton { background-color: transparent; color: #D4AF37; border: 1px solid #D4AF37; border-radius: 4px; padding: 6px 10px; } QPushButton:hover { background-color: #D4AF37; color: #0f0f0f; }")
        btn_manual.clicked.connect(self._ver_manual)
        sidebar_layout.addWidget(btn_manual)
        sidebar_layout.addSpacerItem(QSpacerItem(0, 4, QSizePolicy.Minimum, QSizePolicy.Fixed))
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
        if codigo == "proveedores":
            from modulos.datos.views.proveedores_view import ProveedoresView
            return ProveedoresView()
        if codigo == "requisiciones":
            from modulos.compras.views.requisiciones_view import RequisicionesView
            return RequisicionesView()
        if codigo == "req_sugerido":
            from modulos.compras.views.orden_sugerida_view import ReqSugeridoView
            return ReqSugeridoView()
        if codigo == "ordenes_compra":
            from modulos.compras.views.ordenes_compra_view import OrdenesCompraView
            return OrdenesCompraView()
        if codigo == "recepcion":
            from modulos.compras.views.recepcion_view import RecepcionView
            return RecepcionView()
        if codigo == "facturas_compra":
            from modulos.compras.views.facturas_compra_view import FacturasCompraView
            return FacturasCompraView()
        if codigo == "precios":
            from modulos.compras.views.precios_proveedores_view import PreciosProveedoresView
            return PreciosProveedoresView()
        if codigo == "cotizaciones":
            from modulos.compras.views.cotizaciones_compra_view import CotizacionesCompraView
            return CotizacionesCompraView()
        if codigo == "aprobaciones":
            from modulos.compras.views.aprobaciones_compra_view import AprobacionesCompraView
            return AprobacionesCompraView()
        if codigo == "trazabilidad":
            from modulos.compras.views.trazabilidad_view import TrazabilidadCompraView
            return TrazabilidadCompraView()
        if codigo == "reportes":
            from modulos.compras.views.reportes_compras_view import ReportesComprasView
            return ReportesComprasView()
        return QWidget()

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == index)
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _ver_manual(self):
        from ui.manual_uso_view import ManualUsoView, MANUAL_COMPRAS
        if not hasattr(self, '_manual_idx'):
            manual = ManualUsoView(MANUAL_COMPRAS, "Manual - Compras")
            self._manual_idx = self.stack.addWidget(manual)
        self.stack.setCurrentIndex(self._manual_idx)
        for btn in self._buttons:
            btn.setChecked(False)
