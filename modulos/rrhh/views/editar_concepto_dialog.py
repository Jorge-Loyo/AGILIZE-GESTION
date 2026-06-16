from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QDoubleSpinBox,
    QMessageBox, QCheckBox,
)
from PySide6.QtCore import Qt, Signal
from decimal import Decimal
from core.database import get_db
from models.nomina import ConceptoNomina


class EditarConceptoDialog(QDialog):
    concepto_actualizado = Signal()

    def __init__(self, concepto_id: int, parent=None):
        super().__init__(parent)
        self._concepto_id = concepto_id
        self.setWindowTitle("Editar Concepto")
        self.setFixedSize(450, 320)
        self.setModal(True)
        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Editar Concepto de Nomina")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        form = QGridLayout()
        form.setSpacing(10)
        form.setColumnStretch(1, 1)

        form.addWidget(QLabel("Codigo:"), 0, 0)
        self.input_codigo = QLineEdit()
        self.input_codigo.setMinimumHeight(32)
        form.addWidget(self.input_codigo, 0, 1)

        form.addWidget(QLabel("Nombre:"), 1, 0)
        self.input_nombre = QLineEdit()
        self.input_nombre.setMinimumHeight(32)
        form.addWidget(self.input_nombre, 1, 1)

        form.addWidget(QLabel("Tipo:"), 2, 0)
        self.combo_tipo = QComboBox()
        self.combo_tipo.setMinimumHeight(32)
        self.combo_tipo.addItems(["haber", "deduccion"])
        form.addWidget(self.combo_tipo, 2, 1)

        form.addWidget(QLabel("Calculo:"), 3, 0)
        self.combo_calculo = QComboBox()
        self.combo_calculo.setMinimumHeight(32)
        self.combo_calculo.addItem("Porcentaje sobre bruto", "porcentaje")
        self.combo_calculo.addItem("Monto fijo", "fijo")
        self.combo_calculo.addItem("Monto por dia trabajado", "por_dia")
        self.combo_calculo.currentIndexChanged.connect(self._on_calculo_changed)
        form.addWidget(self.combo_calculo, 3, 1)

        self.lbl_valor = QLabel("Valor:")
        form.addWidget(self.lbl_valor, 4, 0)
        self.input_valor = QDoubleSpinBox()
        self.input_valor.setMinimumHeight(32)
        self.input_valor.setRange(0, 9999999)
        self.input_valor.setDecimals(2)
        form.addWidget(self.input_valor, 4, 1)

        self.chk_activo = QCheckBox("Activo")
        self.chk_activo.setChecked(True)
        form.addWidget(self.chk_activo, 5, 1)

        layout.addLayout(form)

        # Botones
        from PySide6.QtWidgets import QHBoxLayout
        btns = QHBoxLayout()
        btns.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(38)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setMinimumHeight(38)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)

        layout.addLayout(btns)

    def _on_calculo_changed(self):
        calculo = self.combo_calculo.currentData()
        self.input_valor.setPrefix("")
        self.input_valor.setSuffix("")
        if calculo == "porcentaje":
            self.lbl_valor.setText("Porcentaje:")
            self.input_valor.setSuffix(" %")
            self.input_valor.setRange(0, 100)
        elif calculo == "fijo":
            self.lbl_valor.setText("Monto fijo:")
            self.input_valor.setPrefix("$ ")
            self.input_valor.setRange(0, 9999999)
        elif calculo == "por_dia":
            self.lbl_valor.setText("Monto/dia:")
            self.input_valor.setPrefix("$ ")
            self.input_valor.setRange(0, 9999999)

    def _cargar_datos(self):
        with get_db() as db:
            c = db.get(ConceptoNomina, self._concepto_id)
            if not c:
                return
            self.input_codigo.setText(c.codigo)
            self.input_nombre.setText(c.nombre)
            idx_tipo = self.combo_tipo.findText(c.tipo)
            if idx_tipo >= 0:
                self.combo_tipo.setCurrentIndex(idx_tipo)
            calculo = getattr(c, 'calculo', None) or 'porcentaje'
            idx_calc = self.combo_calculo.findData(calculo)
            if idx_calc >= 0:
                self.combo_calculo.setCurrentIndex(idx_calc)
            if c.porcentaje:
                self.input_valor.setValue(float(c.porcentaje))
            elif c.monto_fijo:
                self.input_valor.setValue(float(c.monto_fijo))
            self.chk_activo.setChecked(c.activo)

    def _guardar(self):
        codigo = self.input_codigo.text().strip().upper()
        nombre = self.input_nombre.text().strip()
        tipo = self.combo_tipo.currentText()
        calculo = self.combo_calculo.currentData()
        valor = self.input_valor.value()
        activo = self.chk_activo.isChecked()

        if not codigo or not nombre:
            QMessageBox.warning(self, "Error", "Codigo y Nombre son obligatorios.")
            return
        if valor == 0:
            QMessageBox.warning(self, "Error", "Ingresa un valor.")
            return

        with get_db() as db:
            c = db.get(ConceptoNomina, self._concepto_id)
            if not c:
                QMessageBox.critical(self, "Error", "Concepto no encontrado.")
                return
            c.codigo = codigo
            c.nombre = nombre
            c.tipo = tipo
            c.calculo = calculo
            c.porcentaje = Decimal(str(valor)) if calculo == "porcentaje" else None
            c.monto_fijo = Decimal(str(valor)) if calculo in ("fijo", "por_dia") else None
            c.activo = activo

        self.concepto_actualizado.emit()
        self.accept()
