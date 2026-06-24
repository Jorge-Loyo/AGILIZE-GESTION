from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QDoubleSpinBox, QComboBox, QMessageBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.finanzas.finanzas_service import finanzas_service


class CajaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Caja Diaria")
        title.setObjectName("title")
        layout.addWidget(title)

        # Estado
        cards = QHBoxLayout()
        cards.setSpacing(12)
        self._card_estado = self._card("Estado", "Sin abrir")
        self._card_apertura = self._card("Apertura", "$ 0")
        self._card_ingresos = self._card("Ingresos", "$ 0")
        self._card_egresos = self._card("Egresos", "$ 0")
        self._card_saldo = self._card("Saldo Actual", "$ 0")
        cards.addWidget(self._card_estado)
        cards.addWidget(self._card_apertura)
        cards.addWidget(self._card_ingresos)
        cards.addWidget(self._card_egresos)
        cards.addWidget(self._card_saldo)
        layout.addLayout(cards)

        # Botones
        toolbar = QHBoxLayout()
        self._btn_abrir = QPushButton("  Abrir Caja")
        self._btn_abrir.setIcon(qta.icon("fa5s.lock-open", color="#10b981"))
        self._btn_abrir.setFixedHeight(32)
        self._btn_abrir.clicked.connect(self._abrir_caja)
        toolbar.addWidget(self._btn_abrir)

        self._btn_cerrar = QPushButton("  Cerrar Caja")
        self._btn_cerrar.setIcon(qta.icon("fa5s.lock", color="#ef4444"))
        self._btn_cerrar.setFixedHeight(32)
        self._btn_cerrar.clicked.connect(self._cerrar_caja)
        toolbar.addWidget(self._btn_cerrar)

        toolbar.addStretch()

        btn_ingreso = QPushButton("  Ingreso")
        btn_ingreso.setIcon(qta.icon("fa5s.plus", color="#10b981"))
        btn_ingreso.setFixedHeight(32)
        btn_ingreso.clicked.connect(lambda: self._mov("ingreso"))
        toolbar.addWidget(btn_ingreso)

        btn_egreso = QPushButton("  Egreso")
        btn_egreso.setIcon(qta.icon("fa5s.minus", color="#ef4444"))
        btn_egreso.setFixedHeight(32)
        btn_egreso.clicked.connect(lambda: self._mov("egreso"))
        toolbar.addWidget(btn_egreso)

        layout.addLayout(toolbar)

        # Tabla movimientos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Tipo", "Concepto", "Monto", "Referencia"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla, 1)

    def _card(self, label, value):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(120)
        card.setMinimumHeight(60)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(2)
        lay.addWidget(QLabel(label))
        val = QLabel(value)
        val.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        lay.addWidget(val)
        card._val = val
        return card

    def _cargar(self):
        resumen = finanzas_service.resumen_caja()
        if resumen:
            self._card_estado._val.setText("Abierta")
            self._card_estado._val.setStyleSheet("font-size: 14px; font-weight: bold; color: #10b981;")
            self._card_apertura._val.setText(f"$ {resumen['apertura']:,.2f}")
            self._card_ingresos._val.setText(f"$ {resumen['ingresos']:,.2f}")
            self._card_egresos._val.setText(f"$ {resumen['egresos']:,.2f}")
            self._card_saldo._val.setText(f"$ {resumen['saldo_actual']:,.2f}")
            self._btn_abrir.setEnabled(False)
            self._btn_cerrar.setEnabled(True)
            # Cargar movimientos
            caja = finanzas_service.caja_actual()
            if caja:
                from core.database import get_db
                from models.finanzas import MovimientoCaja
                with get_db() as db:
                    movs = db.query(MovimientoCaja).filter(MovimientoCaja.caja_id == caja.id).order_by(MovimientoCaja.id.desc()).all()
                    self.tabla.setRowCount(len(movs))
                    for i, m in enumerate(movs):
                        self.tabla.setItem(i, 0, QTableWidgetItem(m.tipo.capitalize()))
                        self.tabla.setItem(i, 1, QTableWidgetItem(m.concepto))
                        self.tabla.setItem(i, 2, QTableWidgetItem(f"$ {m.monto:,.2f}"))
                        self.tabla.setItem(i, 3, QTableWidgetItem(m.referencia or ""))
        else:
            self._card_estado._val.setText("Cerrada")
            self._card_estado._val.setStyleSheet("font-size: 14px; font-weight: bold; color: #ef4444;")
            self._btn_abrir.setEnabled(True)
            self._btn_cerrar.setEnabled(False)

    def _abrir_caja(self):
        from PySide6.QtWidgets import QInputDialog
        monto, ok = QInputDialog.getDouble(self, "Abrir Caja", "Monto de apertura:", 0, 0, 99999999, 2)
        if ok:
            try:
                finanzas_service.abrir_caja(monto)
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _cerrar_caja(self):
        from PySide6.QtWidgets import QInputDialog
        monto, ok = QInputDialog.getDouble(self, "Cerrar Caja", "Monto de cierre (arqueo):", 0, 0, 99999999, 2)
        if ok:
            try:
                finanzas_service.cerrar_caja(monto)
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _mov(self, tipo):
        from PySide6.QtWidgets import QInputDialog
        concepto, ok = QInputDialog.getText(self, f"{'Ingreso' if tipo == 'ingreso' else 'Egreso'}", "Concepto:")
        if not ok or not concepto:
            return
        monto, ok = QInputDialog.getDouble(self, "Monto", "Monto:", 0, 0.01, 99999999, 2)
        if ok:
            try:
                finanzas_service.registrar_movimiento_caja(tipo, concepto, monto)
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
