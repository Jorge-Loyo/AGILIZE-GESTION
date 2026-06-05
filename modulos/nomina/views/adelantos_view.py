from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QLabel, QSpinBox,
    QMessageBox, QComboBox, QDoubleSpinBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt
from decimal import Decimal
from datetime import date
from services.adelanto_service import adelanto_service
from services.empleado_service import empleado_service


class AdelantosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar_empleados()
        self._cargar_adelantos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # === Info del empleado ===
        grp_info = QGroupBox("Situación del Empleado")
        grp_info.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px; margin-top: 8px; }")
        info_layout = QGridLayout(grp_info)
        info_layout.setSpacing(10)
        info_layout.setColumnStretch(1, 1)
        info_layout.setColumnStretch(3, 1)

        info_layout.addWidget(QLabel("Empleado:"), 0, 0)
        self.combo_empleado = QComboBox()
        self.combo_empleado.setMinimumHeight(36)
        self.combo_empleado.currentIndexChanged.connect(self._actualizar_info)
        info_layout.addWidget(self.combo_empleado, 0, 1)

        info_layout.addWidget(QLabel("Período actual:"), 0, 2)
        self.lbl_periodo = QLabel(date.today().strftime("%Y-%m"))
        self.lbl_periodo.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.lbl_periodo, 0, 3)

        self.lbl_horas = QLabel("Horas trabajadas: —")
        info_layout.addWidget(self.lbl_horas, 1, 0, 1, 2)
        self.lbl_generado = QLabel("Monto generado: —")
        info_layout.addWidget(self.lbl_generado, 1, 2, 1, 2)
        self.lbl_saldo = QLabel("Saldo adelantos pendientes: —")
        self.lbl_saldo.setStyleSheet("color: #ef4444; font-weight: bold;")
        info_layout.addWidget(self.lbl_saldo, 2, 0, 1, 4)

        layout.addWidget(grp_info)

        # === Form registrar ===
        grp = QGroupBox("Registrar Adelanto")
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px; margin-top: 8px; }")
        form = QGridLayout(grp)
        form.setSpacing(10)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        form.addWidget(QLabel("Monto:"), 0, 0)
        self.adelanto_monto = QDoubleSpinBox()
        self.adelanto_monto.setMinimumHeight(36)
        self.adelanto_monto.setRange(0, 9999999)
        self.adelanto_monto.setDecimals(2)
        self.adelanto_monto.setPrefix("$ ")
        form.addWidget(self.adelanto_monto, 0, 1)

        form.addWidget(QLabel("Cuotas:"), 0, 2)
        self.adelanto_cuotas = QSpinBox()
        self.adelanto_cuotas.setMinimumHeight(36)
        self.adelanto_cuotas.setRange(1, 24)
        self.adelanto_cuotas.setValue(1)
        form.addWidget(self.adelanto_cuotas, 0, 3)

        form.addWidget(QLabel("Motivo:"), 1, 0)
        self.adelanto_motivo = QLineEdit()
        self.adelanto_motivo.setMinimumHeight(36)
        self.adelanto_motivo.setPlaceholderText("Opcional")
        form.addWidget(self.adelanto_motivo, 1, 1)

        btn_registrar = QPushButton("Registrar Adelanto")
        btn_registrar.setMinimumHeight(38)
        btn_registrar.clicked.connect(self._registrar_adelanto)
        form.addWidget(btn_registrar, 1, 3)

        layout.addWidget(grp)

        # === Tabla ===
        self.tabla_adelantos = QTableWidget()
        self.tabla_adelantos.setColumnCount(7)
        self.tabla_adelantos.setHorizontalHeaderLabels([
            "Empleado", "Fecha", "Monto", "Cuotas", "Descontado", "Saldo", "Estado"
        ])
        self.tabla_adelantos.horizontalHeader().setStretchLastSection(True)
        self.tabla_adelantos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_adelantos.setAlternatingRowColors(True)
        self.tabla_adelantos.verticalHeader().setVisible(False)
        self.tabla_adelantos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_adelantos)

    def _cargar_empleados(self):
        empleados = empleado_service.listar()
        self.combo_empleado.clear()
        for emp in empleados:
            self.combo_empleado.addItem(f"{emp.apellido}, {emp.nombre}", emp.id)
        if empleados:
            self._actualizar_info()

    def _actualizar_info(self):
        emp_id = self.combo_empleado.currentData()
        if not emp_id:
            return
        periodo = date.today().strftime("%Y-%m")
        info = adelanto_service.info_empleado_periodo(emp_id, periodo)
        self.lbl_horas.setText(f"Horas trabajadas: {info['horas_totales']} hs (N: {info['horas_normales']} | E: {info['horas_extra']})")
        self.lbl_generado.setText(f"Monto generado: $ {info['monto_generado']:,.2f}")
        self.lbl_saldo.setText(f"Saldo adelantos pendientes: $ {info['saldo_adelantos']:,.2f}")

    def _registrar_adelanto(self):
        emp_id = self.combo_empleado.currentData()
        monto = Decimal(str(self.adelanto_monto.value()))
        cuotas = self.adelanto_cuotas.value()
        motivo = self.adelanto_motivo.text().strip()

        if not emp_id or monto <= 0:
            QMessageBox.warning(self, "Error", "Seleccioná empleado e ingresá un monto.")
            return

        try:
            adelanto_service.crear(emp_id, monto, cuotas, motivo)
            self.adelanto_monto.setValue(0)
            self.adelanto_motivo.clear()
            self.adelanto_cuotas.setValue(1)
            self._actualizar_info()
            self._cargar_adelantos()
            QMessageBox.information(self, "OK", f"Adelanto registrado en {cuotas} cuota(s).")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _cargar_adelantos(self):
        adelantos = adelanto_service.listar()
        self.tabla_adelantos.setRowCount(len(adelantos))
        for i, a in enumerate(adelantos):
            nombre = f"{a.empleado.apellido}, {a.empleado.nombre}" if a.empleado else "—"
            estado = "Completado" if a.completado else f"{a.cuotas_descontadas}/{a.cuotas}"
            self.tabla_adelantos.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla_adelantos.setItem(i, 1, QTableWidgetItem(a.fecha.strftime("%d/%m/%Y")))
            self.tabla_adelantos.setItem(i, 2, QTableWidgetItem(f"$ {a.monto:,.2f}"))
            self.tabla_adelantos.setItem(i, 3, QTableWidgetItem(str(a.cuotas)))
            self.tabla_adelantos.setItem(i, 4, QTableWidgetItem(f"$ {a.monto_descontado:,.2f}"))
            self.tabla_adelantos.setItem(i, 5, QTableWidgetItem(f"$ {a.saldo_pendiente:,.2f}"))
            self.tabla_adelantos.setItem(i, 6, QTableWidgetItem(estado))
