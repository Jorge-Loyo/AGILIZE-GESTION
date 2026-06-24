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
        btn_logout.setIcon(qta.icon("fa5s.sign-out-alt", color="#ffffff"))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("QPushButton { background-color: #ef4444; padding: 6px 10px; } QPushButton:hover { background-color: #dc2626; }")
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
                    db.execute(text(f"INSERT INTO {tabla} ({campos[0]}) VALUES (:v)"), {"v": nombre.strip()})
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
        """Tab con matriz visual de permisos que lee/guarda en BD."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)

        info = QLabel("Los checkboxes controlan el acceso real de cada rol. Los cambios se guardan al marcar/desmarcar.")
        info.setStyleSheet("font-size: 11px; color: #888;")
        lay.addWidget(info)

        MODULOS_APP = [
            ("compras", "Compras"), ("inventario", "Inventario"), ("ventas", "Ventas"),
            ("facturador", "Facturador"), ("empleados", "RRHH"), ("cuentas", "Cuentas"),
            ("finanzas", "Finanzas"), ("reportes", "Reportes"), ("herramientas", "Herramientas"),
            ("importador", "Importador"), ("administrador", "Administrador"), ("admin", "Configuracion"),
        ]
        ACCIONES = ["ver", "crear", "editar", "eliminar"]

        tabla_p = QTableWidget()
        lay.addWidget(tabla_p, 1)

        from core.database import get_db
        from models.rol import Rol
        from models.permiso import Permiso, RolPermiso, Modulo

        with get_db() as db:
            roles = db.query(Rol).filter(Rol.activo.is_(True)).order_by(Rol.id).all()
            roles_data = [(r.id, r.nombre) for r in roles]

            # Asegurar que existen los modulos y permisos en BD
            for mod_codigo, mod_nombre in MODULOS_APP:
                modulo = db.query(Modulo).filter(Modulo.codigo == mod_codigo).first()
                if not modulo:
                    modulo = Modulo(codigo=mod_codigo, nombre=mod_nombre, activo=True)
                    db.add(modulo)
                    db.flush()
                for accion in ACCIONES:
                    perm = db.query(Permiso).filter(Permiso.modulo_id == modulo.id, Permiso.accion == accion).first()
                    if not perm:
                        db.add(Permiso(modulo_id=modulo.id, accion=accion))

            # Leer permisos asignados
            permisos_asignados = set()
            for rp in db.query(RolPermiso).all():
                permisos_asignados.add((rp.rol_id, rp.permiso_id))

            # Mapa permiso_id por (modulo_codigo, accion)
            perm_map = {}
            for mod_codigo, _ in MODULOS_APP:
                modulo = db.query(Modulo).filter(Modulo.codigo == mod_codigo).first()
                if modulo:
                    for perm in db.query(Permiso).filter(Permiso.modulo_id == modulo.id).all():
                        perm_map[(mod_codigo, perm.accion)] = perm.id

        # Construir tabla
        n_cols = 1 + len(roles_data) * len(ACCIONES)
        tabla_p.setColumnCount(n_cols)
        headers = ["Modulo"]
        for _, nombre in roles_data:
            for acc in ACCIONES:
                headers.append(f"{nombre[:6]}\n{acc}")
        tabla_p.setHorizontalHeaderLabels(headers)
        tabla_p.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tabla_p.setRowCount(len(MODULOS_APP))
        tabla_p.verticalHeader().setVisible(False)

        for i, (mod_codigo, mod_nombre) in enumerate(MODULOS_APP):
            tabla_p.setItem(i, 0, QTableWidgetItem(mod_nombre))
            for j, (rol_id, _) in enumerate(roles_data):
                for k, acc in enumerate(ACCIONES):
                    col = 1 + j * len(ACCIONES) + k
                    chk = QCheckBox()
                    perm_id = perm_map.get((mod_codigo, acc))
                    # Admin siempre todo
                    if rol_id == 1:
                        chk.setChecked(True)
                        chk.setEnabled(False)
                    else:
                        chk.setChecked((rol_id, perm_id) in permisos_asignados if perm_id else False)
                        # Conectar para guardar al cambiar
                        chk.toggled.connect(lambda checked, r=rol_id, p=perm_id: self._toggle_permiso(r, p, checked))
                    tabla_p.setCellWidget(i, col, chk)

        return w

    def _toggle_permiso(self, rol_id: int, permiso_id: int, checked: bool):
        """Guarda/elimina permiso en BD al marcar/desmarcar checkbox."""
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
