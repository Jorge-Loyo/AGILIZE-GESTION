from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QGroupBox, QFrame,
)
from PySide6.QtCore import Qt
from core.database import get_db
from models.rol import Rol
from models.permiso import Modulo, Permiso, RolPermiso


ACCIONES = ["ver", "crear", "editar", "eliminar", "exportar"]


class RolesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._checks: dict[tuple[int, str], QCheckBox] = {}
        self._build_ui()
        self._cargar_roles()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Administracion de Roles")
        title.setObjectName("title")
        layout.addWidget(title)

        # Crear rol
        grp_nuevo = QGroupBox("Crear Rol")
        grp_nuevo.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        nuevo_layout = QHBoxLayout(grp_nuevo)
        nuevo_layout.setSpacing(8)
        nuevo_layout.addWidget(QLabel("Nombre:"))
        self.input_nombre = QLineEdit()
        self.input_nombre.setMinimumHeight(32)
        self.input_nombre.setPlaceholderText("Ej: Supervisor")
        nuevo_layout.addWidget(self.input_nombre)
        nuevo_layout.addWidget(QLabel("Descripcion:"))
        self.input_desc = QLineEdit()
        self.input_desc.setMinimumHeight(32)
        nuevo_layout.addWidget(self.input_desc)
        btn_crear = QPushButton("Crear Rol")
        btn_crear.setMinimumHeight(32)
        btn_crear.clicked.connect(self._crear_rol)
        nuevo_layout.addWidget(btn_crear)
        layout.addWidget(grp_nuevo)

        # Selector de rol
        sel_layout = QHBoxLayout()
        sel_layout.addWidget(QLabel("Rol:"))
        self.combo_rol = QComboBox()
        self.combo_rol.setMinimumHeight(32)
        self.combo_rol.setMinimumWidth(200)
        self.combo_rol.currentIndexChanged.connect(self._cargar_permisos)
        sel_layout.addWidget(self.combo_rol)
        sel_layout.addStretch()
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        sel_layout.addWidget(self.lbl_info)
        layout.addLayout(sel_layout)

        # Matriz de permisos
        self.grp_permisos = QGroupBox("Permisos del Rol")
        self.grp_permisos.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        self.permisos_layout = QGridLayout(self.grp_permisos)
        self.permisos_layout.setSpacing(6)
        layout.addWidget(self.grp_permisos)

        # Boton guardar
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_guardar = QPushButton("  Guardar Permisos")
        btn_guardar.setMinimumHeight(36)
        btn_guardar.setFixedWidth(180)
        btn_guardar.clicked.connect(self._guardar_permisos)
        btn_row.addWidget(btn_guardar)
        layout.addLayout(btn_row)

        layout.addStretch()

    def _cargar_roles(self):
        self.combo_rol.clear()
        with get_db() as db:
            roles = db.query(Rol).filter(Rol.activo == True).order_by(Rol.nombre).all()
            for rol in roles:
                self.combo_rol.addItem(f"{rol.nombre} — {rol.descripcion}", rol.id)

    def _cargar_permisos(self):
        # Limpiar grid anterior
        while self.permisos_layout.count():
            item = self.permisos_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._checks.clear()

        rol_id = self.combo_rol.currentData()
        if not rol_id:
            return

        with get_db() as db:
            modulos = db.query(Modulo).filter(Modulo.activo == True).order_by(Modulo.orden).all()
            permisos = db.query(Permiso).all()

            # Permisos actuales del rol
            rol_perms = db.query(RolPermiso).filter(RolPermiso.rol_id == rol_id).all()
            permisos_activos = set(rp.permiso_id for rp in rol_perms)

            # Header
            self.permisos_layout.addWidget(QLabel("Modulo"), 0, 0)
            for j, accion in enumerate(ACCIONES):
                lbl = QLabel(accion.capitalize())
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setStyleSheet("font-weight: bold; font-size: 11px;")
                self.permisos_layout.addWidget(lbl, 0, j + 1)

            # Filas por modulo
            for i, modulo in enumerate(modulos):
                lbl_mod = QLabel(modulo.nombre)
                lbl_mod.setStyleSheet("font-size: 13px;")
                self.permisos_layout.addWidget(lbl_mod, i + 1, 0)

                for j, accion in enumerate(ACCIONES):
                    # Buscar permiso_id para este modulo+accion
                    perm = next((p for p in permisos if p.modulo_id == modulo.id and p.accion == accion), None)
                    if perm:
                        chk = QCheckBox()
                        chk.setChecked(perm.id in permisos_activos)
                        self.permisos_layout.addWidget(chk, i + 1, j + 1, alignment=Qt.AlignCenter)
                        self._checks[(modulo.id, accion)] = chk

            rol = db.get(Rol, rol_id)
            usuarios_count = len(rol.usuarios) if rol else 0
            self.lbl_info.setText(f"{usuarios_count} usuario(s) con este rol")

    def _guardar_permisos(self):
        rol_id = self.combo_rol.currentData()
        if not rol_id:
            QMessageBox.warning(self, "Error", "Selecciona un rol.")
            return

        with get_db() as db:
            # Borrar permisos actuales del rol
            db.query(RolPermiso).filter(RolPermiso.rol_id == rol_id).delete()

            # Insertar los marcados
            permisos = db.query(Permiso).all()
            for (modulo_id, accion), chk in self._checks.items():
                if chk.isChecked():
                    perm = next((p for p in permisos if p.modulo_id == modulo_id and p.accion == accion), None)
                    if perm:
                        db.add(RolPermiso(rol_id=rol_id, permiso_id=perm.id))

        QMessageBox.information(self, "OK", "Permisos guardados correctamente.")

    def _crear_rol(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return
        desc = self.input_desc.text().strip()
        try:
            with get_db() as db:
                db.add(Rol(nombre=nombre, descripcion=desc))
            self.input_nombre.clear()
            self.input_desc.clear()
            self._cargar_roles()
            QMessageBox.information(self, "OK", f"Rol '{nombre}' creado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
