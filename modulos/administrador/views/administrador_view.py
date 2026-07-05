"""
Modulo Administrador - Tablas maestras organizadas por modulo.
Sidebar con botones por modulo que despliegan sub-opciones.
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QPushButton, QLabel, QStackedWidget, QSpacerItem, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QInputDialog, QCheckBox, QDialog, QFormLayout, QLineEdit,
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
from ui.theme_manager import theme_manager


# Estructura: modulo -> [submodulos]
GRUPOS_ADMIN = [
    {
        "grupo": "Sistema",
        "icon": "fa5s.shield-alt",
        "items": [
            {"codigo": "adm_usuarios", "label": "Usuarios", "icon": "fa5s.user-cog"},
            {"codigo": "adm_roles", "label": "Roles y Permisos", "icon": "fa5s.user-shield"},
        ],
    },
    {
        "grupo": "Inventario",
        "icon": "fa5s.boxes",
        "items": [
            {"codigo": "adm_productos", "label": "Productos", "icon": "fa5s.box"},
            {"codigo": "adm_categorias", "label": "Categorias", "icon": "fa5s.tags"},
            {"codigo": "adm_depositos", "label": "Depositos", "icon": "fa5s.warehouse"},
        ],
    },
    {
        "grupo": "Comercial",
        "icon": "fa5s.handshake",
        "items": [
            {"codigo": "adm_clientes", "label": "Clientes", "icon": "fa5s.user-tie"},
            {"codigo": "adm_proveedores", "label": "Proveedores", "icon": "fa5s.truck"},
            {"codigo": "adm_facturadores", "label": "Facturadores", "icon": "fa5s.cash-register"},
        ],
    },
    {
        "grupo": "Empresa",
        "icon": "fa5s.building",
        "items": [
            {"codigo": "adm_sucursales", "label": "Sucursales", "icon": "fa5s.store"},
            {"codigo": "adm_departamentos", "label": "Departamentos", "icon": "fa5s.sitemap"},
            {"codigo": "adm_cargos", "label": "Cargos", "icon": "fa5s.id-badge"},
            {"codigo": "adm_tipos_compra", "label": "Tipos de Compra", "icon": "fa5s.shopping-basket"},
        ],
    },
    {
        "grupo": "Finanzas",
        "icon": "fa5s.coins",
        "items": [
            {"codigo": "adm_cuentas_banco", "label": "Bancos", "icon": "fa5s.university"},
            {"codigo": "adm_plan_cuentas", "label": "Plan de Cuentas", "icon": "fa5s.book"},
        ],
    },
]


class AdministradorView(QWidget):
    volver_dashboard = Signal()
    logout_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grupo_buttons: list[QPushButton] = []
        self._item_buttons: list[QPushButton] = []
        self._pages: dict[str, int] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === SIDEBAR PRINCIPAL (modulos) ===
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 16, 10, 16)
        sidebar_layout.setSpacing(4)

        btn_volver = QPushButton("  Menu")
        btn_volver.setIcon(qta.icon("fa5s.arrow-left", color="#8a8a8a"))
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.setStyleSheet("QPushButton { background-color: transparent; color: #8a8a8a; border: none; text-align: left; padding: 8px 10px; } QPushButton:hover { color: #F8F9FA; }")
        btn_volver.clicked.connect(self.volver_dashboard.emit)
        sidebar_layout.addWidget(btn_volver)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))
        lbl = QLabel("Administrador")
        lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #D4AF37;")
        lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl)
        sidebar_layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Botones por grupo
        for i, grupo in enumerate(GRUPOS_ADMIN):
            btn = QPushButton(f"  {grupo['grupo']}")
            btn.setIcon(qta.icon(grupo["icon"], color="#8a8a8a"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton { text-align: left; padding: 7px 10px; border-radius: 4px; }
                QPushButton:checked { background-color: #D4AF37; color: #0f0f0f; }
            """)
            btn.clicked.connect(lambda checked, idx=i: self._select_grupo(idx))
            sidebar_layout.addWidget(btn)
            self._grupo_buttons.append(btn)

        sidebar_layout.addStretch()
        btn_theme = QPushButton("  Modo")
        btn_theme.setIcon(qta.icon("fa5s.adjust", color="#8a8a8a"))
        btn_theme.setCursor(Qt.PointingHandCursor)
        btn_theme.setStyleSheet("QPushButton { background-color: transparent; color: #8a8a8a; border: none; padding: 6px 10px; } QPushButton:hover { color: #F8F9FA; }")
        btn_theme.clicked.connect(lambda: theme_manager.toggle(__import__('PySide6.QtWidgets', fromlist=['QApplication']).QApplication.instance()))
        sidebar_layout.addWidget(btn_theme)
        btn_logout = QPushButton("  Salir")
        btn_logout.setIcon(qta.icon("fa5s.sign-out-alt", color="#000000"))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("QPushButton { background-color: #ef4444; color: #000000; padding: 6px 10px; } QPushButton:hover { background-color: #dc2626; }")
        btn_logout.clicked.connect(self.logout_signal.emit)
        sidebar_layout.addWidget(btn_logout)

        layout.addWidget(sidebar)

        # === SUB-SIDEBAR (opciones del grupo) ===
        self._sub_sidebar = QFrame()
        self._sub_sidebar.setObjectName("sub_sidebar")
        self._sub_sidebar.setFixedWidth(160)
        self._sub_layout = QVBoxLayout(self._sub_sidebar)
        self._sub_layout.setContentsMargins(8, 16, 8, 16)
        self._sub_layout.setSpacing(3)
        self._sub_layout.addStretch()
        layout.addWidget(self._sub_sidebar)

        # === CONTENIDO ===
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Placeholder inicial
        placeholder = QWidget()
        p_lay = QVBoxLayout(placeholder)
        p_lay.setAlignment(Qt.AlignCenter)
        lbl_p = QLabel("Seleccione un grupo y una opcion")
        lbl_p.setStyleSheet("font-size: 14px; color: #666;")
        p_lay.addWidget(lbl_p)
        self.stack.addWidget(placeholder)

        # Seleccionar primer grupo
        if self._grupo_buttons:
            self._select_grupo(0)

    def _select_grupo(self, idx: int):
        # Marcar botón activo
        for i, btn in enumerate(self._grupo_buttons):
            btn.setChecked(i == idx)

        # Limpiar sub-sidebar
        while self._sub_layout.count():
            child = self._sub_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._item_buttons.clear()

        # Titulo del grupo
        grupo = GRUPOS_ADMIN[idx]
        lbl = QLabel(grupo["grupo"])
        lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #D4AF37; padding: 4px 6px;")
        self._sub_layout.addWidget(lbl)

        # Botones de items
        for item in grupo["items"]:
            btn = QPushButton(f"  {item['label']}")
            btn.setIcon(qta.icon(item["icon"], color="#888"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(28)
            btn.setObjectName("sub_sidebar_btn")
            btn.clicked.connect(lambda checked, c=item["codigo"]: self._open_item(c))
            self._sub_layout.addWidget(btn)
            self._item_buttons.append(btn)

        self._sub_layout.addStretch()

        # Auto-abrir primer item
        if grupo["items"]:
            self._open_item(grupo["items"][0]["codigo"])

    def _open_item(self, codigo: str):
        # Marcar botón activo en sub-sidebar
        for btn in self._item_buttons:
            btn.setChecked(btn.text().strip() in [item["label"] for g in GRUPOS_ADMIN for item in g["items"] if item["codigo"] == codigo])

        if codigo not in self._pages:
            page = self._create_submodule(codigo)
            idx = self.stack.addWidget(page)
            self._pages[codigo] = idx
        self.stack.setCurrentIndex(self._pages[codigo])

    def _create_submodule(self, codigo: str) -> QWidget:
        if codigo == "adm_usuarios":
            from modulos.configuracion.views.usuarios_view import UsuariosView
            return UsuariosView()
        if codigo == "adm_roles":
            return self._roles_permisos_view()
        if codigo == "adm_productos":
            from modulos.inventario.views.productos_view import ProductosView
            return ProductosView()
        if codigo == "adm_categorias":
            return self._simple_crud("Categorias de Producto", "categorias_producto", ["nombre", "descripcion"])
        if codigo == "adm_depositos":
            from modulos.inventario.views.depositos_view import DepositosView
            return DepositosView()
        if codigo == "adm_clientes":
            from modulos.datos.views.clientes_view import ClientesView
            return ClientesView()
        if codigo == "adm_proveedores":
            from modulos.datos.views.proveedores_view import ProveedoresView
            return ProveedoresView()
        if codigo == "adm_sucursales":
            return self._simple_crud("Sucursales", "sucursales", ["nombre", "direccion", "telefono"])
        if codigo == "adm_departamentos":
            return self._simple_crud("Departamentos", "departamentos", ["nombre"])
        if codigo == "adm_cargos":
            return self._simple_crud("Cargos", "cargos", ["nombre"])
        if codigo == "adm_facturadores":
            from modulos.ventas.views.config_facturadores_view import ConfigFacturadoresView
            return ConfigFacturadoresView()
        if codigo == "adm_cuentas_banco":
            from modulos.finanzas.views.bancos_view import BancosView
            return BancosView()
        if codigo == "adm_tipos_compra":
            return self._simple_crud("Tipos de Compra", "tipos_compra", ["nombre", "descripcion"])
        if codigo == "adm_plan_cuentas":
            from modulos.finanzas.views.contabilidad_view import ContabilidadView
            return ContabilidadView()
        return QWidget()

    def _simple_crud(self, titulo: str, tabla: str, campos: list) -> QWidget:
        """Genera vista CRUD generica para tablas simples."""
        from core.database import get_db
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel(titulo)
        t.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        header.addWidget(t)
        header.addStretch()
        btn = QPushButton("  Nuevo")
        btn.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn.setFixedHeight(32)
        header.addWidget(btn)
        lay.addLayout(header)

        tw = QTableWidget()
        tw.setColumnCount(len(campos))
        tw.setHorizontalHeaderLabels([c.capitalize() for c in campos])
        tw.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tw.setAlternatingRowColors(True)
        tw.verticalHeader().setVisible(False)
        tw.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(tw)

        def cargar():
            with get_db() as db:
                from sqlalchemy import text
                rows = db.execute(text(f"SELECT {','.join(campos)} FROM {tabla} WHERE activo=true ORDER BY {campos[0]}")).fetchall()
                tw.setRowCount(len(rows))
                for i, row in enumerate(rows):
                    for j, val in enumerate(row):
                        tw.setItem(i, j, QTableWidgetItem(str(val or "")))

        def nuevo():
            nombre, ok = QInputDialog.getText(page, f"Nuevo {titulo}", f"{campos[0].capitalize()}:")
            if ok and nombre.strip():
                with get_db() as db:
                    from sqlalchemy import text
                    db.execute(text(f"INSERT INTO {tabla} ({campos[0]}, activo) VALUES (:v, true)"), {"v": nombre.strip()})
                cargar()

        btn.clicked.connect(nuevo)
        cargar()
        return page

    def _roles_permisos_view(self) -> QWidget:
        """Vista de roles con matriz de permisos por modulo."""
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel("Roles y Permisos")
        t.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        header.addWidget(t)
        header.addStretch()
        btn_nuevo = QPushButton("  Nuevo Rol")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(32)
        header.addWidget(btn_nuevo)
        lay.addLayout(header)

        info = QLabel("Configura que puede hacer cada rol en cada modulo del sistema.")
        info.setStyleSheet("font-size: 11px; color: #888;")
        lay.addWidget(info)

        # Tabla de roles existentes
        from PySide6.QtWidgets import QTabWidget
        tabs = QTabWidget()
        tabs.addTab(self._build_lista_roles(), "Roles")
        tabs.addTab(self._build_matriz_permisos(), "Matriz de Permisos")
        lay.addWidget(tabs)

        def nuevo_rol():
            dlg = QDialog(page)
            dlg.setWindowTitle("Nuevo Rol")
            dlg.setMinimumWidth(350)
            d_lay = QVBoxLayout(dlg)
            form = QFormLayout()
            inp_n = QLineEdit()
            inp_n.setMaxLength(50)
            form.addRow("Nombre:", inp_n)
            inp_d = QLineEdit()
            inp_d.setMaxLength(200)
            form.addRow("Descripcion:", inp_d)
            d_lay.addLayout(form)
            btn_ok = QPushButton("Crear")
            btn_ok.clicked.connect(dlg.accept)
            d_lay.addWidget(btn_ok)
            if dlg.exec() == QDialog.Accepted and inp_n.text().strip():
                from core.database import get_db
                from models.rol import Rol
                with get_db() as db:
                    db.add(Rol(nombre=inp_n.text().strip(), descripcion=inp_d.text().strip(), activo=True))
                self._cargar_roles_tabla()

        btn_nuevo.clicked.connect(nuevo_rol)
        return page

    def _build_lista_roles(self) -> QWidget:
        """Tab con lista de roles editables."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)

        self._tabla_roles = QTableWidget()
        self._tabla_roles.setColumnCount(5)
        self._tabla_roles.setHorizontalHeaderLabels(["ID", "Nombre", "Descripcion", "Activo", ""])
        self._tabla_roles.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._tabla_roles.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self._tabla_roles.setColumnWidth(4, 80)
        self._tabla_roles.setColumnHidden(0, True)
        self._tabla_roles.setAlternatingRowColors(True)
        self._tabla_roles.verticalHeader().setVisible(False)
        self._tabla_roles.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_roles.setSelectionBehavior(QTableWidget.SelectRows)
        lay.addWidget(self._tabla_roles)

        btns = QHBoxLayout()
        btn_editar = QPushButton("  Editar")
        btn_editar.setIcon(qta.icon("fa5s.edit", color="#3b82f6"))
        btn_editar.setFixedHeight(28)
        btn_editar.clicked.connect(self._editar_rol)
        btns.addWidget(btn_editar)
        btn_toggle = QPushButton("  Activar/Desactivar")
        btn_toggle.setFixedHeight(28)
        btn_toggle.clicked.connect(self._toggle_rol)
        btns.addWidget(btn_toggle)
        btns.addStretch()
        lay.addLayout(btns)

        self._cargar_roles_tabla()
        return w

    def _cargar_roles_tabla(self):
        from core.database import get_db
        from models.rol import Rol
        with get_db() as db:
            roles = db.query(Rol).order_by(Rol.id).all()
            self._roles_data = [(r.id, r.nombre, r.descripcion, r.activo) for r in roles]
        self._tabla_roles.setRowCount(len(self._roles_data))
        for i, (rid, nombre, desc, activo) in enumerate(self._roles_data):
            self._tabla_roles.setItem(i, 0, QTableWidgetItem(str(rid)))
            self._tabla_roles.setItem(i, 1, QTableWidgetItem(nombre))
            self._tabla_roles.setItem(i, 2, QTableWidgetItem(desc or ""))
            estado = QTableWidgetItem("Activo" if activo else "Inactivo")
            if not activo:
                estado.setForeground(__import__('PySide6.QtCore', fromlist=['Qt']).Qt.red)
            self._tabla_roles.setItem(i, 3, estado)
            # Proteger Administrador
            if rid == 1:
                self._tabla_roles.setItem(i, 4, QTableWidgetItem("(protegido)"))
            else:
                self._tabla_roles.setItem(i, 4, QTableWidgetItem(""))

    def _editar_rol(self):
        row = self._tabla_roles.currentRow()
        if row < 0:
            return
        rid = int(self._tabla_roles.item(row, 0).text())
        if rid == 1:
            QMessageBox.warning(None, "Aviso", "El rol Administrador no se puede editar.")
            return
        nombre_actual = self._tabla_roles.item(row, 1).text()
        desc_actual = self._tabla_roles.item(row, 2).text()

        dlg = QDialog()
        dlg.setWindowTitle("Editar Rol")
        dlg.setMinimumWidth(350)
        d_lay = QVBoxLayout(dlg)
        form = QFormLayout()
        inp_n = QLineEdit(nombre_actual)
        inp_n.setMaxLength(50)
        form.addRow("Nombre:", inp_n)
        inp_d = QLineEdit(desc_actual)
        inp_d.setMaxLength(200)
        form.addRow("Descripcion:", inp_d)
        d_lay.addLayout(form)
        btn_ok = QPushButton("Guardar")
        btn_ok.clicked.connect(dlg.accept)
        d_lay.addWidget(btn_ok)
        if dlg.exec() == QDialog.Accepted and inp_n.text().strip():
            from core.database import get_db
            from models.rol import Rol
            with get_db() as db:
                rol = db.get(Rol, rid)
                if rol:
                    rol.nombre = inp_n.text().strip()
                    rol.descripcion = inp_d.text().strip()
            self._cargar_roles_tabla()

    def _toggle_rol(self):
        row = self._tabla_roles.currentRow()
        if row < 0:
            return
        rid = int(self._tabla_roles.item(row, 0).text())
        if rid == 1:
            QMessageBox.warning(None, "Aviso", "El rol Administrador no se puede desactivar.")
            return
        from core.database import get_db
        from models.rol import Rol
        with get_db() as db:
            rol = db.get(Rol, rid)
            if rol:
                rol.activo = not rol.activo
        self._cargar_roles_tabla()

    def _build_matriz_permisos(self) -> QWidget:
        """Tab con matriz de permisos: selector de rol + tabla modulo x acciones."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        # Selector de rol
        row_sel = QHBoxLayout()
        row_sel.addWidget(QLabel("Rol:"))
        self._combo_rol_permisos = __import__('PySide6.QtWidgets', fromlist=['QComboBox']).QComboBox()
        self._combo_rol_permisos.setFixedHeight(30)
        self._combo_rol_permisos.setMinimumWidth(200)
        row_sel.addWidget(self._combo_rol_permisos)
        row_sel.addStretch()
        self._lbl_rol_info = QLabel("")
        self._lbl_rol_info.setStyleSheet("font-size: 11px; color: #888;")
        row_sel.addWidget(self._lbl_rol_info)
        lay.addLayout(row_sel)

        info = QLabel("Marca las acciones permitidas para este rol en cada modulo. Los cambios se guardan automaticamente.")
        info.setStyleSheet("font-size: 11px; color: #666;")
        lay.addWidget(info)

        # Tabla: filas=modulos, columnas=VER/CREAR/EDITAR/ELIMINAR
        self._tabla_matriz = QTableWidget()
        self._tabla_matriz.setColumnCount(5)
        self._tabla_matriz.setHorizontalHeaderLabels(["Modulo", "Ver", "Crear", "Editar", "Eliminar"])
        self._tabla_matriz.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 5):
            self._tabla_matriz.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
            self._tabla_matriz.setColumnWidth(col, 80)
        self._tabla_matriz.setAlternatingRowColors(True)
        self._tabla_matriz.verticalHeader().setVisible(False)
        self._tabla_matriz.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._tabla_matriz, 1)

        # Definir modulos
        self._MODULOS_PERMISOS = [
            ("compras", "Compras"), ("inventario", "Inventario"), ("ventas", "Ventas"),
            ("facturador", "Facturador"), ("empleados", "RRHH"), ("cuentas", "Cuentas"),
            ("finanzas", "Finanzas"), ("reportes", "Reportes"), ("herramientas", "Herramientas"),
            ("importador", "Importador"), ("administrador", "Administrador"), ("admin", "Configuracion"),
        ]
        self._ACCIONES_PERMISOS = ["ver", "crear", "editar", "eliminar"]

        # Asegurar permisos en BD y cargar mapa
        self._asegurar_permisos_bd()

        # Cargar roles en combo
        self._cargar_combo_roles()
        self._combo_rol_permisos.currentIndexChanged.connect(self._cargar_matriz_rol)

        # Cargar matriz del primer rol
        if self._combo_rol_permisos.count() > 0:
            self._cargar_matriz_rol()

        return w

    def _asegurar_permisos_bd(self):
        """Crea modulos y permisos que no existan en BD."""
        from core.database import get_db
        from models.permiso import Permiso, Modulo
        self._perm_map = {}  # (modulo_codigo, accion) -> permiso_id
        with get_db() as db:
            for mod_codigo, mod_nombre in self._MODULOS_PERMISOS:
                modulo = db.query(Modulo).filter(Modulo.codigo == mod_codigo).first()
                if not modulo:
                    modulo = Modulo(codigo=mod_codigo, nombre=mod_nombre, activo=True)
                    db.add(modulo)
                    db.flush()
                for accion in self._ACCIONES_PERMISOS:
                    perm = db.query(Permiso).filter(Permiso.modulo_id == modulo.id, Permiso.accion == accion).first()
                    if not perm:
                        perm = Permiso(modulo_id=modulo.id, accion=accion)
                        db.add(perm)
                        db.flush()
                    self._perm_map[(mod_codigo, accion)] = perm.id

    def _cargar_combo_roles(self):
        from core.database import get_db
        from models.rol import Rol
        self._combo_rol_permisos.clear()
        with get_db() as db:
            roles = db.query(Rol).filter(Rol.activo.is_(True)).order_by(Rol.id).all()
            for r in roles:
                self._combo_rol_permisos.addItem(f"{r.nombre}", r.id)

    def _cargar_matriz_rol(self):
        """Carga checkboxes segun permisos del rol seleccionado."""
        rol_id = self._combo_rol_permisos.currentData()
        if not rol_id:
            return

        es_admin = (rol_id == 1)
        self._lbl_rol_info.setText("(Administrador: acceso total, no editable)" if es_admin else "")

        # Leer permisos asignados a este rol
        from core.database import get_db
        from models.permiso import RolPermiso
        with get_db() as db:
            asignados = set(
                rp.permiso_id for rp in db.query(RolPermiso).filter(RolPermiso.rol_id == rol_id).all()
            )

        # Construir tabla
        self._tabla_matriz.setRowCount(len(self._MODULOS_PERMISOS))
        for i, (mod_codigo, mod_nombre) in enumerate(self._MODULOS_PERMISOS):
            # Columna modulo
            item_mod = QTableWidgetItem(f"  {mod_nombre}")
            item_mod.setFlags(item_mod.flags() & ~__import__('PySide6.QtCore', fromlist=['Qt']).Qt.ItemIsSelectable)
            self._tabla_matriz.setItem(i, 0, item_mod)

            # Columnas de acciones
            for k, accion in enumerate(self._ACCIONES_PERMISOS):
                col = k + 1
                perm_id = self._perm_map.get((mod_codigo, accion))
                chk = QCheckBox()
                chk.setStyleSheet("QCheckBox { margin-left: 25px; }")

                if es_admin:
                    chk.setChecked(True)
                    chk.setEnabled(False)
                else:
                    chk.setChecked(perm_id in asignados if perm_id else False)
                    chk.toggled.connect(
                        lambda checked, r=rol_id, p=perm_id: self._toggle_permiso(r, p, checked)
                    )

                self._tabla_matriz.setCellWidget(i, col, chk)

    def _toggle_permiso(self, rol_id: int, permiso_id: int, checked: bool):
        """Guarda/elimina permiso en BD al marcar/desmarcar."""
        if not permiso_id:
            return
        from core.database import get_db
        from models.permiso import RolPermiso
        with get_db() as db:
            existente = db.query(RolPermiso).filter(
                RolPermiso.rol_id == rol_id, RolPermiso.permiso_id == permiso_id
            ).first()
            if checked and not existente:
                db.add(RolPermiso(rol_id=rol_id, permiso_id=permiso_id))
            elif not checked and existente:
                db.delete(existente)

    def _build_matriz_permisos(self) -> QWidget:
        """Tab con matriz jerarquica: modulos colapsables con submodulos."""
        from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QComboBox as QCB

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        # Selector de rol
        row_sel = QHBoxLayout()
        row_sel.addWidget(QLabel("Rol:"))
        self._combo_rol_permisos = QCB()
        self._combo_rol_permisos.setFixedHeight(30)
        self._combo_rol_permisos.setMinimumWidth(200)
        row_sel.addWidget(self._combo_rol_permisos)
        row_sel.addStretch()
        self._lbl_rol_info = QLabel("")
        self._lbl_rol_info.setStyleSheet("font-size: 11px; color: #888;")
        row_sel.addWidget(self._lbl_rol_info)
        lay.addLayout(row_sel)

        info = QLabel("Expande cada modulo para configurar permisos granulares por submodulo. Cambios automaticos.")
        info.setStyleSheet("font-size: 11px; color: #666;")
        lay.addWidget(info)

        # Tree widget
        self._tree_permisos = QTreeWidget()
        self._tree_permisos.setHeaderLabels(["Modulo / Submodulo", "Ver", "Crear", "Editar", "Eliminar"])
        self._tree_permisos.setColumnWidth(0, 260)
        for col in range(1, 5):
            self._tree_permisos.setColumnWidth(col, 70)
        self._tree_permisos.setAlternatingRowColors(True)
        self._tree_permisos.setRootIsDecorated(True)
        lay.addWidget(self._tree_permisos, 1)

        # Arbol de modulos con submodulos
        self._ARBOL_MODULOS = [
            ("compras", "Compras", ["proveedores", "requisiciones", "req_sugerido", "ordenes_compra", "recepcion", "facturas_compra", "precios", "cotizaciones", "aprobaciones", "trazabilidad", "reportes_kpi"]),
            ("inventario", "Inventario", ["productos", "depositos", "movimientos", "lotes", "series", "toma_stock", "valorizacion", "alertas"]),
            ("ventas", "Ventas", ["clientes", "presupuestos", "pedidos", "remitos", "facturas_venta", "notas_cred_deb", "riesgo", "reportes_venta"]),
            ("facturador", "Facturador", ["pos", "facturacion_central", "cajas_turnos", "historial"]),
            ("empleados", "RRHH", ["empleados_crud", "legajo", "asistencia", "fichaje_turnos", "cierres", "nomina", "reclutamiento", "config_rrhh"]),
            ("cuentas", "Cuentas", ["cta_corriente"]),
            ("finanzas", "Finanzas", ["contabilidad", "facturacion", "bancos", "caja"]),
            ("reportes", "Reportes", ["dashboard_bi"]),
            ("herramientas", "Herramientas", ["etiquetas", "limpiador", "cotizacion_tc", "exportar"]),
            ("importador", "Importador", ["importar_productos", "actualizar_precios"]),
            ("administrador", "Administrador", ["usuarios", "roles_permisos", "tablas_maestras"]),
            ("admin", "Configuracion", ["datos_empresa", "visual", "auditoria", "actualizar", "desarrollador"]),
        ]
        self._ACCIONES = ["ver", "crear", "editar", "eliminar"]

        self._asegurar_permisos_arbol()
        self._cargar_combo_roles_arbol()
        self._combo_rol_permisos.currentIndexChanged.connect(self._cargar_arbol_rol)
        if self._combo_rol_permisos.count() > 0:
            self._cargar_arbol_rol()

        return w

    def _asegurar_permisos_arbol(self):
        """Crea modulos, submodulos y permisos en BD si no existen."""
        from core.database import get_db
        from models.permiso import Permiso, Modulo
        self._perm_map = {}
        with get_db() as db:
            for mod_codigo, mod_nombre, submodulos in self._ARBOL_MODULOS:
                modulo = db.query(Modulo).filter(Modulo.codigo == mod_codigo).first()
                if not modulo:
                    modulo = Modulo(codigo=mod_codigo, nombre=mod_nombre, activo=True)
                    db.add(modulo)
                    db.flush()
                for accion in self._ACCIONES:
                    perm = db.query(Permiso).filter(Permiso.modulo_id == modulo.id, Permiso.accion == accion).first()
                    if not perm:
                        perm = Permiso(modulo_id=modulo.id, accion=accion)
                        db.add(perm)
                        db.flush()
                    self._perm_map[(mod_codigo, accion)] = perm.id
                for sub in submodulos:
                    sub_code = f"{mod_codigo}.{sub}"
                    sub_mod = db.query(Modulo).filter(Modulo.codigo == sub_code).first()
                    if not sub_mod:
                        sub_mod = Modulo(codigo=sub_code, nombre=sub, activo=True)
                        db.add(sub_mod)
                        db.flush()
                    for accion in self._ACCIONES:
                        perm = db.query(Permiso).filter(Permiso.modulo_id == sub_mod.id, Permiso.accion == accion).first()
                        if not perm:
                            perm = Permiso(modulo_id=sub_mod.id, accion=accion)
                            db.add(perm)
                            db.flush()
                        self._perm_map[(sub_code, accion)] = perm.id

    def _cargar_combo_roles_arbol(self):
        from core.database import get_db
        from models.rol import Rol
        self._combo_rol_permisos.clear()
        with get_db() as db:
            roles = db.query(Rol).filter(Rol.activo.is_(True)).order_by(Rol.id).all()
            for r in roles:
                self._combo_rol_permisos.addItem(r.nombre, r.id)

    def _cargar_arbol_rol(self):
        """Reconstruye tree con checkboxes segun permisos del rol."""
        from PySide6.QtWidgets import QTreeWidgetItem
        rol_id = self._combo_rol_permisos.currentData()
        if not rol_id:
            return
        es_admin = (rol_id == 1)
        self._lbl_rol_info.setText("(Administrador: acceso total)" if es_admin else "")

        from core.database import get_db
        from models.permiso import RolPermiso
        with get_db() as db:
            asignados = set(rp.permiso_id for rp in db.query(RolPermiso).filter(RolPermiso.rol_id == rol_id).all())

        self._tree_permisos.clear()

        for mod_codigo, mod_nombre, submodulos in self._ARBOL_MODULOS:
            parent = QTreeWidgetItem([mod_nombre])
            parent.setExpanded(False)
            self._tree_permisos.addTopLevelItem(parent)

            # Checkboxes padre
            parent_chks = []
            child_chks_by_accion = {a: [] for a in self._ACCIONES}

            for k, accion in enumerate(self._ACCIONES):
                col = k + 1
                perm_id = self._perm_map.get((mod_codigo, accion))
                chk = QCheckBox()
                if es_admin:
                    chk.setChecked(True)
                    chk.setEnabled(False)
                else:
                    chk.setChecked(perm_id in asignados if perm_id else False)
                self._tree_permisos.setItemWidget(parent, col, chk)
                parent_chks.append((chk, perm_id))

            # Hijos
            for sub in submodulos:
                sub_code = f"{mod_codigo}.{sub}"
                sub_label = sub.replace("_", " ").capitalize()
                child = QTreeWidgetItem([f"  {sub_label}"])
                parent.addChild(child)

                for k, accion in enumerate(self._ACCIONES):
                    col = k + 1
                    perm_id = self._perm_map.get((sub_code, accion))
                    chk = QCheckBox()
                    if es_admin:
                        chk.setChecked(True)
                        chk.setEnabled(False)
                    else:
                        chk.setChecked(perm_id in asignados if perm_id else False)
                        if perm_id:
                            chk.toggled.connect(lambda checked, r=rol_id, p=perm_id: self._toggle_permiso(r, p, checked))
                    self._tree_permisos.setItemWidget(child, col, chk)
                    child_chks_by_accion[accion].append((chk, perm_id))

            # Cascada padre -> hijos
            if not es_admin:
                for k, accion in enumerate(self._ACCIONES):
                    p_chk, p_perm = parent_chks[k]
                    hijos = child_chks_by_accion[accion]
                    p_chk.toggled.connect(self._make_cascade(rol_id, p_perm, hijos))

    def _make_cascade(self, rol_id, parent_perm_id, hijos):
        """Handler cascada: marcar padre marca todos los hijos."""
        def handler(checked):
            self._toggle_permiso(rol_id, parent_perm_id, checked)
            for chk, perm_id in hijos:
                chk.blockSignals(True)
                chk.setChecked(checked)
                chk.blockSignals(False)
                self._toggle_permiso(rol_id, perm_id, checked)
        return handler

    def _toggle_permiso(self, rol_id: int, permiso_id: int, checked: bool):
        """Guarda/elimina permiso en BD."""
        if not permiso_id:
            return
        from core.database import get_db
        from models.permiso import RolPermiso
        with get_db() as db:
            existente = db.query(RolPermiso).filter(
                RolPermiso.rol_id == rol_id, RolPermiso.permiso_id == permiso_id
            ).first()
            if checked and not existente:
                db.add(RolPermiso(rol_id=rol_id, permiso_id=permiso_id))
            elif not checked and existente:
                db.delete(existente)
