from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QComboBox, QDateEdit, QTimeEdit, QPushButton,
    QLabel, QMessageBox, QFrame, QGridLayout,
    QCheckBox, QLineEdit, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, QDate, QTime
from datetime import date
from ui.components.data_table import DataTable
from modulos.empleados.views.editar_asistencia_dialog import EditarAsistenciaDialog
from services.asistencia_service import asistencia_service
from services.permiso_ausencia_service import permiso_ausencia_service
from services.empleado_service import empleado_service
from services.export_service import exportar_excel
import os


class AsistenciaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._empleados = []
        self._registros = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        tabs = QTabWidget()
        tabs.addTab(self._build_registro_tab(), "Registro")
        tabs.addTab(self._build_permisos_tab(), "Permisos / Licencias")
        tabs.addTab(self._build_ausencias_tab(), "Ausencias")
        layout.addWidget(tabs)

    # === TAB REGISTRO ===
    def _build_registro_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        # Formulario
        form_frame = QFrame()
        form_frame.setObjectName("card")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(10)

        lbl = QLabel("Registrar Asistencia")
        lbl.setStyleSheet("font-size: 15px; font-weight: bold;")
        form_layout.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(10)

        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Empleado"))
        self.combo_empleado = QComboBox()
        self.combo_empleado.setMinimumHeight(34)
        col1.addWidget(self.combo_empleado)
        row.addLayout(col1)

        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Fecha"))
        self.input_fecha = QDateEdit()
        self.input_fecha.setMinimumHeight(34)
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate.currentDate())
        col2.addWidget(self.input_fecha)
        row.addLayout(col2)

        col3 = QVBoxLayout()
        col3.addWidget(QLabel("Entrada"))
        self.input_entrada = QTimeEdit()
        self.input_entrada.setMinimumHeight(34)
        self.input_entrada.setTime(QTime(8, 0))
        self.input_entrada.setDisplayFormat("HH:mm")
        col3.addWidget(self.input_entrada)
        row.addLayout(col3)

        col4 = QVBoxLayout()
        col4.addWidget(QLabel("Salida"))
        self.input_salida = QTimeEdit()
        self.input_salida.setMinimumHeight(34)
        self.input_salida.setTime(QTime(17, 0))
        self.input_salida.setDisplayFormat("HH:mm")
        col4.addWidget(self.input_salida)
        row.addLayout(col4)

        col5 = QVBoxLayout()
        col5.addWidget(QLabel(""))
        self.btn_registrar = QPushButton("Registrar")
        self.btn_registrar.setMinimumHeight(34)
        self.btn_registrar.setCursor(Qt.PointingHandCursor)
        self.btn_registrar.clicked.connect(self._registrar)
        col5.addWidget(self.btn_registrar)
        row.addLayout(col5)

        form_layout.addLayout(row)
        layout.addWidget(form_frame)

        # Tabla
        self.tabla = DataTable(["Empleado", "Fecha", "Entrada", "Salida", "Tipo Dia", "Hs Normales", "Hs Extra"])
        self.tabla.btn_nuevo.hide()
        self.tabla.btn_buscar.setText("Filtrar")
        self.tabla.input_busqueda.setPlaceholderText("Buscar empleado...")
        self.tabla.btn_buscar.clicked.connect(self._cargar_lista)
        self.tabla.input_busqueda.returnPressed.connect(self._cargar_lista)
        self.tabla.row_double_clicked.connect(self._editar_registro)
        layout.addWidget(self.tabla)

        # Filtro periodo
        filtro_row = QHBoxLayout()
        filtro_row.addWidget(QLabel("Periodo:"))
        self.filtro_periodo = QLineEdit()
        self.filtro_periodo.setMinimumHeight(32)
        self.filtro_periodo.setPlaceholderText("YYYY-MM (vacio = todos)")
        self.filtro_periodo.setMaximumWidth(180)
        self.filtro_periodo.returnPressed.connect(self._cargar_lista)
        filtro_row.addWidget(self.filtro_periodo)
        filtro_row.addStretch()
        layout.addLayout(filtro_row)

        # Barra inferior
        bottom = QHBoxLayout()
        bottom.addStretch()

        btn_export = QPushButton("Exportar Excel")
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.setStyleSheet("QPushButton { background-color: #10b981; } QPushButton:hover { background-color: #059669; }")
        btn_export.clicked.connect(self._exportar)
        bottom.addWidget(btn_export)

        btn_editar = QPushButton("Editar registro")
        btn_editar.setCursor(Qt.PointingHandCursor)
        btn_editar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_editar.clicked.connect(self._editar_seleccionado)
        bottom.addWidget(btn_editar)
        layout.addLayout(bottom)

        self._cargar_empleados()
        self._cargar_lista()
        return page

    def _cargar_empleados(self):
        self._empleados = asistencia_service.listar_empleados_activos()
        self.combo_empleado.clear()
        for emp in self._empleados:
            self.combo_empleado.addItem(f"{emp.apellido}, {emp.nombre}", emp.id)
        self.combo_empleado.currentIndexChanged.connect(self._on_empleado_changed)
        if self._empleados:
            self._on_empleado_changed()

    def _on_empleado_changed(self):
        idx = self.combo_empleado.currentIndex()
        if idx < 0 or idx >= len(self._empleados):
            return
        emp = self._empleados[idx]
        if emp.hora_entrada:
            h, m = emp.hora_entrada.split(":")
            self.input_entrada.setTime(QTime(int(h), int(m)))
        if emp.hora_salida:
            h, m = emp.hora_salida.split(":")
            self.input_salida.setTime(QTime(int(h), int(m)))

    def _registrar(self):
        emp_id = self.combo_empleado.currentData()
        if not emp_id:
            QMessageBox.warning(self, "Error", "Selecciona un empleado.")
            return
        fecha = self.input_fecha.date().toPython()
        entrada = self.input_entrada.time().toPython()
        salida = self.input_salida.time().toPython()
        if entrada == salida:
            QMessageBox.warning(self, "Error", "Entrada y salida no pueden ser iguales.")
            return
        try:
            reg = asistencia_service.registrar(emp_id, fecha, entrada, salida)
            QMessageBox.information(self, "Registrado",
                f"Dia: {reg.tipo_dia.upper()} | Normales: {reg.horas_normales}h | Extra: {reg.horas_extra}h")
            self._cargar_lista()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _cargar_lista(self):
        busqueda = self.tabla.input_busqueda.text().strip().lower()
        periodo_filtro = self.filtro_periodo.text().strip()
        self._registros = asistencia_service.listar()
        rows = []
        for r in self._registros:
            nombre = f"{r.empleado.apellido}, {r.empleado.nombre}" if r.empleado else ""
            if busqueda and busqueda not in nombre.lower():
                continue
            if periodo_filtro and not r.fecha.strftime("%Y-%m").startswith(periodo_filtro):
                continue
            rows.append((r.id, [
                nombre,
                r.fecha.strftime("%d/%m/%Y"),
                r.hora_entrada.strftime("%H:%M") if r.hora_entrada else "",
                r.hora_salida.strftime("%H:%M") if r.hora_salida else "",
                r.tipo_dia.capitalize(),
                str(r.horas_normales),
                str(r.horas_extra),
            ]))
        self.tabla.set_data(rows)

    def _editar_registro(self, registro_id: int):
        reg = next((r for r in self._registros if r.id == registro_id), None)
        if not reg:
            return
        dialog = EditarAsistenciaDialog(reg, parent=self)
        dialog.registro_actualizado.connect(self._cargar_lista)
        dialog.exec()

    def _editar_seleccionado(self):
        reg_id = self.tabla.selected_id()
        if not reg_id:
            QMessageBox.information(self, "Seleccion", "Selecciona un registro.")
            return
        self._editar_registro(reg_id)

    def _exportar(self):
        headers = ["Empleado", "Fecha", "Entrada", "Salida", "Tipo Dia", "Hs Normales", "Hs Extra"]
        rows = []
        for r in self._registros:
            nombre = f"{r.empleado.apellido}, {r.empleado.nombre}" if r.empleado else ""
            rows.append([nombre, r.fecha.strftime("%d/%m/%Y"),
                r.hora_entrada.strftime("%H:%M") if r.hora_entrada else "",
                r.hora_salida.strftime("%H:%M") if r.hora_salida else "",
                r.tipo_dia.capitalize(), float(r.horas_normales), float(r.horas_extra)])
        try:
            path = exportar_excel("asistencia.xlsx", headers, rows, "Registros de Asistencia")
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === TAB PERMISOS ===
    def _build_permisos_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        grp = QGroupBox("Registrar Permiso / Licencia")
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        form = QGridLayout(grp)
        form.setSpacing(8)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        form.addWidget(QLabel("Empleado:"), 0, 0)
        self.perm_empleado = QComboBox()
        self.perm_empleado.setMinimumHeight(32)
        form.addWidget(self.perm_empleado, 0, 1)

        form.addWidget(QLabel("Tipo:"), 0, 2)
        self.perm_tipo = QComboBox()
        self.perm_tipo.setMinimumHeight(32)
        form.addWidget(self.perm_tipo, 0, 3)

        form.addWidget(QLabel("Desde:"), 1, 0)
        self.perm_desde = QDateEdit()
        self.perm_desde.setMinimumHeight(32)
        self.perm_desde.setCalendarPopup(True)
        self.perm_desde.setDate(QDate.currentDate())
        form.addWidget(self.perm_desde, 1, 1)

        form.addWidget(QLabel("Hasta:"), 1, 2)
        self.perm_hasta = QDateEdit()
        self.perm_hasta.setMinimumHeight(32)
        self.perm_hasta.setCalendarPopup(True)
        self.perm_hasta.setDate(QDate.currentDate())
        form.addWidget(self.perm_hasta, 1, 3)

        form.addWidget(QLabel("Motivo:"), 2, 0)
        self.perm_motivo = QLineEdit()
        self.perm_motivo.setMinimumHeight(32)
        form.addWidget(self.perm_motivo, 2, 1, 1, 2)

        btn_perm = QPushButton("Registrar Permiso")
        btn_perm.setMinimumHeight(34)
        btn_perm.clicked.connect(self._registrar_permiso)
        form.addWidget(btn_perm, 2, 3)

        layout.addWidget(grp)

        self.tabla_permisos = QTableWidget()
        self.tabla_permisos.setColumnCount(6)
        self.tabla_permisos.setHorizontalHeaderLabels(["Empleado", "Tipo", "Desde", "Hasta", "Dias", "Motivo"])
        self.tabla_permisos.horizontalHeader().setStretchLastSection(True)
        self.tabla_permisos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_permisos.setAlternatingRowColors(True)
        self.tabla_permisos.verticalHeader().setVisible(False)
        self.tabla_permisos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_permisos)

        self._cargar_permisos_data()
        return page

    def _cargar_permisos_data(self):
        emps = empleado_service.listar()
        self.perm_empleado.clear()
        for e in emps:
            self.perm_empleado.addItem(f"{e.apellido}, {e.nombre}", e.id)

        tipos = permiso_ausencia_service.listar_tipos()
        self.perm_tipo.clear()
        for t in tipos:
            self.perm_tipo.addItem(t.nombre, t.id)

        self._cargar_tabla_permisos()

    def _cargar_tabla_permisos(self):
        permisos = permiso_ausencia_service.listar_permisos()
        self.tabla_permisos.setRowCount(len(permisos))
        for i, p in enumerate(permisos):
            nombre = f"{p.empleado.apellido}, {p.empleado.nombre}" if p.empleado else ""
            self.tabla_permisos.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla_permisos.setItem(i, 1, QTableWidgetItem(p.tipo_permiso.nombre if p.tipo_permiso else ""))
            self.tabla_permisos.setItem(i, 2, QTableWidgetItem(p.fecha_desde.strftime("%d/%m/%Y")))
            self.tabla_permisos.setItem(i, 3, QTableWidgetItem(p.fecha_hasta.strftime("%d/%m/%Y")))
            self.tabla_permisos.setItem(i, 4, QTableWidgetItem(str(p.dias)))
            self.tabla_permisos.setItem(i, 5, QTableWidgetItem(p.motivo or ""))

    def _registrar_permiso(self):
        emp_id = self.perm_empleado.currentData()
        tipo_id = self.perm_tipo.currentData()
        if not emp_id or not tipo_id:
            QMessageBox.warning(self, "Error", "Selecciona empleado y tipo.")
            return
        desde = self.perm_desde.date().toPython()
        hasta = self.perm_hasta.date().toPython()
        if hasta < desde:
            QMessageBox.warning(self, "Error", "Fecha hasta no puede ser anterior a desde.")
            return
        motivo = self.perm_motivo.text().strip()
        try:
            permiso_ausencia_service.crear_permiso(emp_id, tipo_id, desde, hasta, motivo)
            self.perm_motivo.clear()
            self._cargar_tabla_permisos()
            QMessageBox.information(self, "OK", "Permiso registrado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === TAB AUSENCIAS ===
    def _build_ausencias_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        grp = QGroupBox("Registrar Ausencia")
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        form = QGridLayout(grp)
        form.setSpacing(8)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        form.addWidget(QLabel("Empleado:"), 0, 0)
        self.aus_empleado = QComboBox()
        self.aus_empleado.setMinimumHeight(32)
        form.addWidget(self.aus_empleado, 0, 1)

        form.addWidget(QLabel("Fecha:"), 0, 2)
        self.aus_fecha = QDateEdit()
        self.aus_fecha.setMinimumHeight(32)
        self.aus_fecha.setCalendarPopup(True)
        self.aus_fecha.setDate(QDate.currentDate())
        form.addWidget(self.aus_fecha, 0, 3)

        form.addWidget(QLabel("Motivo:"), 1, 0)
        self.aus_motivo = QLineEdit()
        self.aus_motivo.setMinimumHeight(32)
        form.addWidget(self.aus_motivo, 1, 1)

        self.aus_justificada = QCheckBox("Justificada")
        form.addWidget(self.aus_justificada, 1, 2)

        btn_aus = QPushButton("Registrar")
        btn_aus.setMinimumHeight(34)
        btn_aus.clicked.connect(self._registrar_ausencia)
        form.addWidget(btn_aus, 1, 3)

        layout.addWidget(grp)

        self.tabla_ausencias = QTableWidget()
        self.tabla_ausencias.setColumnCount(5)
        self.tabla_ausencias.setHorizontalHeaderLabels(["Empleado", "Fecha", "Periodo", "Justificada", "Motivo"])
        self.tabla_ausencias.horizontalHeader().setStretchLastSection(True)
        self.tabla_ausencias.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_ausencias.setAlternatingRowColors(True)
        self.tabla_ausencias.verticalHeader().setVisible(False)
        self.tabla_ausencias.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_ausencias)

        self._cargar_ausencias_data()
        return page

    def _cargar_ausencias_data(self):
        emps = empleado_service.listar()
        self.aus_empleado.clear()
        for e in emps:
            self.aus_empleado.addItem(f"{e.apellido}, {e.nombre}", e.id)
        self._cargar_tabla_ausencias()

    def _cargar_tabla_ausencias(self):
        ausencias = permiso_ausencia_service.listar_ausencias()
        self.tabla_ausencias.setRowCount(len(ausencias))
        for i, a in enumerate(ausencias):
            nombre = f"{a.empleado.apellido}, {a.empleado.nombre}" if a.empleado else ""
            self.tabla_ausencias.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla_ausencias.setItem(i, 1, QTableWidgetItem(a.fecha.strftime("%d/%m/%Y")))
            self.tabla_ausencias.setItem(i, 2, QTableWidgetItem(a.periodo))
            self.tabla_ausencias.setItem(i, 3, QTableWidgetItem("Si" if a.justificada else "No"))
            self.tabla_ausencias.setItem(i, 4, QTableWidgetItem(a.motivo or ""))

    def _registrar_ausencia(self):
        emp_id = self.aus_empleado.currentData()
        if not emp_id:
            QMessageBox.warning(self, "Error", "Selecciona un empleado.")
            return
        fecha = self.aus_fecha.date().toPython()
        justificada = self.aus_justificada.isChecked()
        motivo = self.aus_motivo.text().strip()
        try:
            permiso_ausencia_service.registrar_ausencia(emp_id, fecha, justificada, motivo)
            self.aus_motivo.clear()
            self.aus_justificada.setChecked(False)
            self._cargar_tabla_ausencias()
            QMessageBox.information(self, "OK", "Ausencia registrada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
