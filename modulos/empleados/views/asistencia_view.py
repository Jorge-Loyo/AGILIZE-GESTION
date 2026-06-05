from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QComboBox, QDateEdit, QTimeEdit, QPushButton,
    QLabel, QMessageBox, QFrame, QGridLayout,
    QCheckBox, QLineEdit, QGroupBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, QDate, QTime
from datetime import date
from ui.components.data_table import DataTable
from modulos.empleados.views.editar_asistencia_dialog import EditarAsistenciaDialog
from modulos.empleados.views.registro_manual_dialog import RegistroManualDialog
from services.asistencia_service import asistencia_service
from services.permiso_ausencia_service import permiso_ausencia_service
from services.empleado_service import empleado_service
from services.export_service import exportar_excel
from services.import_fichadas_service import importar_fichadas
import os


class AsistenciaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        layout.setSpacing(8)

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(8)

        filtros.addWidget(QLabel("Empleado:"))
        self.filtro_empleado = QComboBox()
        self.filtro_empleado.setMinimumHeight(32)
        self.filtro_empleado.setMinimumWidth(200)
        self.filtro_empleado.addItem("Todos", None)
        emps = asistencia_service.listar_empleados_activos()
        emps_sorted = sorted(emps, key=lambda e: int(e.legajo) if e.legajo and e.legajo.isdigit() else 9999)
        for emp in emps_sorted:
            self.filtro_empleado.addItem(f"{emp.legajo} - {emp.nombre} {emp.apellido or ''}", emp.id)
        self.filtro_empleado.currentIndexChanged.connect(self._cargar_lista)
        filtros.addWidget(self.filtro_empleado)

        filtros.addWidget(QLabel("Periodo:"))
        self.filtro_periodo = QLineEdit()
        self.filtro_periodo.setMinimumHeight(32)
        self.filtro_periodo.setPlaceholderText("YYYY-MM")
        self.filtro_periodo.setMaximumWidth(120)
        self.filtro_periodo.returnPressed.connect(self._cargar_lista)
        filtros.addWidget(self.filtro_periodo)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setMinimumHeight(32)
        btn_filtrar.clicked.connect(self._cargar_lista)
        filtros.addWidget(btn_filtrar)

        filtros.addWidget(QLabel("Ordenar:"))
        self.filtro_orden = QComboBox()
        self.filtro_orden.setMinimumHeight(32)
        self.filtro_orden.addItem("Fecha", "fecha")
        self.filtro_orden.addItem("Legajo", "legajo")
        self.filtro_orden.addItem("Nombre", "nombre")
        self.filtro_orden.addItem("Apellido", "apellido")
        self.filtro_orden.currentIndexChanged.connect(self._cargar_lista)
        filtros.addWidget(self.filtro_orden)

        filtros.addStretch()
        layout.addLayout(filtros)

        # Tabla
        self.tabla = DataTable(["Empleado", "Fecha", "Entrada", "Salida", "Tipo Dia", "Hs Normales", "Hs Extra", "Estado"])
        self.tabla.btn_nuevo.hide()
        self.tabla.btn_buscar.hide()
        self.tabla.input_busqueda.hide()
        self.tabla.row_double_clicked.connect(self._editar_registro)
        layout.addWidget(self.tabla)

        # Barra inferior con botones
        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        bottom.addStretch()

        btn_manual = QPushButton("  Registro Manual")
        btn_manual.setCursor(Qt.PointingHandCursor)
        btn_manual.clicked.connect(self._registro_manual)
        bottom.addWidget(btn_manual)

        btn_importar = QPushButton("  Importar Fichadas")
        btn_importar.setCursor(Qt.PointingHandCursor)
        btn_importar.setStyleSheet("QPushButton { background-color: #6366f1; } QPushButton:hover { background-color: #4f46e5; }")
        btn_importar.clicked.connect(self._importar_fichadas)
        bottom.addWidget(btn_importar)

        btn_export = QPushButton("  Exportar Excel")
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.setStyleSheet("QPushButton { background-color: #10b981; } QPushButton:hover { background-color: #059669; }")
        btn_export.clicked.connect(self._exportar)
        bottom.addWidget(btn_export)

        btn_editar = QPushButton("  Editar")
        btn_editar.setCursor(Qt.PointingHandCursor)
        btn_editar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_editar.clicked.connect(self._editar_seleccionado)
        bottom.addWidget(btn_editar)

        layout.addLayout(bottom)

        self._cargar_lista()
        return page

    def _registro_manual(self):
        dialog = RegistroManualDialog(parent=self)
        dialog.registro_creado.connect(self._cargar_lista)
        dialog.exec()

    def _cargar_lista(self):
        emp_id_filtro = self.filtro_empleado.currentData()
        periodo_filtro = self.filtro_periodo.text().strip()
        self._registros = asistencia_service.listar(empleado_id=emp_id_filtro)
        # Filtrar por periodo
        registros_filtrados = self._registros
        if periodo_filtro:
            registros_filtrados = [r for r in self._registros if r.fecha.strftime("%Y-%m").startswith(periodo_filtro)]
        # Ordenar
        orden = self.filtro_orden.currentData() if hasattr(self, 'filtro_orden') else "fecha"
        if orden == "fecha":
            registros_filtrados.sort(key=lambda r: r.fecha)
        elif orden == "legajo":
            registros_filtrados.sort(key=lambda r: int(r.empleado.legajo) if r.empleado and r.empleado.legajo and r.empleado.legajo.isdigit() else 9999)
        elif orden == "nombre":
            registros_filtrados.sort(key=lambda r: r.empleado.nombre.lower() if r.empleado else "")
        elif orden == "apellido":
            registros_filtrados.sort(key=lambda r: (r.empleado.apellido or "").lower() if r.empleado else "")

        rows = []
        for r in registros_filtrados:
            nombre = f"{r.empleado.nombre} {r.empleado.apellido or ''}" if r.empleado else ""
            estado = "INCOMPLETO" if getattr(r, 'incompleto', False) else "OK"
            rows.append((r.id, [
                nombre,
                r.fecha.strftime("%d/%m/%Y"),
                r.hora_entrada.strftime("%H:%M") if r.hora_entrada else "",
                r.hora_salida.strftime("%H:%M") if r.hora_salida else "",
                r.tipo_dia.capitalize(),
                str(r.horas_normales),
                str(r.horas_extra),
                estado,
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
            nombre = f"{r.empleado.apellido or ''}, {r.empleado.nombre}" if r.empleado else ""
            rows.append([nombre, r.fecha.strftime("%d/%m/%Y"),
                r.hora_entrada.strftime("%H:%M") if r.hora_entrada else "",
                r.hora_salida.strftime("%H:%M") if r.hora_salida else "",
                r.tipo_dia.capitalize(), float(r.horas_normales), float(r.horas_extra)])
        try:
            path = exportar_excel("asistencia.xlsx", headers, rows, "Registros de Asistencia")
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _importar_fichadas(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de fichadas", "", "Excel (*.xlsx *.xls)"
        )
        if not filepath:
            return
        try:
            resultado = importar_fichadas(filepath)
            msg = f"Fichadas importadas: {resultado['importados']}\n"
            if resultado["no_encontrados"]:
                msg += f"\nEmpleados no encontrados ({len(resultado['no_encontrados'])}):\n"
                msg += "\n".join(f"  - {n}" for n in resultado["no_encontrados"][:10])
            if resultado["errores"]:
                msg += f"\n\nErrores: {len(resultado['errores'])}"
                msg += "\n".join(f"  - {e}" for e in resultado["errores"][:5])
            QMessageBox.information(self, "Importacion de Fichadas", msg)
            self._cargar_lista()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al importar: {e}")

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
            self.perm_empleado.addItem(f"{e.legajo} - {e.nombre} {e.apellido or ''}", e.id)
        tipos = permiso_ausencia_service.listar_tipos()
        self.perm_tipo.clear()
        for t in tipos:
            self.perm_tipo.addItem(t.nombre, t.id)
        self._cargar_tabla_permisos()

    def _cargar_tabla_permisos(self):
        permisos = permiso_ausencia_service.listar_permisos()
        self.tabla_permisos.setRowCount(len(permisos))
        for i, p in enumerate(permisos):
            nombre = f"{p.empleado.nombre} {p.empleado.apellido or ''}" if p.empleado else ""
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
            self.aus_empleado.addItem(f"{e.legajo} - {e.nombre} {e.apellido or ''}", e.id)
        self._cargar_tabla_ausencias()

    def _cargar_tabla_ausencias(self):
        ausencias = permiso_ausencia_service.listar_ausencias()
        self.tabla_ausencias.setRowCount(len(ausencias))
        for i, a in enumerate(ausencias):
            nombre = f"{a.empleado.nombre} {a.empleado.apellido or ''}" if a.empleado else ""
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
