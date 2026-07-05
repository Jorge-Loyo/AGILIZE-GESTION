from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage
import qtawesome as qta
import base64


class LoginView(QWidget):
    login_success = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agilize Gestion")
        self.setFixedSize(440, 600)
        self._pass_visible = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(60, 30, 60, 20)
        layout.setSpacing(10)

        # --- Logo empresa (de Visual) ---
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        try:
            from services.core.empresa_service import empresa_service
            datos = empresa_service.obtener_todos()
        except Exception:
            datos = {}

        logo_b64 = datos.get("logo_base64", "")
        if logo_b64:
            img_bytes = base64.b64decode(logo_b64)
            img = QImage()
            img.loadFromData(img_bytes)
            pixmap = QPixmap.fromImage(img).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            # Fallback: archivo local
            from services.core.logo_service import get_empresa_logo_path
            path = get_empresa_logo_path()
            if path:
                pixmap = QPixmap(path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)

        # --- Nombre app (de Visual) ---
        nombre_app = datos.get("nombre_app", "Agilize Gestion")
        title = QLabel(nombre_app)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacerItem(QSpacerItem(0, 24, QSizePolicy.Minimum, QSizePolicy.Fixed))

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

        # --- Desarrollado por (datos de Desarrollador) ---
        dev_nombre = datos.get("dev_nombre", "")
        dev_web = datos.get("dev_web", "")
        dev_logo_b64 = datos.get("dev_logo_base64", "")

        if dev_nombre or dev_logo_b64:
            sep = QLabel()
            sep.setFixedHeight(1)
            sep.setStyleSheet("background-color: #333;")
            layout.addWidget(sep)

            layout.addSpacerItem(QSpacerItem(0, 6, QSizePolicy.Minimum, QSizePolicy.Fixed))

            lbl_dev = QLabel("Desarrollado por")
            lbl_dev.setAlignment(Qt.AlignCenter)
            lbl_dev.setStyleSheet("font-size: 9px; color: #666;")
            layout.addWidget(lbl_dev)

            # Logo dev + nombre en fila
            dev_row = QHBoxLayout()
            dev_row.setAlignment(Qt.AlignCenter)
            dev_row.setSpacing(8)

            if dev_logo_b64:
                dev_logo_label = QLabel()
                dev_logo_label.setAlignment(Qt.AlignCenter)
                img_bytes = base64.b64decode(dev_logo_b64)
                img = QImage()
                img.loadFromData(img_bytes)
                pixmap = QPixmap.fromImage(img).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                dev_logo_label.setPixmap(pixmap)
                dev_row.addWidget(dev_logo_label)

            if dev_nombre:
                lbl_name = QLabel(dev_nombre)
                lbl_name.setStyleSheet("font-size: 10px; color: #888; font-weight: bold;")
                dev_row.addWidget(lbl_name)

            layout.addLayout(dev_row)

            if dev_web:
                lbl_web = QLabel(dev_web)
                lbl_web.setAlignment(Qt.AlignCenter)
                lbl_web.setStyleSheet("font-size: 9px; color: #555;")
                layout.addWidget(lbl_web)

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
            self._show_error("Error de conexion (clic para ver detalle)")
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
