from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap
import qtawesome as qta
from services.core.logo_service import get_dev_logo_path
from services.core.empresa_service import empresa_service


class LoginView(QWidget):
    login_success = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agilize Gestion")
        self.setFixedSize(440, 540)
        self._pass_visible = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(10)

        # Logo
        icon_label = QLabel()
        try:
            pixmap = QPixmap(get_dev_logo_path()).scaled(QSize(64, 64), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        except Exception:
            pass
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Titulo
        try:
            nombre = empresa_service.obtener("dev_nombre") or "Agilize"
        except Exception:
            nombre = "Agilize"
        title = QLabel(nombre)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Gestion Empresarial")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Usuario
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Usuario")
        self.input_user.setMinimumHeight(40)
        layout.addWidget(self.input_user)

        layout.addSpacerItem(QSpacerItem(0, 6, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Password con ojo
        pass_row = QHBoxLayout()
        pass_row.setSpacing(0)

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Contrasena")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setMinimumHeight(40)
        pass_row.addWidget(self.input_pass)

        self.btn_eye = QPushButton()
        self.btn_eye.setFixedSize(40, 40)
        self.btn_eye.setCursor(Qt.PointingHandCursor)
        self.btn_eye.setIcon(qta.icon("fa5s.eye-slash", color="#888888"))
        self.btn_eye.setIconSize(QSize(18, 18))
        self.btn_eye.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #2a2a2a; border-radius: 20px; }")
        self.btn_eye.clicked.connect(self._toggle_password)
        pass_row.addWidget(self.btn_eye)

        layout.addLayout(pass_row)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("error")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.hide()
        layout.addWidget(self.lbl_error)

        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Boton
        self.btn_login = QPushButton("  Ingresar")
        self.btn_login.setMinimumHeight(44)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self._on_login)
        layout.addWidget(self.btn_login)

        layout.addStretch()

        # Version
        version = QLabel("v1.0.0")
        version.setObjectName("subtitle")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        # Enter
        self.input_pass.returnPressed.connect(self._on_login)
        self.input_user.returnPressed.connect(lambda: self.input_pass.setFocus())

    def _toggle_password(self):
        self._pass_visible = not self._pass_visible
        if self._pass_visible:
            self.input_pass.setEchoMode(QLineEdit.Normal)
            self.btn_eye.setIcon(qta.icon("fa5s.eye", color="#D4AF37"))
        else:
            self.input_pass.setEchoMode(QLineEdit.Password)
            self.btn_eye.setIcon(qta.icon("fa5s.eye-slash", color="#888888"))

    def _on_login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text()

        if not username or not password:
            self._show_error("Completa usuario y contrasena")
            return

        try:
            from services.core.auth_service import auth_service
            success, msg = auth_service.login(username, password)

            if success:
                self.lbl_error.hide()
                self.login_success.emit()
            else:
                self._show_error(msg)
        except Exception as e:
            error_detail = str(e)
            self._show_error(f"Error de conexion (clic para ver detalle)")
            self._last_error_detail = error_detail
            self.lbl_error.setCursor(Qt.PointingHandCursor)
            self.lbl_error.mousePressEvent = lambda ev: self._show_error_dialog(error_detail)

    def _show_error(self, msg: str):
        self.lbl_error.setText(msg)
        self.lbl_error.show()

    def _show_error_dialog(self, detail: str):
        from PySide6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle("Detalle del error")
        dlg.setMinimumSize(500, 300)
        lay = QVBoxLayout(dlg)
        txt = QTextEdit()
        txt.setPlainText(detail)
        txt.setReadOnly(True)
        txt.setStyleSheet("font-family: Consolas; font-size: 11px;")
        lay.addWidget(txt)
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dlg.accept)
        lay.addWidget(btns)
        dlg.exec()

    def closeEvent(self, event):
        from services.core.auth_service import auth_service
        if not auth_service.current_user:
            from PySide6.QtWidgets import QApplication
            QApplication.instance().quit()
        event.accept()
