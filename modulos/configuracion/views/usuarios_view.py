from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLabel, QStackedWidget, QSpacerItem, QSizePolicy,
    QLineEdit, QComboBox, QTabWidget,
    QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout,
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
from ui.theme_manager import theme_manager
from services.admin_service import admin_service
from modulos.configuracion.views.audit_view import AuditView


SUBMODULOS_ADMIN = [
    {"codigo": "usuarios", "label": "Usuarios", "icon": "fa5s.user-cog"},
    {"codigo": "auditoria", "label": "Auditoria", "icon": "fa5s.history"},
]


class AdminView(QWidget):
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

        lbl = QLabel("Administracion")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Sub-modulos
        self.stack = QStackedWidget()

        for i, sub in enumerate(SUBMODULOS_ADMIN):
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

        # Boton tema
        btn_theme = QPushButton("  Cambiar modo")
        btn_theme.setIcon(qta.icon("fa5s.adjust", color="#8a8a8a"))
        btn_theme.setCursor(Qt.PointingHandCursor)
        btn_theme.clicked.connect(self._toggle_theme)
        sidebar_layout.addWidget(btn_theme)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 4, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Boton salir
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
        if codigo == "usuarios":
            return UsuariosView()
        if codigo == "auditoria":
            return AuditView()
        return QWidget()

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


class UsuariosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar_usuarios()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Gestion de Usuarios")
        title.setObjectName("title")
        layout.addWidget(title)

        # Boton nuevo arriba
        top = QHBoxLayout()
        btn_nuevo = QPushButton("  Nuevo Usuario")
        btn_nuevo.setIcon(qta.icon("fa5s.user-plus", color="#0f0f0f"))
        btn_nuevo.setMinimumHeight(36)
        btn_nuevo.clicked.connect(self._nuevo_usuario)
        top.addWidget(btn_nuevo)

        btn_rol = QPushButton("  Nuevo Rol")
        btn_rol.setIcon(qta.icon("fa5s.tag", color="#F8F9FA"))
        btn_rol.setMinimumHeight(36)
        btn_rol.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_rol.clicked.connect(self._nuevo_rol)
        top.addWidget(btn_rol)
        top.addStretch()
        layout.addLayout(top)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Usuario", "Nombre Completo", "Email", "Rol", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.tabla)

        # Botones abajo
        bottom = QHBoxLayout()
        bottom.addStretch()

        btn_edit = QPushButton("  Editar")
        btn_edit.setIcon(qta.icon("fa5s.edit", color="#0f0f0f"))
        btn_edit.setMinimumHeight(36)
        btn_edit.clicked.connect(self._editar_seleccionado)
        bottom.addWidget(btn_edit)

        btn_toggle = QPushButton("  Activar/Desactivar")
        btn_toggle.setIcon(qta.icon("fa5s.toggle-on", color="#ffffff"))
        btn_toggle.setMinimumHeight(36)
        btn_toggle.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_toggle.clicked.connect(self._toggle_seleccionado)
        bottom.addWidget(btn_toggle)

        layout.addLayout(bottom)

    def _cargar_usuarios(self):
        self._usuarios = admin_service.listar_usuarios()
        self.tabla.setRowCount(len(self._usuarios))
        for i, u in enumerate(self._usuarios):
            self.tabla.setItem(i, 0, QTableWidgetItem(u.username))
            self.tabla.setItem(i, 1, QTableWidgetItem(u.nombre_completo))
            self.tabla.setItem(i, 2, QTableWidgetItem(u.email or ""))
            self.tabla.setItem(i, 3, QTableWidgetItem(u.rol.nombre if u.rol else ""))
            self.tabla.setItem(i, 4, QTableWidgetItem("Activo" if u.activo else "Inactivo"))

    def _selected_user_id(self) -> int | None:
        row = self.tabla.currentRow()
        if row >= 0 and row < len(self._usuarios):
            return self._usuarios[row].id
        return None

    def _nuevo_usuario(self):
        dialog = UsuarioDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._cargar_usuarios()

    def _editar_seleccionado(self):
        uid = self._selected_user_id()
        if not uid:
            QMessageBox.information(self, "Seleccion", "Selecciona un usuario de la lista.")
            return
        dialog = UsuarioDialog(usuario_id=uid, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._cargar_usuarios()

    def _toggle_seleccionado(self):
        uid = self._selected_user_id()
        if not uid:
            QMessageBox.information(self, "Seleccion", "Selecciona un usuario de la lista.")
            return
        admin_service.desactivar_usuario(uid)
        self._cargar_usuarios()

    def _nuevo_rol(self):
        from PySide6.QtWidgets import QInputDialog
        nombre, ok = QInputDialog.getText(self, "Nuevo Rol", "Nombre del rol:")
        if ok and nombre.strip():
            try:
                admin_service.crear_rol(nombre.strip())
                QMessageBox.information(self, "OK", f"Rol '{nombre}' creado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


class UsuarioDialog(QDialog):
    def __init__(self, usuario_id: int | None = None, parent=None):
        super().__init__(parent)
        self._usuario_id = usuario_id
        self.setWindowTitle("Editar Usuario" if usuario_id else "Nuevo Usuario")
        self.setFixedSize(420, 350)
        self.setModal(True)
        self._build_ui()
        if usuario_id:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        form.setSpacing(10)

        self.input_username = QLineEdit()
        self.input_username.setMinimumHeight(32)
        form.addRow("Usuario:", self.input_username)

        self.input_nombre = QLineEdit()
        self.input_nombre.setMinimumHeight(32)
        form.addRow("Nombre completo:", self.input_nombre)

        self.input_email = QLineEdit()
        self.input_email.setMinimumHeight(32)
        form.addRow("Email:", self.input_email)

        self.input_password = QLineEdit()
        self.input_password.setMinimumHeight(32)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Dejar vacio para no cambiar" if self._usuario_id else "Obligatorio")
        form.addRow("Contrasena:", self.input_password)

        self.combo_rol = QComboBox()
        self.combo_rol.setMinimumHeight(32)
        roles = admin_service.listar_roles()
        for r in roles:
            self.combo_rol.addItem(r.nombre, r.id)
        form.addRow("Rol:", self.combo_rol)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(36)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setMinimumHeight(36)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _cargar_datos(self):
        usuarios = admin_service.listar_usuarios()
        user = next((u for u in usuarios if u.id == self._usuario_id), None)
        if not user:
            return
        self.input_username.setText(user.username)
        self.input_nombre.setText(user.nombre_completo)
        self.input_email.setText(user.email or "")
        if user.rol:
            idx = self.combo_rol.findData(user.rol.id)
            if idx >= 0:
                self.combo_rol.setCurrentIndex(idx)

    def _guardar(self):
        username = self.input_username.text().strip()
        nombre = self.input_nombre.text().strip()
        password = self.input_password.text()

        if not username or not nombre:
            QMessageBox.warning(self, "Error", "Usuario y nombre son obligatorios.")
            return
        if not self._usuario_id and not password:
            QMessageBox.warning(self, "Error", "La contrasena es obligatoria para nuevos usuarios.")
            return

        datos = {
            "username": username,
            "nombre_completo": nombre,
            "email": self.input_email.text().strip(),
            "rol_id": self.combo_rol.currentData(),
        }
        if password:
            datos["password"] = password

        try:
            if self._usuario_id:
                admin_service.actualizar_usuario(self._usuario_id, datos)
            else:
                admin_service.crear_usuario(datos)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
