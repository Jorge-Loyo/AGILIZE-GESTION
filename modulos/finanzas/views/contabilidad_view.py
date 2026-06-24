from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QMessageBox,
    QSpinBox,
)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta
from services.finanzas_service import finanzas_service


class ContabilidadView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Contabilidad")
        title.setObjectName("title")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self._build_plan_cuentas(), "Plan de Cuentas")
        tabs.addTab(self._build_asientos(), "Asientos")
        layout.addWidget(tabs)

    def _build_plan_cuentas(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setSpacing(8)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        btn_nueva = QPushButton("  Nueva Cuenta")
        btn_nueva.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nueva.setFixedHeight(30)
        btn_nueva.clicked.connect(self._nueva_cuenta)
        toolbar.addWidget(btn_nueva)
        lay.addLayout(toolbar)

        self._tabla_cuentas = QTableWidget()
        self._tabla_cuentas.setColumnCount(4)
        self._tabla_cuentas.setHorizontalHeaderLabels(["Codigo", "Nombre", "Tipo", "Grupo"])
        self._tabla_cuentas.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla_cuentas.setAlternatingRowColors(True)
        self._tabla_cuentas.verticalHeader().setVisible(False)
        self._tabla_cuentas.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._tabla_cuentas)

        self._cargar_cuentas()
        return page

    def _build_asientos(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setSpacing(8)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        btn_nuevo = QPushButton("  Nuevo Asiento")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(30)
        btn_nuevo.clicked.connect(self._nuevo_asiento)
        toolbar.addWidget(btn_nuevo)
        lay.addLayout(toolbar)

        self._tabla_asientos = QTableWidget()
        self._tabla_asientos.setColumnCount(5)
        self._tabla_asientos.setHorizontalHeaderLabels(["Nro", "Fecha", "Concepto", "Tipo", "Referencia"])
        self._tabla_asientos.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._tabla_asientos.setAlternatingRowColors(True)
        self._tabla_asientos.verticalHeader().setVisible(False)
        self._tabla_asientos.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._tabla_asientos)

        self._cargar_asientos()
        return page

    def _cargar_cuentas(self):
        cuentas = finanzas_service.listar_cuentas()
        self._tabla_cuentas.setRowCount(len(cuentas))
        for i, c in enumerate(cuentas):
            self._tabla_cuentas.setItem(i, 0, QTableWidgetItem(c.codigo))
            self._tabla_cuentas.setItem(i, 1, QTableWidgetItem(("  " * c.codigo.count(".")) + c.nombre))
            self._tabla_cuentas.setItem(i, 2, QTableWidgetItem(c.tipo.capitalize()))
            self._tabla_cuentas.setItem(i, 3, QTableWidgetItem("Si" if c.es_grupo else ""))

    def _cargar_asientos(self):
        asientos = finanzas_service.listar_asientos()
        self._tabla_asientos.setRowCount(len(asientos))
        for i, a in enumerate(asientos):
            self._tabla_asientos.setItem(i, 0, QTableWidgetItem(str(a.numero)))
            self._tabla_asientos.setItem(i, 1, QTableWidgetItem(a.fecha.strftime("%d/%m/%Y") if a.fecha else ""))
            self._tabla_asientos.setItem(i, 2, QTableWidgetItem(a.concepto))
            self._tabla_asientos.setItem(i, 3, QTableWidgetItem(a.tipo))
            self._tabla_asientos.setItem(i, 4, QTableWidgetItem(a.referencia or ""))

    def _nueva_cuenta(self):
        from PySide6.QtWidgets import QInputDialog
        codigo, ok = QInputDialog.getText(self, "Nueva Cuenta", "Codigo (ej: 1.1.05):")
        if not ok or not codigo:
            return
        nombre, ok = QInputDialog.getText(self, "Nueva Cuenta", "Nombre:")
        if not ok or not nombre:
            return
        tipo, ok = QInputDialog.getItem(self, "Tipo", "Tipo de cuenta:",
            ["activo", "pasivo", "patrimonio", "ingreso", "egreso"], 0, False)
        if ok:
            try:
                finanzas_service.crear_cuenta(codigo.strip(), nombre.strip(), tipo)
                self._cargar_cuentas()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _nuevo_asiento(self):
        dlg = AsientoDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar_asientos()


class AsientoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Asiento Contable")
        self.setMinimumWidth(600)
        self._lineas = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        form = QHBoxLayout()
        form.addWidget(QLabel("Fecha:"))
        self._date = QDateEdit()
        self._date.setDate(QDate.currentDate())
        self._date.setCalendarPopup(True)
        self._date.setFixedHeight(28)
        form.addWidget(self._date)
        form.addWidget(QLabel("Concepto:"))
        self._input_concepto = QLineEdit()
        self._input_concepto.setFixedHeight(28)
        form.addWidget(self._input_concepto, 1)
        layout.addLayout(form)

        # Lineas
        layout.addWidget(QLabel("Detalle (agregar lineas):"))
        linea_form = QHBoxLayout()
        self._combo_cuenta = QComboBox()
        self._combo_cuenta.setFixedHeight(28)
        self._combo_cuenta.setMinimumWidth(200)
        for c in finanzas_service.listar_cuentas():
            if not c.es_grupo:
                self._combo_cuenta.addItem(f"{c.codigo} - {c.nombre}", c.id)
        linea_form.addWidget(self._combo_cuenta)

        linea_form.addWidget(QLabel("Debe:"))
        self._spin_debe = QDoubleSpinBox()
        self._spin_debe.setRange(0, 99999999)
        self._spin_debe.setFixedHeight(28)
        linea_form.addWidget(self._spin_debe)

        linea_form.addWidget(QLabel("Haber:"))
        self._spin_haber = QDoubleSpinBox()
        self._spin_haber.setRange(0, 99999999)
        self._spin_haber.setFixedHeight(28)
        linea_form.addWidget(self._spin_haber)

        btn_add = QPushButton("+")
        btn_add.setFixedSize(30, 28)
        btn_add.clicked.connect(self._agregar_linea)
        linea_form.addWidget(btn_add)
        layout.addLayout(linea_form)

        self._tabla = QTableWidget()
        self._tabla.setColumnCount(4)
        self._tabla.setHorizontalHeaderLabels(["Cuenta", "Debe", "Haber", ""])
        self._tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tabla.setMaximumHeight(150)
        layout.addWidget(self._tabla)

        self._lbl_totales = QLabel("Debe: 0.00 | Haber: 0.00")
        self._lbl_totales.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._lbl_totales)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(30)
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("Guardar Asiento")
        btn_guardar.setFixedHeight(30)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _agregar_linea(self):
        cuenta_id = self._combo_cuenta.currentData()
        cuenta_txt = self._combo_cuenta.currentText()
        debe = self._spin_debe.value()
        haber = self._spin_haber.value()
        if debe == 0 and haber == 0:
            return
        self._lineas.append({"cuenta_id": cuenta_id, "debe": debe, "haber": haber, "cuenta_txt": cuenta_txt})
        self._spin_debe.setValue(0)
        self._spin_haber.setValue(0)
        self._actualizar_tabla()

    def _actualizar_tabla(self):
        self._tabla.setRowCount(len(self._lineas))
        total_d, total_h = 0, 0
        for i, l in enumerate(self._lineas):
            self._tabla.setItem(i, 0, QTableWidgetItem(l["cuenta_txt"]))
            self._tabla.setItem(i, 1, QTableWidgetItem(f"{l['debe']:,.2f}"))
            self._tabla.setItem(i, 2, QTableWidgetItem(f"{l['haber']:,.2f}"))
            total_d += l["debe"]
            total_h += l["haber"]
        color = "#10b981" if abs(total_d - total_h) < 0.01 else "#ef4444"
        self._lbl_totales.setText(f"Debe: {total_d:,.2f} | Haber: {total_h:,.2f}")
        self._lbl_totales.setStyleSheet(f"font-weight: bold; color: {color};")

    def _guardar(self):
        concepto = self._input_concepto.text().strip()
        if not concepto:
            QMessageBox.warning(self, "Error", "El concepto es obligatorio.")
            return
        if not self._lineas:
            QMessageBox.warning(self, "Error", "Agrega al menos una linea.")
            return
        fecha = self._date.date().toPython()
        try:
            finanzas_service.crear_asiento(fecha, concepto, self._lineas)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
