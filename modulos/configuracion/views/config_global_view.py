from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QLineEdit, QPushButton, QLabel, QTabWidget, QFileDialog, QGroupBox,
    QMessageBox, QStackedWidget, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap
from pathlib import Path
import shutil
import qtawesome as qta
from ui.theme_manager import theme_manager
from services.empresa_service import empresa_service
from core.database import get_db
from models.sucursal import Sucursal
from core.config import BASE_DIR


SUBMODULOS_CONFIG = [
    {"codigo": "empresa", "label": "Datos Empresa", "icon": "fa5s.building"},
    {"codigo": "visual", "label": "Visual", "icon": "fa5s.palette"},
    {"codigo": "roles", "label": "Roles", "icon": "fa5s.user-shield"},
    {"codigo": "usuarios", "label": "Usuarios", "icon": "fa5s.user-cog"},
    {"codigo": "auditoria", "label": "Auditoria", "icon": "fa5s.history"},
    {"codigo": "actualizar", "label": "Actualizar", "icon": "fa5s.download"},
    {"codigo": "desarrollador", "label": "Desarrollador", "icon": "fa5s.code"},
]


class ConfigGlobalView(QWidget):
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

        btn_volver = QPushButton("  Menu")
        btn_volver.setIcon(qta.icon("fa5s.arrow-left", color="#8a8a8a"))
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.setStyleSheet("QPushButton { background-color: transparent; color: #8a8a8a; border: none; text-align: left; padding: 8px 12px; } QPushButton:hover { color: #F8F9FA; }")
        btn_volver.clicked.connect(self.volver_dashboard.emit)
        sidebar_layout.addWidget(btn_volver)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        lbl = QLabel("Configuracion")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.stack = QStackedWidget()

        for i, sub in enumerate(SUBMODULOS_CONFIG):
            btn = QPushButton(f"  {sub['label']}")
            btn.setIcon(qta.icon(sub["icon"], color="#8a8a8a"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._navigate(idx))
            sidebar_layout.addWidget(btn)
            self._buttons.append(btn)

        sidebar_layout.addStretch()

        btn_manual = QPushButton("  Manual de uso")
        btn_manual.setIcon(qta.icon("fa5s.question-circle", color="#8a8a8a"))
        btn_manual.setCursor(Qt.PointingHandCursor)
        btn_manual.clicked.connect(self._ver_manual)
        sidebar_layout.addWidget(btn_manual)

        btn_theme = QPushButton("  Cambiar modo")
        btn_theme.setIcon(qta.icon("fa5s.adjust", color="#8a8a8a"))
        btn_theme.setCursor(Qt.PointingHandCursor)
        btn_theme.clicked.connect(self._toggle_theme)
        sidebar_layout.addWidget(btn_theme)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 4, QSizePolicy.Minimum, QSizePolicy.Fixed))

        btn_logout = QPushButton("  Cerrar sesion")
        btn_logout.setIcon(qta.icon("fa5s.sign-out-alt", color="#ffffff"))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_logout.clicked.connect(self.logout_signal.emit)
        sidebar_layout.addWidget(btn_logout)

        layout.addWidget(sidebar)

        # Contenido
        self.stack.addWidget(self._build_empresa_page())
        self.stack.addWidget(self._build_visual_page())
        self.stack.addWidget(self._build_roles_page())
        self.stack.addWidget(self._build_usuarios_page())
        self.stack.addWidget(self._build_auditoria_page())
        self.stack.addWidget(self._build_update_page())
        self.stack.addWidget(self._build_dev_page())
        layout.addWidget(self.stack)

        if self._buttons:
            self._navigate(0)

    def _navigate(self, index: int):
        # Proteger Desarrollador con contrasena almacenada en BD
        if index < len(SUBMODULOS_CONFIG) and SUBMODULOS_CONFIG[index]["codigo"] == "desarrollador":
            from PySide6.QtWidgets import QInputDialog
            pwd, ok = QInputDialog.getText(self, "Acceso Desarrollador", "Contrasena:", QLineEdit.Password)
            if not ok:
                return
            dev_pwd = empresa_service.obtener("dev_password")
            if not dev_pwd:
                QMessageBox.warning(self, "Error", "No hay contrasena configurada. Contacta al desarrollador.")
                return
            if pwd != dev_pwd:
                QMessageBox.warning(self, "Error", "Contrasena incorrecta.")
                return

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
        from ui.manual_uso_view import ManualUsoView, MANUAL_CONFIG
        if not hasattr(self, '_manual_idx'):
            manual = ManualUsoView(MANUAL_CONFIG)
            self._manual_idx = self.stack.addWidget(manual)
        self.stack.setCurrentIndex(self._manual_idx)
        for btn in self._buttons:
            btn.setChecked(False)
            btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # === DATOS EMPRESA ===
    def _build_empresa_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("Datos de la Empresa")
        title.setObjectName("title")
        layout.addWidget(title)

        grp = QGroupBox("Informacion Legal")
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        form = QGridLayout(grp)
        form.setSpacing(8)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        campos = [
            ("Razon Social:", "razon_social", 0, 0),
            ("CUIT:", "cuit", 0, 2),
            ("Direccion:", "direccion_empresa", 1, 0),
            ("Localidad:", "localidad", 1, 2),
            ("Provincia:", "provincia", 2, 0),
            ("Telefono:", "telefono_empresa", 2, 2),
            ("Email:", "email_empresa", 3, 0),
            ("Actividad:", "actividad", 3, 2),
            ("Convenio Colectivo:", "convenio_colectivo", 4, 0),
            ("Nro Establecimiento:", "nro_establecimiento", 4, 2),
        ]

        self._empresa_inputs = {}
        datos = empresa_service.obtener_todos()

        for label, clave, row, col in campos:
            form.addWidget(QLabel(label), row, col)
            inp = QLineEdit()
            inp.setMinimumHeight(32)
            inp.setText(datos.get(clave, ""))
            form.addWidget(inp, row, col + 1)
            self._empresa_inputs[clave] = inp

        layout.addWidget(grp)

        btn = QPushButton("Guardar")
        btn.setMinimumHeight(40)
        btn.clicked.connect(self._guardar_empresa)
        layout.addWidget(btn)

        # Sucursales
        grp_suc = QGroupBox("Sucursales")
        grp_suc.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        suc_layout = QVBoxLayout(grp_suc)

        suc_form = QHBoxLayout()
        suc_form.setSpacing(8)
        suc_form.addWidget(QLabel("Nombre:"))
        self.input_suc_nombre = QLineEdit()
        self.input_suc_nombre.setMinimumHeight(32)
        self.input_suc_nombre.setPlaceholderText("Ej: Sucursal Centro")
        suc_form.addWidget(self.input_suc_nombre)
        suc_form.addWidget(QLabel("Direccion:"))
        self.input_suc_dir = QLineEdit()
        self.input_suc_dir.setMinimumHeight(32)
        suc_form.addWidget(self.input_suc_dir)
        btn_suc = QPushButton("Agregar")
        btn_suc.setMinimumHeight(32)
        btn_suc.clicked.connect(self._agregar_sucursal)
        suc_form.addWidget(btn_suc)
        suc_layout.addLayout(suc_form)

        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        self.tabla_sucursales = QTableWidget()
        self.tabla_sucursales.setColumnCount(3)
        self.tabla_sucursales.setHorizontalHeaderLabels(["Nombre", "Direccion", "Estado"])
        self.tabla_sucursales.horizontalHeader().setStretchLastSection(True)
        self.tabla_sucursales.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_sucursales.setAlternatingRowColors(True)
        self.tabla_sucursales.verticalHeader().setVisible(False)
        self.tabla_sucursales.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_sucursales.setMaximumHeight(150)
        suc_layout.addWidget(self.tabla_sucursales)

        layout.addWidget(grp_suc)
        self._cargar_sucursales()

        layout.addStretch()
        return page

    def _cargar_sucursales(self):
        from PySide6.QtWidgets import QTableWidgetItem
        with get_db() as db:
            sucursales = db.query(Sucursal).order_by(Sucursal.nombre).all()
            self.tabla_sucursales.setRowCount(len(sucursales))
            for i, s in enumerate(sucursales):
                self.tabla_sucursales.setItem(i, 0, QTableWidgetItem(s.nombre))
                self.tabla_sucursales.setItem(i, 1, QTableWidgetItem(s.direccion or ""))
                self.tabla_sucursales.setItem(i, 2, QTableWidgetItem("Activa" if s.activo else "Inactiva"))

    def _agregar_sucursal(self):
        nombre = self.input_suc_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return
        direccion = self.input_suc_dir.text().strip()
        try:
            with get_db() as db:
                db.add(Sucursal(nombre=nombre, direccion=direccion))
            self.input_suc_nombre.clear()
            self.input_suc_dir.clear()
            self._cargar_sucursales()
            QMessageBox.information(self, "OK", f"Sucursal '{nombre}' creada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _guardar_empresa(self):
        datos = {clave: inp.text().strip() for clave, inp in self._empresa_inputs.items()}
        try:
            empresa_service.guardar_multiples(datos)
            QMessageBox.information(self, "OK", "Datos de empresa guardados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === VISUAL ===
    def _build_visual_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("Visual")
        title.setObjectName("title")
        layout.addWidget(title)

        datos = empresa_service.obtener_todos()

        # Nombre comercial
        grp_nombre = QGroupBox("Nombre Comercial")
        grp_nombre.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        nombre_layout = QVBoxLayout(grp_nombre)
        nombre_layout.addWidget(QLabel("Nombre o sobrenombre que se mostrara en la aplicacion."))
        self.input_nombre_app = QLineEdit()
        self.input_nombre_app.setMinimumHeight(36)
        self.input_nombre_app.setPlaceholderText("Ej: Mi Empresa S.A.")
        self.input_nombre_app.setText(datos.get("nombre_app", "Agilize Gestion"))
        nombre_layout.addWidget(self.input_nombre_app)
        layout.addWidget(grp_nombre)

        # Logo
        grp_logo = QGroupBox("Logo de la Empresa")
        grp_logo.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        logo_layout = QHBoxLayout(grp_logo)

        # Preview
        self.lbl_logo_preview = QLabel()
        self.lbl_logo_preview.setFixedSize(120, 120)
        self.lbl_logo_preview.setAlignment(Qt.AlignCenter)
        self.lbl_logo_preview.setStyleSheet("border: 1px solid #333; border-radius: 10px; background-color: #1a1a1a;")
        logo_actual = datos.get("logo_path", "")
        if logo_actual and Path(logo_actual).exists():
            pixmap = QPixmap(logo_actual).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_logo_preview.setPixmap(pixmap)
        logo_layout.addWidget(self.lbl_logo_preview)

        # Info + boton
        logo_info = QVBoxLayout()
        logo_info.setSpacing(8)
        self.lbl_logo_path = QLabel(logo_actual if logo_actual else "Sin logo cargado")
        self.lbl_logo_path.setObjectName("subtitle")
        self.lbl_logo_path.setWordWrap(True)
        logo_info.addWidget(self.lbl_logo_path)
        btn_logo = QPushButton("  Seleccionar imagen")
        btn_logo.setMinimumHeight(36)
        btn_logo.clicked.connect(self._seleccionar_logo)
        logo_info.addWidget(btn_logo)
        logo_info.addStretch()
        logo_layout.addLayout(logo_info)

        layout.addWidget(grp_logo)

        # Guardar
        btn = QPushButton("Guardar")
        btn.setMinimumHeight(40)
        btn.clicked.connect(self._guardar_visual)
        layout.addWidget(btn)
        layout.addStretch()
        return page

    def _seleccionar_logo(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Logo", "", "Imagenes (*.png *.jpg *.jpeg *.svg *.ico)"
        )
        if filepath:
            dest = BASE_DIR / "assets" / "logos" / Path(filepath).name
            shutil.copy2(filepath, str(dest))
            self.lbl_logo_path.setText(str(dest))
            pixmap = QPixmap(str(dest)).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_logo_preview.setPixmap(pixmap)

    def _guardar_visual(self):
        datos = {
            "nombre_app": self.input_nombre_app.text().strip(),
            "logo_path": self.lbl_logo_path.text(),
        }
        try:
            empresa_service.guardar_multiples(datos)
            QMessageBox.information(self, "OK", "Configuracion visual guardada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === DESARROLLADOR ===
    def _build_dev_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("Desarrollador")
        title.setObjectName("title")
        layout.addWidget(title)

        datos = empresa_service.obtener_todos()

        # Datos
        grp_info = QGroupBox("Datos de la Empresa Desarrolladora")
        grp_info.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        form = QGridLayout(grp_info)
        form.setSpacing(8)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        campos_dev = [
            ("Nombre Empresa:", "dev_nombre", 0, 0),
            ("Email:", "dev_email", 0, 2),
            ("Web:", "dev_web", 1, 0),
            ("Telefono:", "dev_telefono", 1, 2),
            ("Direccion:", "dev_direccion", 2, 0),
        ]

        self._dev_inputs = {}
        for label, clave, row, col in campos_dev:
            form.addWidget(QLabel(label), row, col)
            inp = QLineEdit()
            inp.setMinimumHeight(32)
            inp.setText(datos.get(clave, ""))
            form.addWidget(inp, row, col + 1)
            self._dev_inputs[clave] = inp

        layout.addWidget(grp_info)

        # Logo desarrollador
        grp_logo = QGroupBox("Logo del Desarrollador")
        grp_logo.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        logo_layout = QHBoxLayout(grp_logo)

        self.lbl_dev_logo_preview = QLabel()
        self.lbl_dev_logo_preview.setFixedSize(100, 100)
        self.lbl_dev_logo_preview.setAlignment(Qt.AlignCenter)
        self.lbl_dev_logo_preview.setStyleSheet("border: 1px solid #333; border-radius: 10px; background-color: #1a1a1a;")
        dev_logo = datos.get("dev_logo_path", "")
        if dev_logo and Path(dev_logo).exists():
            pixmap = QPixmap(dev_logo).scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_dev_logo_preview.setPixmap(pixmap)
        logo_layout.addWidget(self.lbl_dev_logo_preview)

        logo_info = QVBoxLayout()
        logo_info.setSpacing(8)
        self.lbl_dev_logo_path = QLabel(dev_logo if dev_logo else "Sin logo cargado")
        self.lbl_dev_logo_path.setObjectName("subtitle")
        self.lbl_dev_logo_path.setWordWrap(True)
        logo_info.addWidget(self.lbl_dev_logo_path)
        btn_dev_logo = QPushButton("  Seleccionar imagen")
        btn_dev_logo.setMinimumHeight(36)
        btn_dev_logo.clicked.connect(self._seleccionar_dev_logo)
        logo_info.addWidget(btn_dev_logo)
        logo_info.addStretch()
        logo_layout.addLayout(logo_info)

        layout.addWidget(grp_logo)

        # Guardar
        btn = QPushButton("Guardar")
        btn.setMinimumHeight(40)
        btn.clicked.connect(self._guardar_dev)
        layout.addWidget(btn)

        # Boton reset
        layout.addSpacing(30)

        # Cambiar contrasena dev
        grp_pwd = QGroupBox("Contrasena de Acceso")
        grp_pwd.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        pwd_layout = QHBoxLayout(grp_pwd)
        pwd_layout.addWidget(QLabel("Nueva contrasena:"))
        self.input_dev_pwd = QLineEdit()
        self.input_dev_pwd.setMinimumHeight(32)
        self.input_dev_pwd.setEchoMode(QLineEdit.Password)
        self.input_dev_pwd.setPlaceholderText("Dejar vacio para no cambiar")
        pwd_layout.addWidget(self.input_dev_pwd)
        btn_pwd = QPushButton("Cambiar")
        btn_pwd.setMinimumHeight(32)
        btn_pwd.clicked.connect(self._cambiar_pwd_dev)
        pwd_layout.addWidget(btn_pwd)
        layout.addWidget(grp_pwd)

        btn_reset = QPushButton("  Resetear Aplicacion (borrar datos)")
        btn_reset.setMinimumHeight(40)
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_reset.clicked.connect(self._resetear_app)
        layout.addWidget(btn_reset)

        layout.addStretch()
        return page

    def _seleccionar_dev_logo(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Logo Desarrollador", "", "Imagenes (*.png *.jpg *.jpeg *.svg *.ico)"
        )
        if filepath:
            dest = BASE_DIR / "assets" / "logos" / ("dev_" + Path(filepath).name)
            shutil.copy2(filepath, str(dest))
            self.lbl_dev_logo_path.setText(str(dest))
            pixmap = QPixmap(str(dest)).scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_dev_logo_preview.setPixmap(pixmap)

    def _guardar_dev(self):
        datos = {clave: inp.text().strip() for clave, inp in self._dev_inputs.items()}
        datos["dev_logo_path"] = self.lbl_dev_logo_path.text()
        try:
            empresa_service.guardar_multiples(datos)
            # Actualizar icono de la app en tiempo real
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QIcon
            QApplication.instance().setWindowIcon(QIcon(datos["dev_logo_path"]))
            QMessageBox.information(self, "OK", "Datos del desarrollador guardados. El logo se actualizo.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === USUARIOS ===
    def _build_usuarios_page(self) -> QWidget:
        from modulos.configuracion.views.usuarios_view import UsuariosView
        return UsuariosView()

    # === ROLES ===
    def _build_roles_page(self) -> QWidget:
        from modulos.configuracion.views.roles_view import RolesView
        return RolesView()

    # === AUDITORIA ===
    def _build_auditoria_page(self) -> QWidget:
        from modulos.configuracion.views.audit_view import AuditView
        return AuditView()

    # === ACTUALIZAR ===
    def _build_update_page(self) -> QWidget:
        from modulos.configuracion.views.update_view import UpdateView
        return UpdateView()

    # === RESETEAR ===
    def _cambiar_pwd_dev(self):
        nueva = self.input_dev_pwd.text().strip()
        if not nueva:
            QMessageBox.warning(self, "Error", "Ingresa una contrasena.")
            return
        if len(nueva) < 4:
            QMessageBox.warning(self, "Error", "La contrasena debe tener al menos 4 caracteres.")
            return
        empresa_service.guardar("dev_password", nueva)
        self.input_dev_pwd.clear()
        QMessageBox.information(self, "OK", "Contrasena de desarrollador actualizada.")

    def _resetear_app(self):
        from PySide6.QtWidgets import QMessageBox
        resp = QMessageBox.warning(
            self, "ATENCION - Resetear Aplicacion",
            "Esto eliminara TODOS los datos operativos:\n\n"
            "- Empleados\n"
            "- Asistencias\n"
            "- Liquidaciones\n"
            "- Adelantos\n"
            "- SAC\n"
            "- Cierres\n"
            "- Permisos/Ausencias\n"
            "- Log de auditoria\n\n"
            "Se mantienen: Usuarios, Roles, Configuraciones, Conceptos de Nomina, Feriados.\n\n"
            "Esta accion NO se puede deshacer. Continuar?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        # Doble confirmacion
        resp2 = QMessageBox.critical(
            self, "CONFIRMAR RESET",
            "ULTIMA OPORTUNIDAD\n\nSe perderan todos los datos. Escribi 'RESETEAR' mentalmente y confirma.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp2 != QMessageBox.Yes:
            return

        try:
            from services.reset_service import resetear_aplicacion
            msg = resetear_aplicacion()
            QMessageBox.information(self, "Reseteo Completado", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
