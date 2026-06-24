from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QMessageBox,
    QCheckBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.finanzas_service import finanzas_service


class BancosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar_cuentas()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Bancos")
        title.setObjectName("title")
        layout.addWidget(title)

        # Selector de cuenta + saldo
        sel = QHBoxLayout()
        sel.addWidget(QLabel("Cuenta:"))
        self._combo_cuenta = QComboBox()
        self._combo_cuenta.setFixedHeight(30)
        self._combo_cuenta.setMinimumWidth(300)
        self._combo_cuenta.currentIndexChanged.connect(self._on_cuenta_change)
        sel.addWidget(self._combo_cuenta)
        sel.addStretch()

        btn_nueva = QPushButton("  Nueva Cuenta")
        btn_nueva.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nueva.setFixedHeight(30)
        btn_nueva.clicked.connect(self._nueva_cuenta)
        sel.addWidget(btn_nueva)
        layout.addLayout(sel)

        self._lbl_saldo = QLabel("Saldo: $ 0.00")
        self._lbl_saldo.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(self._lbl_saldo)

        # Botones
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        btn_dep = QPushButton("  Deposito")
        btn_dep.setIcon(qta.icon("fa5s.plus", color="#10b981"))
        btn_dep.setFixedHeight(30)
        btn_dep.clicked.connect(lambda: self._mov("deposito"))
        toolbar.addWidget(btn_dep)

        btn_ret = QPushButton("  Retiro")
        btn_ret.setIcon(qta.icon("fa5s.minus", color="#ef4444"))
        btn_ret.setFixedHeight(30)
        btn_ret.clicked.connect(lambda: self._mov("retiro"))
        toolbar.addWidget(btn_ret)

        btn_transf = QPushButton("  Transferencia")
        btn_transf.setIcon(qta.icon("fa5s.exchange-alt", color="#3b82f6"))
        btn_transf.setFixedHeight(30)
        btn_transf.clicked.connect(lambda: self._mov("transferencia"))
        toolbar.addWidget(btn_transf)

        toolbar.addStretch()

        btn_conciliar = QPushButton("  Conciliar seleccionado")
        btn_conciliar.setFixedHeight(30)
        btn_conciliar.clicked.connect(self._conciliar)
        toolbar.addWidget(btn_conciliar)

        layout.addLayout(toolbar)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Tipo", "Concepto", "Monto", "Saldo", "Conciliado"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabla, 1)

    def _cargar_cuentas(self):
        self._combo_cuenta.clear()
        cuentas = finanzas_service.listar_cuentas_bancarias()
        for c in cuentas:
            self._combo_cuenta.addItem(f"{c.banco} - {c.numero} ({c.tipo_cuenta})", c.id)

    def _on_cuenta_change(self):
        cuenta_id = self._combo_cuenta.currentData()
        if not cuenta_id:
            return
        cuentas = finanzas_service.listar_cuentas_bancarias()
        cuenta = next((c for c in cuentas if c.id == cuenta_id), None)
        if cuenta:
            self._lbl_saldo.setText(f"Saldo: $ {cuenta.saldo:,.2f}")
        self._cargar_movimientos()

    def _cargar_movimientos(self):
        cuenta_id = self._combo_cuenta.currentData()
        if not cuenta_id:
            return
        movs = finanzas_service.listar_movimientos_banco(cuenta_id)
        self.tabla.setRowCount(len(movs))
        for i, m in enumerate(movs):
            self.tabla.setItem(i, 0, QTableWidgetItem(m.fecha.strftime("%d/%m/%Y") if m.fecha else ""))
            self.tabla.setItem(i, 1, QTableWidgetItem(m.tipo.capitalize()))
            self.tabla.setItem(i, 2, QTableWidgetItem(m.concepto))
            monto_item = QTableWidgetItem(f"$ {m.monto:,.2f}")
            monto_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 3, monto_item)
            saldo_item = QTableWidgetItem(f"$ {m.saldo:,.2f}")
            saldo_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 4, saldo_item)
            self.tabla.setItem(i, 5, QTableWidgetItem("Si" if m.conciliado else ""))

    def _nueva_cuenta(self):
        dlg = CuentaBancariaDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar_cuentas()

    def _mov(self, tipo):
        cuenta_id = self._combo_cuenta.currentData()
        if not cuenta_id:
            QMessageBox.warning(self, "Error", "Selecciona una cuenta.")
            return
        from PySide6.QtWidgets import QInputDialog
        concepto, ok = QInputDialog.getText(self, tipo.capitalize(), "Concepto:")
        if not ok or not concepto:
            return
        monto, ok = QInputDialog.getDouble(self, "Monto", "Monto:", 0, 0.01, 99999999, 2)
        if ok:
            try:
                finanzas_service.registrar_movimiento_banco(cuenta_id, tipo, concepto, monto)
                self._on_cuenta_change()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _conciliar(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Selecciona un movimiento.")
            return
        cuenta_id = self._combo_cuenta.currentData()
        movs = finanzas_service.listar_movimientos_banco(cuenta_id)
        if row < len(movs):
            finanzas_service.conciliar_movimiento(movs[row].id)
            self._cargar_movimientos()


class CuentaBancariaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Cuenta Bancaria")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(8)

        self._input_banco = QLineEdit()
        self._input_banco.setFixedHeight(28)
        form.addRow("Banco:", self._input_banco)

        self._combo_tipo = QComboBox()
        self._combo_tipo.addItems(["Corriente", "Ahorro"])
        self._combo_tipo.setFixedHeight(28)
        form.addRow("Tipo:", self._combo_tipo)

        self._input_numero = QLineEdit()
        self._input_numero.setFixedHeight(28)
        form.addRow("Numero:", self._input_numero)

        self._input_moneda = QLineEdit()
        self._input_moneda.setFixedHeight(28)
        self._input_moneda.setText("Bs.")
        form.addRow("Moneda:", self._input_moneda)

        self._input_saldo = QDoubleSpinBox()
        self._input_saldo.setRange(0, 99999999)
        self._input_saldo.setFixedHeight(28)
        form.addRow("Saldo inicial:", self._input_saldo)

        layout.addLayout(form)
        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(30)
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setFixedHeight(30)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _guardar(self):
        banco = self._input_banco.text().strip()
        if not banco:
            QMessageBox.warning(self, "Error", "El banco es obligatorio.")
            return
        try:
            finanzas_service.crear_cuenta_bancaria(
                banco, self._combo_tipo.currentText().lower(),
                self._input_numero.text().strip(),
                self._input_moneda.text().strip(),
                self._input_saldo.value()
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
