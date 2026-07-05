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
            {"codigo": "adm_tipos_compra", "label": "Tipos de Compra", "icon": "fa5s.shopping-basket"},
        ],
    },
    {
        "grupo": "RRHH",
        "icon": "fa5s.users",
        "items": [
            {"codigo": "adm_departamentos", "label": "Departamentos", "icon": "fa5s.sitemap"},
            {"codigo": "adm_cargos", "label": "Cargos", "icon": "fa5s.id-badge"},
            {"codigo": "adm_tipos_evento", "label": "Tipos de Evento", "icon": "fa5s.clipboard-list"},
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
            from modulos.configuracion.views.roles_view import RolesView
            return RolesView()
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
        if codigo == "adm_tipos_evento":
            return self._simple_crud("Tipos de Evento (Legajo)", "tipos_evento_legajo", ["nombre"])
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
        """Genera vista CRUD generica con editar y eliminar (protegido si en uso)."""
        from core.database import get_db
        from sqlalchemy import text

        # Mapa de dependencias: tabla -> (tabla_dependiente, campo_fk)
        DEPENDENCIAS = {
            "departamentos": ("empleados", "departamento_id"),
            "cargos": ("empleados", "cargo_id"),
            "tipos_evento_legajo": ("legajo_eventos", "tipo"),
        }

        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel(titulo)
        t.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        header.addWidget(t)
        header.addStretch()
        btn_nuevo = QPushButton("  Nuevo")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(32)
        header.addWidget(btn_nuevo)
        lay.addLayout(header)

        tw = QTableWidget()
        tw.setColumnCount(len(campos) + 1)  # +1 para ID oculto
        tw.setHorizontalHeaderLabels(["ID"] + [c.capitalize() for c in campos])
        tw.setColumnHidden(0, True)
        tw.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tw.setAlternatingRowColors(True)
        tw.verticalHeader().setVisible(False)
        tw.setEditTriggers(QTableWidget.NoEditTriggers)
        tw.setSelectionBehavior(QTableWidget.SelectRows)
        tw.setSelectionMode(QTableWidget.SingleSelection)
        lay.addWidget(tw)

        # Botones de accion
        btns = QHBoxLayout()
        btns.setSpacing(8)
        btn_editar = QPushButton("  Editar")
        btn_editar.setIcon(qta.icon("fa5s.edit", color="#ffffff"))
        btn_editar.setFixedHeight(32)
        btn_editar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btns.addWidget(btn_editar)
        btn_eliminar = QPushButton("  Eliminar")
        btn_eliminar.setIcon(qta.icon("fa5s.trash", color="#ffffff"))
        btn_eliminar.setFixedHeight(32)
        btn_eliminar.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btns.addWidget(btn_eliminar)
        btns.addStretch()
        lay.addLayout(btns)

        def cargar():
            with get_db() as db:
                rows = db.execute(text(f"SELECT id, {','.join(campos)} FROM {tabla} WHERE activo=true ORDER BY {campos[0]}")).fetchall()
                tw.setRowCount(len(rows))
                for i, row in enumerate(rows):
                    tw.setItem(i, 0, QTableWidgetItem(str(row[0])))
                    for j, val in enumerate(row[1:]):
                        tw.setItem(i, j + 1, QTableWidgetItem(str(val or "")))

        def nuevo():
            if len(campos) == 1:
                nombre, ok = QInputDialog.getText(page, f"Nuevo {titulo}", f"{campos[0].capitalize()}:")
                if ok and nombre.strip():
                    with get_db() as db:
                        db.execute(text(f"INSERT INTO {tabla} ({campos[0]}, activo) VALUES (:v, true)"), {"v": nombre.strip()})
                    cargar()
            else:
                dlg = QDialog(page)
                dlg.setWindowTitle(f"Nuevo {titulo}")
                dlg.setMinimumWidth(400)
                d_lay = QVBoxLayout(dlg)
                form = QFormLayout()
                inputs = []
                for c in campos:
                    inp = QLineEdit()
                    inp.setMaxLength(200)
                    form.addRow(f"{c.capitalize()}:", inp)
                    inputs.append(inp)
                d_lay.addLayout(form)
                btn_ok = QPushButton("Crear")
                btn_ok.clicked.connect(dlg.accept)
                d_lay.addWidget(btn_ok)
                if dlg.exec() == QDialog.Accepted and inputs[0].text().strip():
                    valores = {c: inputs[i].text().strip() for i, c in enumerate(campos)}
                    cols = ", ".join(campos + ["activo"])
                    params = ", ".join([f":{c}" for c in campos] + ["true"])
                    with get_db() as db:
                        db.execute(text(f"INSERT INTO {tabla} ({cols}) VALUES ({params})"), valores)
                    cargar()

        def editar():
            row = tw.currentRow()
            if row < 0:
                QMessageBox.information(page, "Seleccion", "Selecciona un registro.")
                return
            reg_id = tw.item(row, 0).text()
            if len(campos) == 1:
                valor_actual = tw.item(row, 1).text()
                nuevo_val, ok = QInputDialog.getText(page, f"Editar {titulo}", f"{campos[0].capitalize()}:", text=valor_actual)
                if ok and nuevo_val.strip():
                    with get_db() as db:
                        db.execute(text(f"UPDATE {tabla} SET {campos[0]}=:v WHERE id=:id"), {"v": nuevo_val.strip(), "id": reg_id})
                    cargar()
            else:
                dlg = QDialog(page)
                dlg.setWindowTitle(f"Editar {titulo}")
                dlg.setMinimumWidth(400)
                d_lay = QVBoxLayout(dlg)
                form = QFormLayout()
                inputs = []
                for j, c in enumerate(campos):
                    inp = QLineEdit(tw.item(row, j + 1).text())
                    inp.setMaxLength(200)
                    form.addRow(f"{c.capitalize()}:", inp)
                    inputs.append(inp)
                d_lay.addLayout(form)
                btn_ok = QPushButton("Guardar")
                btn_ok.clicked.connect(dlg.accept)
                d_lay.addWidget(btn_ok)
                if dlg.exec() == QDialog.Accepted and inputs[0].text().strip():
                    sets = ", ".join([f"{c}=:{c}" for c in campos])
                    valores = {c: inputs[i].text().strip() for i, c in enumerate(campos)}
                    valores["id"] = reg_id
                    with get_db() as db:
                        db.execute(text(f"UPDATE {tabla} SET {sets} WHERE id=:id"), valores)
                    cargar()

        def eliminar():
            row = tw.currentRow()
            if row < 0:
                QMessageBox.information(page, "Seleccion", "Selecciona un registro.")
                return
            reg_id = tw.item(row, 0).text()
            nombre_reg = tw.item(row, 1).text()

            # Verificar dependencias
            dep = DEPENDENCIAS.get(tabla)
            if dep:
                tabla_dep, campo_dep = dep
                with get_db() as db:
                    # Para tipos_evento_legajo el campo es texto, no FK
                    if tabla == "tipos_evento_legajo":
                        count = db.execute(text(f"SELECT COUNT(*) FROM {tabla_dep} WHERE {campo_dep}=:v"), {"v": nombre_reg}).scalar()
                    else:
                        count = db.execute(text(f"SELECT COUNT(*) FROM {tabla_dep} WHERE {campo_dep}=:id"), {"id": reg_id}).scalar()
                if count > 0:
                    QMessageBox.warning(page, "No se puede eliminar",
                        f"'{nombre_reg}' esta en uso ({count} registro{'s' if count > 1 else ''}).\n"
                        f"No se puede eliminar mientras tenga registros asociados.")
                    return

            resp = QMessageBox.question(page, "Confirmar", f"Eliminar '{nombre_reg}'?",
                QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.Yes:
                with get_db() as db:
                    db.execute(text(f"UPDATE {tabla} SET activo=false WHERE id=:id"), {"id": reg_id})
                cargar()

        btn_nuevo.clicked.connect(nuevo)
        btn_editar.clicked.connect(editar)
        btn_eliminar.clicked.connect(eliminar)
        tw.doubleClicked.connect(lambda: editar())
        cargar()
        return page

