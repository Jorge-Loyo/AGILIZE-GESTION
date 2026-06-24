from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QPushButton, QLabel, QSpinBox,
    QMessageBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt
from datetime import date
from services.rrhh.sac_service import sac_service


class SACView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._empleados = []
        self._build_ui()
        self._cargar_empleados()
        self._cargar_historial()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # === Cálculo ===
        grp = QGroupBox("Calcular SAC (Aguinaldo)")
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px; margin-top: 8px; }")
        form = QGridLayout(grp)
        form.setSpacing(10)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        form.addWidget(QLabel("Empleado:"), 0, 0)
        self.combo_empleado = QComboBox()
        self.combo_empleado.setMinimumHeight(36)
        self.combo_empleado.currentIndexChanged.connect(self._on_empleado_changed)
        form.addWidget(self.combo_empleado, 0, 1)

        form.addWidget(QLabel("Año:"), 0, 2)
        self.spin_anio = QSpinBox()
        self.spin_anio.setMinimumHeight(36)
        self.spin_anio.setRange(2020, 2050)
        self.spin_anio.setValue(date.today().year)
        self.spin_anio.valueChanged.connect(self._on_empleado_changed)
        form.addWidget(self.spin_anio, 0, 3)

        form.addWidget(QLabel("Semestre:"), 1, 0)
        self.combo_semestre = QComboBox()
        self.combo_semestre.setMinimumHeight(36)
        self.combo_semestre.addItem("1° Semestre (Ene-Jun)", 1)
        self.combo_semestre.addItem("2° Semestre (Jul-Dic)", 2)
        mes_actual = date.today().month
        self.combo_semestre.setCurrentIndex(0 if mes_actual <= 6 else 1)
        self.combo_semestre.currentIndexChanged.connect(self._on_empleado_changed)
        form.addWidget(self.combo_semestre, 1, 1)

        form.addWidget(QLabel("Método:"), 1, 2)
        self.combo_metodo = QComboBox()
        self.combo_metodo.setMinimumHeight(36)
        self.combo_metodo.addItem("50% de la mayor remuneración", "mayor")
        self.combo_metodo.addItem("50% del promedio semestral", "promedio")
        form.addWidget(self.combo_metodo, 1, 3)

        layout.addWidget(grp)

        # === Detalle acumulado del semestre ===
        grp_detalle = QGroupBox("Remuneraciones del Semestre")
        grp_detalle.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px; margin-top: 8px; }")
        detalle_layout = QVBoxLayout(grp_detalle)

        self.tabla_acumulado = QTableWidget()
        self.tabla_acumulado.setColumnCount(2)
        self.tabla_acumulado.setHorizontalHeaderLabels(["Período", "Remuneración Bruta"])
        self.tabla_acumulado.horizontalHeader().setStretchLastSection(True)
        self.tabla_acumulado.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_acumulado.setAlternatingRowColors(True)
        self.tabla_acumulado.verticalHeader().setVisible(False)
        self.tabla_acumulado.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_acumulado.setMaximumHeight(180)
        detalle_layout.addWidget(self.tabla_acumulado)

        # Resultado
        resultado_layout = QHBoxLayout()
        self.lbl_resultado = QLabel("Seleccioná un empleado para ver el cálculo")
        self.lbl_resultado.setStyleSheet("font-size: 14px;")
        resultado_layout.addWidget(self.lbl_resultado)
        resultado_layout.addStretch()

        self.lbl_monto = QLabel("")
        self.lbl_monto.setStyleSheet("font-size: 18px; font-weight: bold; color: #D4AF37;")
        resultado_layout.addWidget(self.lbl_monto)
        detalle_layout.addLayout(resultado_layout)

        layout.addWidget(grp_detalle)

        # === Botones ===
        btns = QHBoxLayout()
        btns.addStretch()

        btn_calcular = QPushButton("Calcular")
        btn_calcular.setMinimumHeight(40)
        btn_calcular.setMinimumWidth(120)
        btn_calcular.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_calcular.clicked.connect(self._calcular)
        btns.addWidget(btn_calcular)

        btn_liquidar = QPushButton("Liquidar SAC")
        btn_liquidar.setMinimumHeight(40)
        btn_liquidar.setMinimumWidth(140)
        btn_liquidar.clicked.connect(self._liquidar)
        btns.addWidget(btn_liquidar)

        layout.addLayout(btns)

        # === Historial ===
        grp_hist = QGroupBox("Historial de SAC Liquidados")
        grp_hist.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px; margin-top: 8px; }")
        hist_layout = QVBoxLayout(grp_hist)

        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(5)
        self.tabla_historial.setHorizontalHeaderLabels(["Empleado", "Año", "Semestre", "Método", "Monto SAC"])
        self.tabla_historial.horizontalHeader().setStretchLastSection(True)
        self.tabla_historial.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_historial.setAlternatingRowColors(True)
        self.tabla_historial.verticalHeader().setVisible(False)
        self.tabla_historial.setEditTriggers(QTableWidget.NoEditTriggers)
        hist_layout.addWidget(self.tabla_historial)

        layout.addWidget(grp_hist)

    def _cargar_empleados(self):
        self._empleados = sac_service.listar_empleados_activos()
        self.combo_empleado.clear()
        for emp in self._empleados:
            self.combo_empleado.addItem(f"{emp.apellido}, {emp.nombre}", emp.id)

    def _on_empleado_changed(self):
        self._cargar_acumulado()

    def _cargar_acumulado(self):
        emp_id = self.combo_empleado.currentData()
        anio = self.spin_anio.value()
        semestre = self.combo_semestre.currentData()
        if not emp_id:
            return

        registros = sac_service.obtener_acumulado(emp_id, anio, semestre)
        self.tabla_acumulado.setRowCount(len(registros))
        for i, r in enumerate(registros):
            self.tabla_acumulado.setItem(i, 0, QTableWidgetItem(r.periodo))
            self.tabla_acumulado.setItem(i, 1, QTableWidgetItem(f"$ {r.remuneracion_bruta:,.2f}"))

        if registros:
            self.lbl_resultado.setText(f"{len(registros)} mes(es) registrado(s)")
        else:
            self.lbl_resultado.setText("Sin registros en este semestre")
        self.lbl_monto.setText("")

    def _calcular(self):
        emp_id = self.combo_empleado.currentData()
        anio = self.spin_anio.value()
        semestre = self.combo_semestre.currentData()
        metodo = self.combo_metodo.currentData()

        if not emp_id:
            QMessageBox.warning(self, "Error", "Seleccioná un empleado.")
            return

        resultado = sac_service.calcular_sac(emp_id, anio, semestre, metodo)

        if resultado["meses"] == 0:
            QMessageBox.information(self, "Sin datos", "No hay remuneraciones registradas para este semestre.")
            return

        metodo_txt = "Mayor remuneración" if metodo == "mayor" else "Promedio"
        self.lbl_resultado.setText(
            f"Método: {metodo_txt} | Base: $ {resultado['base']:,.2f} | Meses: {resultado['meses']}/6"
        )
        self.lbl_monto.setText(f"SAC: $ {resultado['monto_sac']:,.2f}")

    def _liquidar(self):
        emp_id = self.combo_empleado.currentData()
        anio = self.spin_anio.value()
        semestre = self.combo_semestre.currentData()
        metodo = self.combo_metodo.currentData()

        if not emp_id:
            QMessageBox.warning(self, "Error", "Seleccioná un empleado.")
            return

        resultado = sac_service.calcular_sac(emp_id, anio, semestre, metodo)
        if resultado["meses"] == 0:
            QMessageBox.warning(self, "Error", "No hay datos para liquidar.")
            return

        resp = QMessageBox.question(
            self, "Confirmar",
            f"¿Liquidar SAC por $ {resultado['monto_sac']:,.2f}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        try:
            sac_service.liquidar_sac(emp_id, anio, semestre, metodo)
            QMessageBox.information(self, "OK", "SAC liquidado correctamente.")
            self._cargar_historial()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _cargar_historial(self):
        liquidaciones = sac_service.listar_liquidaciones_sac()
        self.tabla_historial.setRowCount(len(liquidaciones))
        for i, liq in enumerate(liquidaciones):
            nombre = f"{liq.empleado.apellido}, {liq.empleado.nombre}" if liq.empleado else "—"
            metodo_txt = "Mayor rem." if liq.metodo == "mayor" else "Promedio"
            self.tabla_historial.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla_historial.setItem(i, 1, QTableWidgetItem(str(liq.anio)))
            self.tabla_historial.setItem(i, 2, QTableWidgetItem(f"{liq.semestre}°"))
            self.tabla_historial.setItem(i, 3, QTableWidgetItem(metodo_txt))
            self.tabla_historial.setItem(i, 4, QTableWidgetItem(f"$ {liq.monto_sac:,.2f}"))
