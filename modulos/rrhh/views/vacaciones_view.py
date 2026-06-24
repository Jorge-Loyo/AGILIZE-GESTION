from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QDateEdit, QLineEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QGridLayout,
)
from PySide6.QtCore import Qt, QDate
from datetime import date
from services.rrhh.vacaciones_service import vacaciones_service, calcular_dias_por_antiguedad
from services.rrhh.empleado_service import empleado_service
from services.core.auth_service import auth_service


class VacacionesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        # Formulario de solicitud
        grp = QGroupBox("Solicitar Vacaciones")
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        form = QGridLayout(grp)
        form.setSpacing(8)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        form.addWidget(QLabel("Empleado:"), 0, 0)
        self.combo_emp = QComboBox()
        self.combo_emp.setMinimumHeight(32)
        self.combo_emp.currentIndexChanged.connect(self._actualizar_saldo)
        form.addWidget(self.combo_emp, 0, 1)

        form.addWidget(QLabel("Periodo:"), 0, 2)
        self.spin_periodo = QSpinBox()
        self.spin_periodo.setMinimumHeight(32)
        self.spin_periodo.setRange(2020, 2050)
        self.spin_periodo.setValue(date.today().year)
        self.spin_periodo.valueChanged.connect(self._actualizar_saldo)
        form.addWidget(self.spin_periodo, 0, 3)

        form.addWidget(QLabel("Desde:"), 1, 0)
        self.date_desde = QDateEdit()
        self.date_desde.setMinimumHeight(32)
        self.date_desde.setCalendarPopup(True)
        self.date_desde.setDate(QDate.currentDate())
        form.addWidget(self.date_desde, 1, 1)

        form.addWidget(QLabel("Hasta:"), 1, 2)
        self.date_hasta = QDateEdit()
        self.date_hasta.setMinimumHeight(32)
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.setDate(QDate.currentDate().addDays(13))
        form.addWidget(self.date_hasta, 1, 3)

        form.addWidget(QLabel("Obs.:"), 2, 0)
        self.txt_obs = QLineEdit()
        self.txt_obs.setMinimumHeight(32)
        form.addWidget(self.txt_obs, 2, 1, 1, 2)

        btn_solicitar = QPushButton("Solicitar")
        btn_solicitar.setMinimumHeight(34)
        btn_solicitar.clicked.connect(self._solicitar)
        form.addWidget(btn_solicitar, 2, 3)

        layout.addWidget(grp)

        # Saldo
        self.lbl_saldo = QLabel("")
        self.lbl_saldo.setStyleSheet("font-size: 13px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(self.lbl_saldo)

        # Filtro tabla
        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Filtrar empleado:"))
        self.filtro_emp = QComboBox()
        self.filtro_emp.setMinimumHeight(32)
        self.filtro_emp.addItem("Todos", None)
        self.filtro_emp.currentIndexChanged.connect(self._cargar_tabla)
        filtros.addWidget(self.filtro_emp)
        filtros.addStretch()
        layout.addLayout(filtros)

        # Tabla de vacaciones
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Empleado", "Periodo", "Dias", "Desde", "Hasta", "Estado", "Aprobado por", "Obs."
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabla)

        # Botones de acción
        btns = QHBoxLayout()
        btns.addStretch()

        btn_aprobar = QPushButton("Aprobar")
        btn_aprobar.setMinimumHeight(34)
        btn_aprobar.setStyleSheet("QPushButton { background-color: #10b981; } QPushButton:hover { background-color: #059669; }")
        btn_aprobar.clicked.connect(self._aprobar)
        btns.addWidget(btn_aprobar)

        btn_tomar = QPushButton("Marcar Tomada")
        btn_tomar.setMinimumHeight(34)
        btn_tomar.clicked.connect(self._tomar)
        btns.addWidget(btn_tomar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(34)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_cancelar.clicked.connect(self._cancelar)
        btns.addWidget(btn_cancelar)

        layout.addLayout(btns)

    def _cargar_datos(self):
        emps = empleado_service.listar()
        emps.sort(key=lambda e: int(e.legajo) if e.legajo and e.legajo.isdigit() else 9999)
        self.combo_emp.clear()
        self.filtro_emp.clear()
        self.filtro_emp.addItem("Todos", None)
        for emp in emps:
            label = f"{emp.legajo} - {emp.nombre} {emp.apellido or ''}"
            self.combo_emp.addItem(label, emp.id)
            self.filtro_emp.addItem(label, emp.id)
        self._actualizar_saldo()
        self._cargar_tabla()

    def _actualizar_saldo(self):
        emp_id = self.combo_emp.currentData()
        periodo = self.spin_periodo.value()
        if not emp_id:
            self.lbl_saldo.setText("")
            return
        saldo = vacaciones_service.obtener_saldo(emp_id, periodo)
        self.lbl_saldo.setText(
            f"Dias correspondientes: {saldo['correspondientes']}  |  "
            f"Tomados: {saldo['tomados']}  |  "
            f"Disponibles: {saldo['disponibles']}"
        )

    def _cargar_tabla(self):
        emp_id = self.filtro_emp.currentData()
        registros = vacaciones_service.listar(empleado_id=emp_id)
        self._registros = registros
        self.tabla.setRowCount(len(registros))
        for i, v in enumerate(registros):
            nombre = f"{v.empleado.nombre} {v.empleado.apellido or ''}" if v.empleado else ""
            self.tabla.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla.setItem(i, 1, QTableWidgetItem(str(v.periodo_anual)))
            self.tabla.setItem(i, 2, QTableWidgetItem(str(v.dias_tomados)))
            self.tabla.setItem(i, 3, QTableWidgetItem(v.fecha_desde.strftime("%d/%m/%Y") if v.fecha_desde else ""))
            self.tabla.setItem(i, 4, QTableWidgetItem(v.fecha_hasta.strftime("%d/%m/%Y") if v.fecha_hasta else ""))
            item_estado = QTableWidgetItem(v.estado.capitalize())
            colores = {"pendiente": "#f59e0b", "aprobada": "#3b82f6", "tomada": "#10b981", "cancelada": "#ef4444"}
            item_estado.setForeground(Qt.GlobalColor.white)
            self.tabla.setItem(i, 5, item_estado)
            aprobador = v.aprobador.nombre_completo if v.aprobador else ""
            self.tabla.setItem(i, 6, QTableWidgetItem(aprobador))
            self.tabla.setItem(i, 7, QTableWidgetItem(v.observaciones or ""))

    def _selected_vac(self):
        row = self.tabla.currentRow()
        if row < 0 or row >= len(self._registros):
            return None
        return self._registros[row]

    def _solicitar(self):
        emp_id = self.combo_emp.currentData()
        if not emp_id:
            QMessageBox.warning(self, "Error", "Selecciona un empleado.")
            return
        desde = self.date_desde.date().toPython()
        hasta = self.date_hasta.date().toPython()
        if hasta < desde:
            QMessageBox.warning(self, "Error", "Fecha hasta debe ser posterior a desde.")
            return
        periodo = self.spin_periodo.value()
        obs = self.txt_obs.text().strip()
        try:
            vacaciones_service.solicitar(emp_id, periodo, desde, hasta, obs)
            self._actualizar_saldo()
            self._cargar_tabla()
            QMessageBox.information(self, "OK", "Vacaciones solicitadas.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _aprobar(self):
        vac = self._selected_vac()
        if not vac:
            QMessageBox.information(self, "Info", "Selecciona un registro.")
            return
        if vac.estado != "pendiente":
            QMessageBox.warning(self, "Error", "Solo se pueden aprobar solicitudes pendientes.")
            return
        user = auth_service.current_user
        vacaciones_service.aprobar(vac.id, user.id if user else None)
        self._cargar_tabla()

    def _tomar(self):
        vac = self._selected_vac()
        if not vac:
            QMessageBox.information(self, "Info", "Selecciona un registro.")
            return
        if vac.estado != "aprobada":
            QMessageBox.warning(self, "Error", "Solo se pueden tomar vacaciones aprobadas.")
            return
        vacaciones_service.tomar(vac.id)
        self._cargar_tabla()

    def _cancelar(self):
        vac = self._selected_vac()
        if not vac:
            QMessageBox.information(self, "Info", "Selecciona un registro.")
            return
        if vac.estado == "cancelada":
            return
        resp = QMessageBox.question(self, "Cancelar", "Cancelar esta solicitud de vacaciones?", QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            vacaciones_service.cancelar(vac.id)
            self._actualizar_saldo()
            self._cargar_tabla()
