from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QMessageBox, QCheckBox, QPushButton,
)
from PySide6.QtCore import Qt
from ui.components.data_table import DataTable
from modulos.empleados.views.form_empleado import FormEmpleado
from modulos.empleados.views.detalle_empleado_dialog import EmpleadoDetalleDialog
from services.empleado_service import empleado_service
from services.export_service import exportar_excel
import os


class EmpleadosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar_lista()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        self.stack = QStackedWidget()

        # Página 0: Lista
        lista_page = QWidget()
        lista_layout = QVBoxLayout(lista_page)
        lista_layout.setContentsMargins(0, 0, 0, 0)
        lista_layout.setSpacing(8)

        self.tabla = DataTable(["Apellido", "Nombre", "DNI", "CUIL", "Departamento", "Cargo", "Estado"])
        self.tabla.btn_buscar.clicked.connect(self._cargar_lista)
        self.tabla.input_busqueda.returnPressed.connect(self._cargar_lista)
        self.tabla.btn_nuevo.clicked.connect(self._nuevo)
        self.tabla.row_double_clicked.connect(self._editar)
        lista_layout.addWidget(self.tabla)

        # Barra inferior: filtro + acciones
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(12)

        self.chk_inactivos = QCheckBox("Mostrar inactivos")
        self.chk_inactivos.stateChanged.connect(self._cargar_lista)
        bottom_bar.addWidget(self.chk_inactivos)

        bottom_bar.addStretch()

        self.btn_ver = QPushButton("Ver detalle")
        self.btn_ver.setCursor(Qt.PointingHandCursor)
        self.btn_ver.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        self.btn_ver.clicked.connect(self._ver_detalle)
        bottom_bar.addWidget(self.btn_ver)

        btn_export = QPushButton("Exportar Excel")
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.setStyleSheet("QPushButton { background-color: #10b981; } QPushButton:hover { background-color: #059669; }")
        btn_export.clicked.connect(self._exportar)
        bottom_bar.addWidget(btn_export)

        self.btn_eliminar = QPushButton("Dar de baja")
        self.btn_eliminar.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        self.btn_eliminar.setCursor(Qt.PointingHandCursor)
        self.btn_eliminar.clicked.connect(self._eliminar)
        bottom_bar.addWidget(self.btn_eliminar)

        lista_layout.addLayout(bottom_bar)
        self.stack.addWidget(lista_page)

        # Página 1: Formulario
        self._form_container = QWidget()
        self._form_layout = QVBoxLayout(self._form_container)
        self._form_layout.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(self._form_container)

        layout.addWidget(self.stack)

    def _cargar_lista(self):
        busqueda = self.tabla.input_busqueda.text().strip()
        solo_activos = not self.chk_inactivos.isChecked()
        empleados = empleado_service.listar(busqueda=busqueda, solo_activos=solo_activos)
        rows = []
        for e in empleados:
            rows.append((e.id, [
                e.apellido,
                e.nombre,
                e.dni,
                e.cuil,
                e.departamento.nombre if e.departamento else "—",
                e.cargo.nombre if e.cargo else "—",
                "Activo" if e.activo else "Inactivo",
            ]))
        self.tabla.set_data(rows)

    def _nuevo(self):
        self._mostrar_form(None)

    def _editar(self, empleado_id: int):
        self._mostrar_form(empleado_id)

    def _ver_detalle(self):
        emp_id = self.tabla.selected_id()
        if not emp_id:
            QMessageBox.information(self, "Selección", "Seleccioná un empleado de la lista.")
            return
        dialog = EmpleadoDetalleDialog(emp_id, parent=self)
        dialog.editar_clicked.connect(self._editar)
        dialog.exec()

    def _eliminar(self):
        emp_id = self.tabla.selected_id()
        if not emp_id:
            QMessageBox.information(self, "Selección", "Seleccioná un empleado de la lista.")
            return

        resp = QMessageBox.question(
            self, "Confirmar baja",
            "¿Estás seguro de dar de baja a este empleado?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            empleado_service.eliminar(emp_id)
            self._cargar_lista()

    def _mostrar_form(self, empleado_id: int | None):
        for i in reversed(range(self._form_layout.count())):
            w = self._form_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        form = FormEmpleado(empleado_id=empleado_id)
        form.guardado.connect(self._on_guardado)
        form.cancelado.connect(self._volver_lista)
        self._form_layout.addWidget(form)
        self.stack.setCurrentIndex(1)

    def _on_guardado(self):
        self._volver_lista()
        self._cargar_lista()

    def _volver_lista(self):
        self.stack.setCurrentIndex(0)

    def _exportar(self):
        empleados = empleado_service.listar(solo_activos=not self.chk_inactivos.isChecked())
        headers = ["Apellido", "Nombre", "DNI", "CUIL", "Email", "Departamento", "Cargo", "Valor Hora", "Sueldo Mensual", "Estado"]
        rows = []
        for e in empleados:
            rows.append([
                e.apellido, e.nombre, e.dni, e.cuil, e.email or "",
                e.departamento.nombre if e.departamento else "",
                e.cargo.nombre if e.cargo else "",
                float(e.valor_hora) if e.valor_hora else 0,
                float(e.sueldo_mensual) if e.sueldo_mensual else 0,
                "Activo" if e.activo else "Inactivo",
            ])
        try:
            path = exportar_excel("empleados.xlsx", headers, rows, "Lista de Empleados")
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
