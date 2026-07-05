"""Vista de Roles y Permisos - arbol desplegable por modulo/submodulo."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QMessageBox, QGroupBox, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QDialog, QFormLayout,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from core.database import get_db
from models.rol import Rol
from models.permiso import Modulo, Permiso, RolPermiso


# Estructura real de la app: modulo -> seccion -> sub-pestañas
# Cada nivel puede tener "hijos" para anidar permisos
ESTRUCTURA_APP = [
    {
        "codigo": "rrhh",
        "nombre": "RRHH",
        "icon": "fa5s.users",
        "hijos": [
            {"codigo": "rrhh.dashboard", "nombre": "Dashboard"},
            {"codigo": "rrhh.empleados", "nombre": "Empleados"},
            {"codigo": "rrhh.legajo", "nombre": "Legajo"},
            {"codigo": "rrhh.asistencia", "nombre": "Asistencia", "hijos": [
                {"codigo": "rrhh.asistencia.registro", "nombre": "Registro"},
                {"codigo": "rrhh.asistencia.permisos", "nombre": "Permisos / Licencias"},
                {"codigo": "rrhh.asistencia.ausencias", "nombre": "Ausencias"},
                {"codigo": "rrhh.asistencia.vacaciones", "nombre": "Vacaciones"},
                {"codigo": "rrhh.asistencia.extras", "nombre": "Aprobacion Extras"},
            ]},
            {"codigo": "rrhh.fichaje", "nombre": "Fichaje / Turnos", "hijos": [
                {"codigo": "rrhh.fichaje.fichar", "nombre": "Fichar"},
                {"codigo": "rrhh.fichaje.importar", "nombre": "Importar Fichadas"},
                {"codigo": "rrhh.fichaje.turnos", "nombre": "Turnos Laborales"},
                {"codigo": "rrhh.fichaje.hoy", "nombre": "Fichajes del Dia"},
            ]},
            {"codigo": "rrhh.cierres", "nombre": "Cierres"},
            {"codigo": "rrhh.nomina", "nombre": "Nomina", "hijos": [
                {"codigo": "rrhh.nomina.liquidaciones", "nombre": "Liquidaciones"},
                {"codigo": "rrhh.nomina.resumen", "nombre": "Resumen Mensual"},
                {"codigo": "rrhh.nomina.adelantos", "nombre": "Adelantos"},
                {"codigo": "rrhh.nomina.sac", "nombre": "SAC (Aguinaldo)"},
                {"codigo": "rrhh.nomina.novedades", "nombre": "Novedades Mensuales"},
            ]},
            {"codigo": "rrhh.reclutamiento", "nombre": "Reclutamiento", "hijos": [
                {"codigo": "rrhh.reclutamiento.vacantes", "nombre": "Vacantes"},
                {"codigo": "rrhh.reclutamiento.candidatos", "nombre": "Candidatos"},
            ]},
            {"codigo": "rrhh.config", "nombre": "Configuracion", "hijos": [
                {"codigo": "rrhh.config.periodo", "nombre": "Periodo de Pago"},
                {"codigo": "rrhh.config.multiplicadores", "nombre": "Valor Hora Extra"},
                {"codigo": "rrhh.config.sac", "nombre": "SAC"},
                {"codigo": "rrhh.config.conceptos", "nombre": "Conceptos Nomina"},
                {"codigo": "rrhh.config.permisos", "nombre": "Tipos de Permiso"},
                {"codigo": "rrhh.config.feriados", "nombre": "Feriados"},
            ]},
        ],
    },
    {
        "codigo": "finanzas",
        "nombre": "Finanzas",
        "icon": "fa5s.coins",
        "hijos": [
            {"codigo": "finanzas.facturacion", "nombre": "Facturacion"},
            {"codigo": "finanzas.contabilidad", "nombre": "Contabilidad", "hijos": [
                {"codigo": "finanzas.contabilidad.plan", "nombre": "Plan de Cuentas"},
                {"codigo": "finanzas.contabilidad.asientos", "nombre": "Asientos"},
            ]},
            {"codigo": "finanzas.caja", "nombre": "Caja"},
            {"codigo": "finanzas.bancos", "nombre": "Bancos"},
            {"codigo": "finanzas.historial_dolar", "nombre": "Historial Dolar"},
        ],
    },
    {
        "codigo": "ventas",
        "nombre": "Ventas",
        "icon": "fa5s.shopping-cart",
        "hijos": [
            {"codigo": "ventas.clientes", "nombre": "Clientes"},
            {"codigo": "ventas.presupuestos", "nombre": "Presupuestos"},
            {"codigo": "ventas.pedidos", "nombre": "Pedidos"},
            {"codigo": "ventas.facturar", "nombre": "Facturar"},
            {"codigo": "ventas.facturadores", "nombre": "Facturadores"},
            {"codigo": "ventas.historial", "nombre": "Historial"},
        ],
    },
    {
        "codigo": "compras",
        "nombre": "Compras",
        "icon": "fa5s.truck-loading",
        "hijos": [],
    },
    {
        "codigo": "inventario",
        "nombre": "Inventario",
        "icon": "fa5s.warehouse",
        "hijos": [],
    },
    {
        "codigo": "facturador",
        "nombre": "Facturador",
        "icon": "fa5s.barcode",
        "hijos": [],
    },
    {
        "codigo": "cuentas",
        "nombre": "Cuentas",
        "icon": "fa5s.file-invoice-dollar",
        "hijos": [],
    },
    {
        "codigo": "reportes",
        "nombre": "Reportes",
        "icon": "fa5s.tachometer-alt",
        "hijos": [],
    },
    {
        "codigo": "herramientas",
        "nombre": "Herramientas",
        "icon": "fa5s.tools",
        "hijos": [
            {"codigo": "herramientas.limpiador", "nombre": "Limpiador Productos"},
            {"codigo": "herramientas.categorias", "nombre": "Limpiador Categorias"},
            {"codigo": "herramientas.cotizaciones", "nombre": "Cotizaciones"},
            {"codigo": "herramientas.etiquetas_estante", "nombre": "Etiquetas Estante"},
            {"codigo": "herramientas.etiquetas_producto", "nombre": "Etiquetas Producto"},
            {"codigo": "herramientas.config", "nombre": "Configuracion"},
        ],
    },
    {
        "codigo": "importador",
        "nombre": "Importador",
        "icon": "fa5s.file-import",
        "hijos": [],
    },
    {
        "codigo": "administrador",
        "nombre": "Administrador",
        "icon": "fa5s.shield-alt",
        "hijos": [
            {"codigo": "administrador.usuarios", "nombre": "Usuarios"},
            {"codigo": "administrador.roles", "nombre": "Roles y Permisos"},
            {"codigo": "administrador.tablas", "nombre": "Tablas Maestras"},
        ],
    },
    {
        "codigo": "conexiones",
        "nombre": "Conexiones",
        "icon": "fa5s.plug",
        "hijos": [],
    },
    {
        "codigo": "configuracion",
        "nombre": "Configuracion",
        "icon": "fa5s.cog",
        "hijos": [
            {"codigo": "configuracion.empresa", "nombre": "Datos Empresa"},
            {"codigo": "configuracion.visual", "nombre": "Visual"},
            {"codigo": "configuracion.auditoria", "nombre": "Auditoria"},
            {"codigo": "configuracion.desarrollador", "nombre": "Desarrollador"},
        ],
    },
]


class RolesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._perm_map: dict[str, int] = {}  # codigo -> permiso_id
        self._checks: dict[str, QCheckBox] = {}  # codigo -> checkbox
        self._build_ui()
        self._asegurar_estructura_bd()
        self._cargar_roles()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Roles y Permisos")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        info = QLabel("Define que modulos y pestañas puede ver cada rol. Los cambios se guardan al presionar 'Guardar'.")
        info.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(info)

        # Fila: selector rol + crear rol
        row = QHBoxLayout()
        row.addWidget(QLabel("Rol:"))
        self.combo_rol = QComboBox()
        self.combo_rol.setMinimumHeight(32)
        self.combo_rol.setMinimumWidth(220)
        self.combo_rol.currentIndexChanged.connect(self._cargar_permisos_rol)
        row.addWidget(self.combo_rol)

        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("font-size: 11px; color: #888; margin-left: 12px;")
        row.addWidget(self.lbl_info)

        row.addStretch()

        btn_nuevo_rol = QPushButton("  Nuevo Rol")
        btn_nuevo_rol.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo_rol.setFixedHeight(32)
        btn_nuevo_rol.clicked.connect(self._crear_rol)
        row.addWidget(btn_nuevo_rol)

        btn_editar_rol = QPushButton("  Editar")
        btn_editar_rol.setIcon(qta.icon("fa5s.pen", color="#0f0f0f"))
        btn_editar_rol.setFixedHeight(32)
        btn_editar_rol.clicked.connect(self._editar_rol)
        row.addWidget(btn_editar_rol)

        btn_eliminar_rol = QPushButton("  Eliminar")
        btn_eliminar_rol.setIcon(qta.icon("fa5s.trash", color="#c0392b"))
        btn_eliminar_rol.setFixedHeight(32)
        btn_eliminar_rol.clicked.connect(self._eliminar_rol)
        row.addWidget(btn_eliminar_rol)
        layout.addLayout(row)

        # Arbol de permisos
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Modulo / Pestaña", "Acceso"])
        self.tree.setColumnWidth(0, 350)
        self.tree.setColumnWidth(1, 80)
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setAnimated(True)
        layout.addWidget(self.tree, 1)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_guardar = QPushButton("  Guardar Permisos")
        btn_guardar.setIcon(qta.icon("fa5s.save", color="#121212"))
        btn_guardar.setMinimumHeight(38)
        btn_guardar.setMinimumWidth(180)
        btn_guardar.setStyleSheet(
            "QPushButton { background-color: #D4AF37; color: #121212; font-weight: bold; } "
            "QPushButton:hover { background-color: #c9a030; }"
        )
        btn_guardar.clicked.connect(self._guardar_permisos)
        btn_row.addWidget(btn_guardar)
        layout.addLayout(btn_row)

    def _asegurar_estructura_bd(self):
        """Crea modulos y permisos 'ver' en BD si no existen (3 niveles)."""
        with get_db() as db:
            for mod in ESTRUCTURA_APP:
                self._asegurar_modulo_permiso(db, mod["codigo"], mod["nombre"])
                for hijo in mod["hijos"]:
                    self._asegurar_modulo_permiso(db, hijo["codigo"], hijo["nombre"])
                    for nieto in hijo.get("hijos", []):
                        self._asegurar_modulo_permiso(db, nieto["codigo"], nieto["nombre"])

    def _asegurar_modulo_permiso(self, db, codigo: str, nombre: str):
        modulo = db.query(Modulo).filter(Modulo.codigo == codigo).first()
        if not modulo:
            modulo = Modulo(codigo=codigo, nombre=nombre, activo=True)
            db.add(modulo)
            db.flush()
        perm = db.query(Permiso).filter(Permiso.modulo_id == modulo.id, Permiso.accion == "ver").first()
        if not perm:
            perm = Permiso(modulo_id=modulo.id, accion="ver")
            db.add(perm)
            db.flush()
        self._perm_map[codigo] = perm.id

    def _cargar_roles(self):
        self.combo_rol.blockSignals(True)
        self.combo_rol.clear()
        with get_db() as db:
            roles = db.query(Rol).filter(Rol.activo == True).order_by(Rol.id).all()
            for r in roles:
                self.combo_rol.addItem(r.nombre, r.id)
        self.combo_rol.blockSignals(False)
        if self.combo_rol.count() > 0:
            self._cargar_permisos_rol()

    def _cargar_permisos_rol(self):
        """Reconstruye el arbol con checkboxes segun permisos del rol (3 niveles)."""
        self.tree.clear()
        self._checks.clear()

        rol_id = self.combo_rol.currentData()
        if not rol_id:
            return

        es_admin = (rol_id == 1)
        self.lbl_info.setText("(Administrador: acceso total, no editable)" if es_admin else "")

        with get_db() as db:
            asignados = set(
                rp.permiso_id for rp in db.query(RolPermiso).filter(RolPermiso.rol_id == rol_id).all()
            )

        for mod in ESTRUCTURA_APP:
            parent = QTreeWidgetItem([mod["nombre"]])
            parent.setExpanded(False)
            self.tree.addTopLevelItem(parent)

            chk_padre = self._crear_check(mod["codigo"], asignados, es_admin)
            self.tree.setItemWidget(parent, 1, chk_padre)

            all_descendants = []  # todos los checks descendientes del modulo

            for hijo in mod["hijos"]:
                child = QTreeWidgetItem([hijo["nombre"]])
                parent.addChild(child)

                chk_hijo = self._crear_check(hijo["codigo"], asignados, es_admin)
                self.tree.setItemWidget(child, 1, chk_hijo)
                all_descendants.append(chk_hijo)

                # Nivel 3: sub-pestañas
                nietos = hijo.get("hijos", [])
                if nietos:
                    nieto_checks = []
                    for nieto in nietos:
                        grandchild = QTreeWidgetItem([nieto["nombre"]])
                        child.addChild(grandchild)

                        chk_nieto = self._crear_check(nieto["codigo"], asignados, es_admin)
                        self.tree.setItemWidget(grandchild, 1, chk_nieto)
                        nieto_checks.append(chk_nieto)
                        all_descendants.append(chk_nieto)

                    if not es_admin:
                        chk_hijo.toggled.connect(self._make_cascade(nieto_checks))

            if not es_admin:
                chk_padre.toggled.connect(self._make_cascade(all_descendants))

    def _crear_check(self, codigo: str, asignados: set, es_admin: bool) -> QCheckBox:
        chk = QCheckBox()
        perm_id = self._perm_map.get(codigo)
        if es_admin:
            chk.setChecked(True)
            chk.setEnabled(False)
        else:
            chk.setChecked(perm_id in asignados if perm_id else False)
        self._checks[codigo] = chk
        return chk

    def _make_cascade(self, child_checks: list[QCheckBox]):
        def handler(checked):
            for chk in child_checks:
                chk.blockSignals(True)
                chk.setChecked(checked)
                chk.blockSignals(False)
        return handler

    def _guardar_permisos(self):
        rol_id = self.combo_rol.currentData()
        if not rol_id:
            QMessageBox.warning(self, "Error", "Selecciona un rol.")
            return
        if rol_id == 1:
            QMessageBox.information(self, "Info", "El rol Administrador tiene acceso total y no se puede modificar.")
            return

        with get_db() as db:
            # Borrar permisos 'ver' actuales del rol
            perm_ids = list(self._perm_map.values())
            db.query(RolPermiso).filter(
                RolPermiso.rol_id == rol_id,
                RolPermiso.permiso_id.in_(perm_ids)
            ).delete(synchronize_session=False)

            # Insertar los marcados
            for codigo, chk in self._checks.items():
                if chk.isChecked():
                    perm_id = self._perm_map.get(codigo)
                    if perm_id:
                        db.add(RolPermiso(rol_id=rol_id, permiso_id=perm_id))

        QMessageBox.information(self, "OK", "Permisos guardados correctamente.")

    def _crear_rol(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Nuevo Rol")
        dlg.setMinimumWidth(350)
        lay = QVBoxLayout(dlg)
        form = QFormLayout()
        inp_nombre = QLineEdit()
        inp_nombre.setMaxLength(50)
        inp_nombre.setPlaceholderText("Ej: Supervisor")
        form.addRow("Nombre:", inp_nombre)
        inp_desc = QLineEdit()
        inp_desc.setMaxLength(200)
        inp_desc.setPlaceholderText("Descripcion del rol")
        form.addRow("Descripcion:", inp_desc)
        lay.addLayout(form)
        btn_ok = QPushButton("Crear")
        btn_ok.setMinimumHeight(34)
        btn_ok.clicked.connect(dlg.accept)
        lay.addWidget(btn_ok)

        if dlg.exec() == QDialog.Accepted and inp_nombre.text().strip():
            try:
                with get_db() as db:
                    db.add(Rol(nombre=inp_nombre.text().strip(), descripcion=inp_desc.text().strip(), activo=True))
                self._cargar_roles()
                # Seleccionar el nuevo rol
                self.combo_rol.setCurrentIndex(self.combo_rol.count() - 1)
                QMessageBox.information(self, "OK", f"Rol '{inp_nombre.text().strip()}' creado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _editar_rol(self):
        rol_id = self.combo_rol.currentData()
        if not rol_id:
            return
        if rol_id == 1:
            QMessageBox.information(self, "Info", "El rol Administrador no se puede editar.")
            return

        with get_db() as db:
            rol = db.query(Rol).get(rol_id)
            if not rol:
                return
            nombre_actual = rol.nombre
            desc_actual = rol.descripcion or ""

        dlg = QDialog(self)
        dlg.setWindowTitle("Editar Rol")
        dlg.setMinimumWidth(350)
        lay = QVBoxLayout(dlg)
        form = QFormLayout()
        inp_nombre = QLineEdit(nombre_actual)
        inp_nombre.setMaxLength(50)
        form.addRow("Nombre:", inp_nombre)
        inp_desc = QLineEdit(desc_actual)
        inp_desc.setMaxLength(200)
        form.addRow("Descripcion:", inp_desc)
        lay.addLayout(form)
        btn_ok = QPushButton("Guardar")
        btn_ok.setMinimumHeight(34)
        btn_ok.clicked.connect(dlg.accept)
        lay.addWidget(btn_ok)

        if dlg.exec() == QDialog.Accepted and inp_nombre.text().strip():
            with get_db() as db:
                rol = db.query(Rol).get(rol_id)
                rol.nombre = inp_nombre.text().strip()
                rol.descripcion = inp_desc.text().strip()
            idx = self.combo_rol.currentIndex()
            self._cargar_roles()
            self.combo_rol.setCurrentIndex(idx)

    def _eliminar_rol(self):
        rol_id = self.combo_rol.currentData()
        if not rol_id:
            return
        if rol_id == 1:
            QMessageBox.information(self, "Info", "El rol Administrador no se puede eliminar.")
            return

        nombre = self.combo_rol.currentText()
        resp = QMessageBox.question(
            self, "Confirmar",
            f"¿Eliminar el rol '{nombre}'?\nSe eliminaran todos sus permisos asignados.",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp != QMessageBox.Yes:
            return

        with get_db() as db:
            # Verificar si hay usuarios con este rol
            from models.usuario import Usuario
            en_uso = db.query(Usuario).filter(Usuario.rol_id == rol_id).count()
            if en_uso:
                QMessageBox.warning(self, "Error", f"No se puede eliminar: {en_uso} usuario(s) tienen este rol asignado.")
                return
            db.query(RolPermiso).filter(RolPermiso.rol_id == rol_id).delete()
            db.query(Rol).filter(Rol.id == rol_id).delete()

        self._cargar_roles()
