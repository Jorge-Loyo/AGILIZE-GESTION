from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QLineEdit, QPushButton, QLabel, QTabWidget, QFileDialog, QGroupBox,
    QMessageBox, QStackedWidget, QSpacerItem, QSizePolicy, QScrollArea,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage
from pathlib import Path
import base64
import qtawesome as qta
from ui.theme_manager import theme_manager
from services.core.empresa_service import empresa_service
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
            dev_pwd = empresa_service.obtener("dev_password")
            if not dev_pwd:
                # Si no hay contrasena configurada, usar la por defecto
                dev_pwd = "agilize2025"
            pwd, ok = QInputDialog.getText(self, "Acceso Desarrollador", "Contrasena:", QLineEdit.Password)
            if not ok:
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
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        page = QWidget()
        page.setMaximumWidth(750)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(14)

        title = QLabel("Datos de la Empresa")
        title.setObjectName("title")
        layout.addWidget(title)

        GRP_STYLE = "QGroupBox { font-weight: bold; font-size: 12px; padding-top: 14px; margin-top: 4px; }"

        grp = QGroupBox("Informacion Legal")
        grp.setStyleSheet(GRP_STYLE)
        form = QGridLayout(grp)
        form.setSpacing(6)
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
            lbl = QLabel(label)
            lbl.setStyleSheet("font-weight: normal; font-size: 11px; color: #aaa;")
            form.addWidget(lbl, row, col)
            inp = QLineEdit()
            inp.setFixedHeight(28)
            inp.setText(datos.get(clave, ""))
            form.addWidget(inp, row, col + 1)
            self._empresa_inputs[clave] = inp

        layout.addWidget(grp)

        # Boton guardar alineado a la derecha
        save_row = QHBoxLayout()
        save_row.addStretch()
        btn = QPushButton("  Guardar")
        btn.setIcon(qta.icon("fa5s.save", color="#10b981"))
        btn.setFixedHeight(32)
        btn.setFixedWidth(140)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._guardar_empresa)
        save_row.addWidget(btn)
        layout.addLayout(save_row)

        # Pais
        grp_pais = QGroupBox("Pais")
        grp_pais.setStyleSheet(GRP_STYLE)
        pais_layout = QHBoxLayout(grp_pais)
        pais_layout.setSpacing(8)
        lbl_pais = QLabel("Pais de operacion:")
        lbl_pais.setStyleSheet("font-weight: normal; font-size: 11px; color: #aaa;")
        pais_layout.addWidget(lbl_pais)
        self._combo_pais = QComboBox()
        self._combo_pais.setFixedHeight(28)
        self._combo_pais.addItems(["Venezuela", "Argentina"])
        pais_actual = datos.get("cotizacion_pais", "Venezuela")
        idx_pais = self._combo_pais.findText(pais_actual)
        if idx_pais >= 0:
            self._combo_pais.setCurrentIndex(idx_pais)
        pais_layout.addWidget(self._combo_pais)
        pais_layout.addStretch()
        lbl_pais_info = QLabel("Determina IVA, formato de factura e impuestos.")
        lbl_pais_info.setStyleSheet("font-size: 10px; color: #888;")
        pais_layout.addWidget(lbl_pais_info)
        layout.addWidget(grp_pais)

        # Sucursales
        grp_suc = QGroupBox("Sucursales")
        grp_suc.setStyleSheet(GRP_STYLE)
        suc_layout = QVBoxLayout(grp_suc)
        suc_layout.setSpacing(8)

        suc_form = QHBoxLayout()
        suc_form.setSpacing(6)
        lbl_n = QLabel("Nombre:")
        lbl_n.setStyleSheet("font-size: 11px; color: #aaa;")
        suc_form.addWidget(lbl_n)
        self.input_suc_nombre = QLineEdit()
        self.input_suc_nombre.setFixedHeight(28)
        self.input_suc_nombre.setPlaceholderText("Ej: Sucursal Centro")
        suc_form.addWidget(self.input_suc_nombre)
        lbl_d = QLabel("Direccion:")
        lbl_d.setStyleSheet("font-size: 11px; color: #aaa;")
        suc_form.addWidget(lbl_d)
        self.input_suc_dir = QLineEdit()
        self.input_suc_dir.setFixedHeight(28)
        suc_form.addWidget(self.input_suc_dir)
        btn_suc = QPushButton("Agregar")
        btn_suc.setFixedHeight(28)
        btn_suc.setFixedWidth(80)
        btn_suc.setCursor(Qt.PointingHandCursor)
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
        self.tabla_sucursales.setMaximumHeight(130)
        suc_layout.addWidget(self.tabla_sucursales)

        layout.addWidget(grp_suc)
        self._cargar_sucursales()

        layout.addStretch()

        # Centrar
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(page)
        wrapper_layout.addStretch()

        scroll.setWidget(wrapper)
        return scroll

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
        datos["cotizacion_pais"] = self._combo_pais.currentText()
        try:
            empresa_service.guardar_multiples(datos)
            QMessageBox.information(self, "OK", "Datos de empresa guardados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === VISUAL ===
    def _build_visual_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        page = QWidget()
        page.setMaximumWidth(600)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(14)

        title = QLabel("Visual")
        title.setObjectName("title")
        layout.addWidget(title)

        datos = empresa_service.obtener_todos()
        GRP_STYLE = "QGroupBox { font-weight: bold; font-size: 12px; padding-top: 14px; margin-top: 4px; }"

        # Nombre comercial
        grp_nombre = QGroupBox("Nombre Comercial")
        grp_nombre.setStyleSheet(GRP_STYLE)
        nombre_layout = QVBoxLayout(grp_nombre)
        nombre_layout.setSpacing(6)
        lbl_hint = QLabel("Nombre que se muestra en la aplicacion y recibos.")
        lbl_hint.setStyleSheet("font-size: 11px; color: #888; font-weight: normal;")
        nombre_layout.addWidget(lbl_hint)
        self.input_nombre_app = QLineEdit()
        self.input_nombre_app.setFixedHeight(30)
        self.input_nombre_app.setPlaceholderText("Ej: Mi Empresa S.A.")
        self.input_nombre_app.setText(datos.get("nombre_app", "Agilize Gestion"))
        nombre_layout.addWidget(self.input_nombre_app)
        layout.addWidget(grp_nombre)

        # Logo
        grp_logo = QGroupBox("Logo de la Empresa")
        grp_logo.setStyleSheet(GRP_STYLE)
        logo_layout = QHBoxLayout(grp_logo)
        logo_layout.setSpacing(14)

        self.lbl_logo_preview = QLabel()
        self.lbl_logo_preview.setFixedSize(80, 80)
        self.lbl_logo_preview.setAlignment(Qt.AlignCenter)
        self.lbl_logo_preview.setStyleSheet("border: 1px solid #333; border-radius: 10px; background-color: #1a1a1a;")
        self._cargar_logo_preview(datos)
        logo_layout.addWidget(self.lbl_logo_preview)

        logo_info = QVBoxLayout()
        logo_info.setSpacing(6)
        self.lbl_logo_status = QLabel("Logo cargado" if datos.get("logo_base64") else "Sin logo cargado")
        self.lbl_logo_status.setObjectName("subtitle")
        self.lbl_logo_status.setWordWrap(True)
        logo_info.addWidget(self.lbl_logo_status)
        btn_logo = QPushButton("  Seleccionar imagen")
        btn_logo.setFixedHeight(28)
        btn_logo.setFixedWidth(160)
        btn_logo.setCursor(Qt.PointingHandCursor)
        btn_logo.clicked.connect(self._seleccionar_logo)
        logo_info.addWidget(btn_logo)
        logo_info.addStretch()
        logo_layout.addLayout(logo_info)

        layout.addWidget(grp_logo)

        # Guardar alineado a la derecha
        save_row = QHBoxLayout()
        save_row.addStretch()
        btn = QPushButton("  Guardar")
        btn.setIcon(qta.icon("fa5s.save", color="#10b981"))
        btn.setFixedHeight(32)
        btn.setFixedWidth(140)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._guardar_visual)
        save_row.addWidget(btn)
        layout.addLayout(save_row)

        layout.addStretch()

        # Centrar
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(page)
        wrapper_layout.addStretch()

        scroll.setWidget(wrapper)
        return scroll

    def _seleccionar_logo(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Logo", "", "Imagenes (*.png *.jpg *.jpeg *.ico)"
        )
        if filepath:
            with open(filepath, "rb") as f:
                img_bytes = f.read()
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            empresa_service.guardar("logo_base64", b64)
            pixmap = QPixmap(filepath).scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_logo_preview.setPixmap(pixmap)
            self.lbl_logo_status.setText("Logo cargado")
            QMessageBox.information(self, "OK", "Logo guardado en base de datos.")

    def _cargar_logo_preview(self, datos: dict):
        b64 = datos.get("logo_base64", "")
        if b64:
            img_bytes = base64.b64decode(b64)
            img = QImage()
            img.loadFromData(img_bytes)
            pixmap = QPixmap.fromImage(img).scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_logo_preview.setPixmap(pixmap)

    def _guardar_visual(self):
        datos = {
            "nombre_app": self.input_nombre_app.text().strip(),
        }
        try:
            empresa_service.guardar_multiples(datos)
            QMessageBox.information(self, "OK", "Configuracion visual guardada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === DESARROLLADOR ===
    def _build_dev_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        page = QWidget()
        page.setMaximumWidth(700)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(14)

        title = QLabel("Desarrollador")
        title.setObjectName("title")
        layout.addWidget(title)

        datos = empresa_service.obtener_todos()
        GRP_STYLE = "QGroupBox { font-weight: bold; font-size: 12px; padding-top: 14px; margin-top: 4px; }"

        # --- Datos + Logo en un mismo grupo ---
        grp_info = QGroupBox("Empresa Desarrolladora")
        grp_info.setStyleSheet(GRP_STYLE)
        info_main = QVBoxLayout(grp_info)
        info_main.setSpacing(10)

        # Logo inline con datos
        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        self.lbl_dev_logo_preview = QLabel()
        self.lbl_dev_logo_preview.setFixedSize(56, 56)
        self.lbl_dev_logo_preview.setAlignment(Qt.AlignCenter)
        self.lbl_dev_logo_preview.setStyleSheet("border: 1px solid #333; border-radius: 8px; background-color: #1a1a1a;")
        self._cargar_dev_logo_preview(datos)
        top_row.addWidget(self.lbl_dev_logo_preview)

        self.lbl_dev_logo_status = QLabel("Logo cargado" if datos.get("dev_logo_base64") else "Sin logo")
        self.lbl_dev_logo_status.setObjectName("subtitle")
        top_row.addWidget(self.lbl_dev_logo_status, 1)

        btn_dev_logo = QPushButton("Cambiar logo")
        btn_dev_logo.setFixedHeight(30)
        btn_dev_logo.setFixedWidth(110)
        btn_dev_logo.setCursor(Qt.PointingHandCursor)
        btn_dev_logo.clicked.connect(self._seleccionar_dev_logo)
        top_row.addWidget(btn_dev_logo)

        info_main.addLayout(top_row)

        # Formulario
        form = QGridLayout()
        form.setSpacing(6)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        campos_dev = [
            ("Nombre:", "dev_nombre", 0, 0),
            ("Email:", "dev_email", 0, 2),
            ("Web:", "dev_web", 1, 0),
            ("Telefono:", "dev_telefono", 1, 2),
            ("Direccion:", "dev_direccion", 2, 0),
        ]

        self._dev_inputs = {}
        for label, clave, row, col in campos_dev:
            lbl = QLabel(label)
            lbl.setStyleSheet("font-weight: normal; font-size: 11px; color: #aaa;")
            form.addWidget(lbl, row, col)
            inp = QLineEdit()
            inp.setFixedHeight(28)
            inp.setText(datos.get(clave, ""))
            form.addWidget(inp, row, col + 1)
            self._dev_inputs[clave] = inp

        info_main.addLayout(form)

        # Boton guardar alineado a la derecha
        save_row = QHBoxLayout()
        save_row.addStretch()
        btn_guardar = QPushButton("  Guardar")
        btn_guardar.setIcon(qta.icon("fa5s.save", color="#10b981"))
        btn_guardar.setFixedHeight(32)
        btn_guardar.setFixedWidth(140)
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.clicked.connect(self._guardar_dev)
        save_row.addWidget(btn_guardar)
        info_main.addLayout(save_row)

        layout.addWidget(grp_info)

        # --- Pais del Producto ---
        grp_pais = QGroupBox("Pais del Producto")
        grp_pais.setStyleSheet(GRP_STYLE)
        pais_layout = QVBoxLayout(grp_pais)
        pais_layout.setSpacing(8)

        pais_hint = QLabel("Define moneda, impuestos y conceptos de nomina del sistema.")
        pais_hint.setStyleSheet("font-size: 10px; color: #888; font-weight: normal;")
        pais_layout.addWidget(pais_hint)

        pais_row = QHBoxLayout()
        pais_row.setSpacing(8)
        lbl_pais_dev = QLabel("Pais:")
        lbl_pais_dev.setStyleSheet("font-weight: normal; font-size: 11px; color: #aaa;")
        pais_row.addWidget(lbl_pais_dev)
        self._combo_pais_dev = QComboBox()
        self._combo_pais_dev.setFixedHeight(28)
        self._combo_pais_dev.setFixedWidth(180)
        self._combo_pais_dev.addItems(["Venezuela", "Argentina"])
        pais_actual = datos.get("cotizacion_pais", "Argentina")
        idx_p = self._combo_pais_dev.findText(pais_actual)
        if idx_p >= 0:
            self._combo_pais_dev.setCurrentIndex(idx_p)
        pais_row.addWidget(self._combo_pais_dev)

        self._lbl_moneda_info = QLabel()
        self._lbl_moneda_info.setStyleSheet("font-size: 10px; color: #D4AF37;")
        self._actualizar_info_moneda()
        self._combo_pais_dev.currentTextChanged.connect(self._actualizar_info_moneda)
        pais_row.addWidget(self._lbl_moneda_info)
        pais_row.addStretch()

        btn_aplicar_pais = QPushButton("  Aplicar")
        btn_aplicar_pais.setIcon(qta.icon("fa5s.globe", color="#10b981"))
        btn_aplicar_pais.setFixedHeight(28)
        btn_aplicar_pais.setFixedWidth(100)
        btn_aplicar_pais.setCursor(Qt.PointingHandCursor)
        btn_aplicar_pais.clicked.connect(self._aplicar_pais)
        pais_row.addWidget(btn_aplicar_pais)
        pais_layout.addLayout(pais_row)

        layout.addWidget(grp_pais)

        # --- Contrasena de acceso ---
        grp_pwd = QGroupBox("Contrasena de Acceso al Panel")
        grp_pwd.setStyleSheet(GRP_STYLE)
        pwd_layout = QHBoxLayout(grp_pwd)
        pwd_layout.setSpacing(8)
        lbl_pwd = QLabel("Nueva:")
        lbl_pwd.setFixedWidth(50)
        pwd_layout.addWidget(lbl_pwd)
        self.input_dev_pwd = QLineEdit()
        self.input_dev_pwd.setFixedHeight(28)
        self.input_dev_pwd.setEchoMode(QLineEdit.Password)
        self.input_dev_pwd.setPlaceholderText("Dejar vacio para no cambiar")
        pwd_layout.addWidget(self.input_dev_pwd)
        btn_pwd = QPushButton("Cambiar")
        btn_pwd.setFixedHeight(28)
        btn_pwd.setFixedWidth(90)
        btn_pwd.setCursor(Qt.PointingHandCursor)
        btn_pwd.clicked.connect(self._cambiar_pwd_dev)
        pwd_layout.addWidget(btn_pwd)
        layout.addWidget(grp_pwd)

        # --- Backup ---
        grp_backup = QGroupBox("Backup de Base de Datos")
        grp_backup.setStyleSheet(GRP_STYLE)
        backup_layout = QVBoxLayout(grp_backup)
        backup_layout.setSpacing(8)

        backup_btns = QHBoxLayout()
        backup_btns.setSpacing(6)

        btn_crear_backup = QPushButton("  Crear")
        btn_crear_backup.setIcon(qta.icon("fa5s.database", color="#10b981"))
        btn_crear_backup.setFixedHeight(32)
        btn_crear_backup.setCursor(Qt.PointingHandCursor)
        btn_crear_backup.clicked.connect(self._crear_backup)
        backup_btns.addWidget(btn_crear_backup)

        btn_exportar_backup = QPushButton("  Exportar a...")
        btn_exportar_backup.setIcon(qta.icon("fa5s.file-export", color="#D4AF37"))
        btn_exportar_backup.setFixedHeight(32)
        btn_exportar_backup.setCursor(Qt.PointingHandCursor)
        btn_exportar_backup.clicked.connect(self._exportar_backup)
        backup_btns.addWidget(btn_exportar_backup)

        btn_restaurar_backup = QPushButton("  Restaurar")
        btn_restaurar_backup.setIcon(qta.icon("fa5s.upload", color="#3b82f6"))
        btn_restaurar_backup.setFixedHeight(32)
        btn_restaurar_backup.setCursor(Qt.PointingHandCursor)
        btn_restaurar_backup.clicked.connect(self._restaurar_backup)
        backup_btns.addWidget(btn_restaurar_backup)

        backup_layout.addLayout(backup_btns)

        self.lbl_backup_info = QLabel("")
        self.lbl_backup_info.setObjectName("subtitle")
        self.lbl_backup_info.setWordWrap(True)
        backup_layout.addWidget(self.lbl_backup_info)

        layout.addWidget(grp_backup)

        # --- Zona peligrosa ---
        layout.addSpacing(10)
        grp_danger = QGroupBox("Zona Peligrosa")
        grp_danger.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; padding-top: 14px; margin-top: 4px; color: #ef4444; }")
        danger_layout = QHBoxLayout(grp_danger)
        danger_layout.addWidget(QLabel("Elimina todos los datos operativos. No se puede deshacer."))
        danger_layout.addStretch()
        btn_reset = QPushButton("  Resetear")
        btn_reset.setIcon(qta.icon("fa5s.exclamation-triangle", color="#ffffff"))
        btn_reset.setFixedHeight(32)
        btn_reset.setFixedWidth(130)
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_reset.clicked.connect(self._resetear_app)
        danger_layout.addWidget(btn_reset)
        layout.addWidget(grp_danger)

        layout.addStretch()

        # Centrar el contenido en el scroll
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(page)
        wrapper_layout.addStretch()

        scroll.setWidget(wrapper)
        return scroll

    def _cargar_dev_logo_preview(self, datos: dict):
        b64 = datos.get("dev_logo_base64", "")
        if b64:
            img_bytes = base64.b64decode(b64)
            img = QImage()
            img.loadFromData(img_bytes)
            pixmap = QPixmap.fromImage(img).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_dev_logo_preview.setPixmap(pixmap)

    def _seleccionar_dev_logo(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Logo Desarrollador", "", "Imagenes (*.png *.jpg *.jpeg *.ico)"
        )
        if filepath:
            with open(filepath, "rb") as f:
                img_bytes = f.read()
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            empresa_service.guardar("dev_logo_base64", b64)
            pixmap = QPixmap(filepath).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_dev_logo_preview.setPixmap(pixmap)
            self.lbl_dev_logo_status.setText("Logo cargado")
            QMessageBox.information(self, "OK", "Logo desarrollador guardado en base de datos.")

    def _actualizar_info_moneda(self, pais=None):
        from services.core.pais_config_service import PAISES
        pais = (pais or self._combo_pais_dev.currentText()).lower().strip()
        config = PAISES.get(pais, {})
        if config:
            self._lbl_moneda_info.setText(
                f"Moneda: {config['moneda_local']} / {config['moneda_extranjera']}  |  "
                f"IVA: {config['iva']}%  |  ID Fiscal: {config['id_fiscal_empresa']}"
            )

    def _aplicar_pais(self):
        pais = self._combo_pais_dev.currentText()
        resp = QMessageBox.question(
            self, "Aplicar Pais",
            f"Se configurara el sistema para: {pais}\n\n"
            f"Esto actualizara:\n"
            f"- Moneda local y extranjera\n"
            f"- Conceptos de nomina (se desactivan los del pais anterior)\n"
            f"- IVA y formato fiscal\n\n"
            f"Continuar?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return
        try:
            from services.core.pais_config_service import pais_config_service
            pais_config_service.aplicar_pais(pais)
            QMessageBox.information(self, "OK",
                f"Sistema configurado para {pais}.\n"
                f"Los conceptos de nomina fueron actualizados."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _guardar_dev(self):
        datos = {clave: inp.text().strip() for clave, inp in self._dev_inputs.items()}
        try:
            empresa_service.guardar_multiples(datos)
            QMessageBox.information(self, "OK", "Datos del desarrollador guardados.")
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

    def _crear_backup(self):
        try:
            from services.core.backup_service import crear_backup
            filepath = crear_backup()
            self.lbl_backup_info.setText(f"Backup creado: {filepath}")
            QMessageBox.information(self, "Backup", f"Backup creado exitosamente:\n\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el backup:\n\n{str(e)}")

    def _exportar_backup(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Guardar Backup", f"backup_agilize_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.sql",
            "SQL Files (*.sql);;Todos (*)"
        )
        if not filepath:
            return
        try:
            from services.core.backup_service import crear_backup
            result = crear_backup(destino=filepath)
            self.lbl_backup_info.setText(f"Exportado: {result}")
            QMessageBox.information(self, "Backup", f"Backup exportado a:\n\n{result}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar:\n\n{str(e)}")

    def _restaurar_backup(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Backup", "", "SQL Files (*.sql);;Todos (*)"
        )
        if not filepath:
            return
        resp = QMessageBox.warning(
            self, "Restaurar Backup",
            f"Se restaurara el backup:\n{filepath}\n\n"
            "Esto puede sobrescribir datos actuales.\nContinuar?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return
        try:
            from services.core.backup_service import restaurar_backup
            msg = restaurar_backup(filepath)
            self.lbl_backup_info.setText(f"Restaurado: {filepath}")
            QMessageBox.information(self, "Backup", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al restaurar:\n\n{str(e)}")

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
            from services.core.reset_service import resetear_aplicacion
            msg = resetear_aplicacion()
            QMessageBox.information(self, "Reseteo Completado", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
