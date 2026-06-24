from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpacerItem, QSizePolicy, QGridLayout,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap
import qtawesome as qta
from ui.theme_manager import theme_manager
from services.logo_service import get_dev_logo_path
from services.empresa_service import empresa_service

ICONOS_MODULO = {
    "empleados": "fa5s.user-friends",
    "ventas": "fa5s.cash-register",
    "compras": "fa5s.truck-loading",
    "facturador": "fa5s.barcode",
    "inventario": "fa5s.warehouse",
    "cuentas": "fa5s.file-invoice-dollar",
    "finanzas": "fa5s.chart-pie",
    "reportes": "fa5s.tachometer-alt",
    "herramientas": "fa5s.tools",
    "conexiones": "fa5s.plug",
    "importador": "fa5s.file-import",
    "administrador": "fa5s.th-list",
    "admin": "fa5s.sliders-h",
}


class DashboardView(QWidget):
    modulo_selected = Signal(str)
    logout_signal = Signal()

    def __init__(self, modulos: list[dict], parent=None):
        super().__init__(parent)
        self._modulos = modulos
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(20)

        # Top bar
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        self.btn_theme = QPushButton()
        self.btn_theme.setFixedSize(40, 40)
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #2a2a2a; border-radius: 20px; }")
        self.btn_theme.clicked.connect(self._toggle_theme)
        self._update_theme_icon()
        top_bar.addWidget(self.btn_theme)

        btn_logout = QPushButton("  Cerrar sesion")
        btn_logout.setIcon(qta.icon("fa5s.sign-out-alt", color="#ffffff"))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("QPushButton { background-color: #ef4444; padding: 8px 16px; } QPushButton:hover { background-color: #dc2626; }")
        btn_logout.clicked.connect(self.logout_signal.emit)
        top_bar.addWidget(btn_logout)

        layout.addLayout(top_bar)

        # Header
        logo_label = QLabel()
        pixmap = QPixmap(get_dev_logo_path()).scaled(QSize(80, 80), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        title = QLabel(empresa_service.obtener("dev_nombre") or "Agilize")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Selecciona un modulo para comenzar")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Grid de modulos (2 filas)
        grid = QGridLayout()
        grid.setAlignment(Qt.AlignCenter)
        grid.setSpacing(20)

        cols = 7  # 7 columnas por fila
        for idx, mod in enumerate(self._modulos):
            row = idx // cols
            col = idx % cols
            btn = QPushButton(f"\n{mod['label']}")
            icon_name = mod.get("icon") or ICONOS_MODULO.get(mod["codigo"], "fa5s.cube")
            btn.setIcon(qta.icon(icon_name, color="#0f0f0f"))
            btn.setIconSize(QSize(32, 32))
            btn.setFixedSize(140, 100)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 11px;
                    font-weight: bold;
                    border-radius: 12px;
                    color: #0f0f0f;
                }
            """)
            btn.clicked.connect(lambda checked, c=mod["codigo"]: self.modulo_selected.emit(c))
            grid.addWidget(btn, row, col)

        layout.addLayout(grid)
        layout.addStretch()

    def _toggle_theme(self):
        from PySide6.QtWidgets import QApplication
        theme_manager.toggle(QApplication.instance())
        self._update_theme_icon()

    def _update_theme_icon(self):
        if theme_manager.current == theme_manager.DARK:
            self.btn_theme.setIcon(qta.icon("fa5s.sun", color="#D4AF37"))
        else:
            self.btn_theme.setIcon(qta.icon("fa5s.moon", color="#b8962e"))
        self.btn_theme.setIconSize(QSize(22, 22))
