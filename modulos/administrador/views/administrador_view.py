from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QPushButton, QLabel, QStackedWidget, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
from ui.theme_manager import theme_manager


SUBMODULOS_ADMINISTRADOR = [
    {"codigo": "adm_usuarios", "label": "Usuarios", "icon": "fa5s.user-cog"},
    {"codigo": "adm_roles", "label": "Roles y Permisos", "icon": "fa5s.user-shield"},
    {"codigo": "adm_productos", "label": "Productos", "icon": "fa5s.box"},
    {"codigo": "adm_categorias", "label": "Categorias", "icon": "fa5s.tags"},
    {"codigo": "adm_depositos", "label": "Depositos", "icon": "fa5s.warehouse"},
    {"codigo": "adm_clientes", "label": "Clientes", "icon": "fa5s.user-tie"},
    {"codigo": "adm_proveedores", "label": "Proveedores", "icon": "fa5s.truck"},
    {"codigo": "adm_sucursales", "label": "Sucursales", "icon": "fa5s.store"},
    {"codigo": "adm_departamentos", "label": "Departamentos", "icon": "fa5s.building"},
    {"codigo": "adm_facturadores", "label": "Facturadores", "icon": "fa5s.cash-register"},
    {"codigo": "adm_cuentas_banco", "label": "Bancos", "icon": "fa5s.university"},
    {"codigo": "adm_tipos_compra", "label": "Tipos de Compra", "icon": "fa5s.shopping-basket"},
    {"codigo": "adm_plan_cuentas", "label": "Plan de Cuentas", "icon": "fa5s.book"},
]


class AdministradorView(QWidget):
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
        lbl = QLabel("Administrador")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl)

        lbl_sub = QLabel("Tablas Maestras")
        lbl_sub.setStyleSheet("font-size: 10px; color: #888;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl_sub)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.stack = QStackedWidget()
        for i, sub in enumerate(SUBMODULOS_ADMINISTRADOR):
            btn = QPushButton(f"  {sub['label']}")
            btn.setIcon(qta.icon(sub["icon"], color="#8a8a8a"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._navigate(idx))
            sidebar_layout.addWidget(btn)
            self._buttons.append(btn)
            self.stack.addWidget(self._create_submodule(sub["codigo"]))

        sidebar_layout.addStretch()
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
        if codigo == "adm_usuarios":
            from modulos.configuracion.views.usuarios_view import UsuariosView
            return UsuariosView()
        if codigo == "adm_roles":
            return self._roles_permisos_view()
        if codigo == "adm_productos":
            from modulos.inventario.views.productos_view import ProductosView
            return ProductosView()
        if codigo == "adm_categorias":
            return self._categorias_view()
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
            return self._sucursales_view()
        if codigo == "adm_departamentos":
            return self._departamentos_view()
        if codigo == "adm_facturadores":
            from modulos.ventas.views.config_facturadores_view import ConfigFacturadoresView
            return ConfigFacturadoresView()
        if codigo == "adm_cuentas_banco":
            from modulos.finanzas.views.bancos_view import BancosView
            return BancosView()
        if codigo == "adm_tipos_compra":
            return self._tipos_compra_view()
        if codigo == "adm_plan_cuentas":
            from modulos.finanzas.views.contabilidad_view import ContabilidadView
            return ContabilidadView()
        return QWidget()

    def _categorias_view(self) -> QWidget:
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel("Categorias de Producto")
        t.setObjectName("title")
        header.addWidget(t)
        header.addStretch()
        btn = QPushButton("  Nueva Categoria")
        btn.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn.setFixedHeight(32)
        btn.setCursor(Qt.PointingHandCursor)
        header.addWidget(btn)
        lay.addLayout(header)

        tabla = QTableWidget()
        tabla.setColumnCount(2)
        tabla.setHorizontalHeaderLabels(["Nombre", "Descripcion"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setAlternatingRowColors(True)
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(tabla)

        def cargar():
            from services.inventario import inventario_service
            cats = inventario_service.listar_categorias()
            tabla.setRowCount(len(cats))
            for i, c in enumerate(cats):
                tabla.setItem(i, 0, QTableWidgetItem(c.nombre))
                tabla.setItem(i, 1, QTableWidgetItem(c.descripcion or ""))

        def nueva():
            nombre, ok = QInputDialog.getText(page, "Nueva Categoria", "Nombre:")
            if ok and nombre.strip():
                from services.inventario import inventario_service
                try:
                    inventario_service.crear_categoria(nombre.strip())
                    cargar()
                except Exception as e:
                    QMessageBox.critical(page, "Error", str(e))

        btn.clicked.connect(nueva)
        cargar()
        return page

    def _sucursales_view(self) -> QWidget:
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog
        from core.database import get_db
        from models.sucursal import Sucursal
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel("Sucursales")
        t.setObjectName("title")
        header.addWidget(t)
        header.addStretch()
        btn = QPushButton("  Nueva Sucursal")
        btn.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn.setFixedHeight(32)
        btn.setCursor(Qt.PointingHandCursor)
        header.addWidget(btn)
        lay.addLayout(header)

        tabla = QTableWidget()
        tabla.setColumnCount(3)
        tabla.setHorizontalHeaderLabels(["Nombre", "Direccion", "Estado"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setAlternatingRowColors(True)
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(tabla)

        def cargar():
            with get_db() as db:
                sucursales = db.query(Sucursal).order_by(Sucursal.nombre).all()
                tabla.setRowCount(len(sucursales))
                for i, s in enumerate(sucursales):
                    tabla.setItem(i, 0, QTableWidgetItem(s.nombre))
                    tabla.setItem(i, 1, QTableWidgetItem(s.direccion or ""))
                    tabla.setItem(i, 2, QTableWidgetItem("Activa" if s.activo else "Inactiva"))

        def nueva():
            nombre, ok = QInputDialog.getText(page, "Nueva Sucursal", "Nombre:")
            if ok and nombre.strip():
                try:
                    with get_db() as db:
                        db.add(Sucursal(nombre=nombre.strip()))
                    cargar()
                except Exception as e:
                    QMessageBox.critical(page, "Error", str(e))

        btn.clicked.connect(nueva)
        cargar()
        return page

    def _departamentos_view(self) -> QWidget:
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog
        from core.database import get_db
        from models.empleado import Departamento
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel("Departamentos")
        t.setObjectName("title")
        header.addWidget(t)
        header.addStretch()
        btn = QPushButton("  Nuevo Departamento")
        btn.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn.setFixedHeight(32)
        btn.setCursor(Qt.PointingHandCursor)
        header.addWidget(btn)
        lay.addLayout(header)

        tabla = QTableWidget()
        tabla.setColumnCount(2)
        tabla.setHorizontalHeaderLabels(["Nombre", "Estado"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setAlternatingRowColors(True)
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(tabla)

        def cargar():
            with get_db() as db:
                deptos = db.query(Departamento).order_by(Departamento.nombre).all()
                tabla.setRowCount(len(deptos))
                for i, d in enumerate(deptos):
                    tabla.setItem(i, 0, QTableWidgetItem(d.nombre))
                    tabla.setItem(i, 1, QTableWidgetItem("Activo" if d.activo else "Inactivo"))

        def nueva():
            nombre, ok = QInputDialog.getText(page, "Nuevo Departamento", "Nombre:")
            if ok and nombre.strip():
                try:
                    with get_db() as db:
                        db.add(Departamento(nombre=nombre.strip()))
                    cargar()
                except Exception as e:
                    QMessageBox.critical(page, "Error", str(e))

        btn.clicked.connect(nueva)
        cargar()
        return page

    def _tipos_compra_view(self) -> QWidget:
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog
        from core.database import get_db
        from models.compras import TipoCompra
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel("Tipos de Compra")
        t.setObjectName("title")
        header.addWidget(t)
        header.addStretch()
        btn = QPushButton("  Nuevo Tipo")
        btn.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn.setFixedHeight(32)
        btn.setCursor(Qt.PointingHandCursor)
        header.addWidget(btn)
        lay.addLayout(header)

        tabla = QTableWidget()
        tabla.setColumnCount(2)
        tabla.setHorizontalHeaderLabels(["Nombre", "Estado"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setAlternatingRowColors(True)
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(tabla)

        def cargar():
            with get_db() as db:
                tipos = db.query(TipoCompra).filter(TipoCompra.activo == True).order_by(TipoCompra.nombre).all()
                tabla.setRowCount(len(tipos))
                for i, tc in enumerate(tipos):
                    tabla.setItem(i, 0, QTableWidgetItem(tc.nombre))
                    tabla.setItem(i, 1, QTableWidgetItem("Activo" if tc.activo else "Inactivo"))

        def nueva():
            nombre, ok = QInputDialog.getText(page, "Nuevo Tipo de Compra", "Nombre:")
            if ok and nombre.strip():
                try:
                    with get_db() as db:
                        db.add(TipoCompra(nombre=nombre.strip()))
                    cargar()
                except Exception as e:
                    QMessageBox.critical(page, "Error", str(e))

        btn.clicked.connect(nueva)
        cargar()
        return page

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == index)
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _roles_permisos_view(self) -> QWidget:
        """Vista de roles con matriz de permisos por modulo."""
        from PySide6.QtWidgets import (
            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
            QInputDialog, QCheckBox, QTabWidget, QDialog, QFormLayout, QLineEdit,
        )
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel("Roles y Permisos")
        t.setObjectName("title")
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

        # Modulos del sistema
        MODULOS_APP = [
            "Compras", "Inventario", "Ventas", "Facturador", "RRHH",
            "Cuentas", "Finanzas", "Reportes", "Herramientas",
            "Importador", "Administrador", "Configuracion",
        ]
        ACCIONES = ["ver", "crear", "editar", "eliminar"]

        # Tabla de permisos (filas=modulos, columnas=roles x acciones)
        self._tabla_permisos = QTableWidget()
        lay.addWidget(self._tabla_permisos, 1)

        def cargar_roles():
            from core.database import get_db
            from models.rol import Rol
            with get_db() as db:
                roles = db.query(Rol).filter(Rol.activo.is_(True)).order_by(Rol.id).all()
                roles_data = [(r.id, r.nombre) for r in roles]

            # Columnas: Modulo + (ver/crear/editar/eliminar) por cada rol
            n_cols = 1 + len(roles_data) * len(ACCIONES)
            self._tabla_permisos.setColumnCount(n_cols)
            headers = ["Modulo"]
            for _, rol_nombre in roles_data:
                for accion in ACCIONES:
                    headers.append(f"{rol_nombre[:8]}\n{accion}")
            self._tabla_permisos.setHorizontalHeaderLabels(headers)
            self._tabla_permisos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self._tabla_permisos.setRowCount(len(MODULOS_APP))
            self._tabla_permisos.verticalHeader().setVisible(False)

            for i, modulo in enumerate(MODULOS_APP):
                self._tabla_permisos.setItem(i, 0, QTableWidgetItem(modulo))
                for j, (rol_id, _) in enumerate(roles_data):
                    for k, accion in enumerate(ACCIONES):
                        col = 1 + j * len(ACCIONES) + k
                        chk = QCheckBox()
                        # Admin tiene todo
                        if rol_id == 1:
                            chk.setChecked(True)
                            chk.setEnabled(False)
                        else:
                            chk.setChecked(accion == "ver")  # Default: solo ver
                        self._tabla_permisos.setCellWidget(i, col, chk)

        def nuevo_rol():
            dlg = QDialog(page)
            dlg.setWindowTitle("Nuevo Rol")
            dlg.setMinimumWidth(300)
            form_lay = QVBoxLayout(dlg)
            form = QFormLayout()
            input_nombre = QLineEdit()
            input_nombre.setMaxLength(50)
            form.addRow("Nombre:", input_nombre)
            input_desc = QLineEdit()
            input_desc.setMaxLength(200)
            form.addRow("Descripcion:", input_desc)
            form_lay.addLayout(form)
            btn_ok = QPushButton("Crear")
            btn_ok.clicked.connect(dlg.accept)
            form_lay.addWidget(btn_ok)
            if dlg.exec() == QDialog.Accepted and input_nombre.text().strip():
                from core.database import get_db
                from models.rol import Rol
                with get_db() as db:
                    db.add(Rol(nombre=input_nombre.text().strip(), descripcion=input_desc.text().strip(), activo=True))
                cargar_roles()

        btn_nuevo.clicked.connect(nuevo_rol)
        cargar_roles()
        return page
