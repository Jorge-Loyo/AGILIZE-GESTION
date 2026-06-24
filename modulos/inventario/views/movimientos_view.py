from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialog, QFormLayout, QSpinBox, QLineEdit, QMessageBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.inventario import inventario_service


class MovimientosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Movimientos de Stock")
        title.setObjectName("title")
        layout.addWidget(title)

        # Botones de acciones
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        btn_entrada = QPushButton("  Entrada")
        btn_entrada.setIcon(qta.icon("fa5s.arrow-down", color="#10b981"))
        btn_entrada.setFixedHeight(32)
        btn_entrada.setCursor(Qt.PointingHandCursor)
        btn_entrada.clicked.connect(lambda: self._nuevo_movimiento("entrada"))
        toolbar.addWidget(btn_entrada)

        btn_salida = QPushButton("  Salida")
        btn_salida.setIcon(qta.icon("fa5s.arrow-up", color="#ef4444"))
        btn_salida.setFixedHeight(32)
        btn_salida.setCursor(Qt.PointingHandCursor)
        btn_salida.clicked.connect(lambda: self._nuevo_movimiento("salida"))
        toolbar.addWidget(btn_salida)

        btn_transfer = QPushButton("  Transferencia")
        btn_transfer.setIcon(qta.icon("fa5s.exchange-alt", color="#3b82f6"))
        btn_transfer.setFixedHeight(32)
        btn_transfer.setCursor(Qt.PointingHandCursor)
        btn_transfer.clicked.connect(lambda: self._nuevo_movimiento("transferencia"))
        toolbar.addWidget(btn_transfer)

        btn_ajuste = QPushButton("  Ajuste")
        btn_ajuste.setIcon(qta.icon("fa5s.balance-scale", color="#D4AF37"))
        btn_ajuste.setFixedHeight(32)
        btn_ajuste.setCursor(Qt.PointingHandCursor)
        btn_ajuste.clicked.connect(lambda: self._nuevo_movimiento("ajuste"))
        toolbar.addWidget(btn_ajuste)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Tabla de movimientos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Producto", "Deposito", "Cantidad", "Motivo", "Usuario"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla, 1)

    def _cargar(self):
        movimientos = inventario_service.listar_movimientos()
        self.tabla.setRowCount(len(movimientos))
        for i, m in enumerate(movimientos):
            self.tabla.setItem(i, 0, QTableWidgetItem(m.fecha.strftime("%d/%m/%Y") if m.fecha else ""))
            tipo_text = m.tipo.capitalize()
            self.tabla.setItem(i, 1, QTableWidgetItem(tipo_text))
            self.tabla.setItem(i, 2, QTableWidgetItem(m.producto.nombre if m.producto else ""))
            dep_text = m.deposito.nombre if m.deposito else ""
            if m.tipo == "transferencia" and m.deposito_destino:
                dep_text += f" -> {m.deposito_destino.nombre}"
            self.tabla.setItem(i, 3, QTableWidgetItem(dep_text))
            self.tabla.setItem(i, 4, QTableWidgetItem(str(m.cantidad)))
            self.tabla.setItem(i, 5, QTableWidgetItem(m.motivo or ""))
            self.tabla.setItem(i, 6, QTableWidgetItem(str(m.usuario_id or "")))

    def _nuevo_movimiento(self, tipo: str):
        dlg = MovimientoDialog(tipo, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()


class MovimientoDialog(QDialog):
    def __init__(self, tipo: str, parent=None):
        super().__init__(parent)
        self._tipo = tipo
        self.setWindowTitle(f"Nuevo Movimiento: {tipo.capitalize()}")
        self.setMinimumWidth(420)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(8)

        # Producto
        self._combo_producto = QComboBox()
        self._combo_producto.setFixedHeight(28)
        for p in inventario_service.listar_productos():
            self._combo_producto.addItem(f"{p.codigo} - {p.nombre}", p.id)
        form.addRow("Producto:", self._combo_producto)

        # Deposito origen
        self._combo_deposito = QComboBox()
        self._combo_deposito.setFixedHeight(28)
        for d in inventario_service.listar_depositos():
            self._combo_deposito.addItem(d.nombre, d.id)
        label_dep = "Deposito destino:" if self._tipo == "entrada" else "Deposito origen:" if self._tipo in ("salida", "transferencia") else "Deposito:"
        form.addRow(label_dep, self._combo_deposito)

        # Deposito destino (solo transferencia)
        if self._tipo == "transferencia":
            self._combo_destino = QComboBox()
            self._combo_destino.setFixedHeight(28)
            for d in inventario_service.listar_depositos():
                self._combo_destino.addItem(d.nombre, d.id)
            form.addRow("Deposito destino:", self._combo_destino)

        # Cantidad
        self._spin_cantidad = QSpinBox()
        self._spin_cantidad.setRange(1 if self._tipo != "ajuste" else 0, 999999)
        self._spin_cantidad.setFixedHeight(28)
        label_cant = "Nueva cantidad:" if self._tipo == "ajuste" else "Cantidad:"
        form.addRow(label_cant, self._spin_cantidad)

        # Motivo
        self._input_motivo = QLineEdit()
        self._input_motivo.setFixedHeight(28)
        self._input_motivo.setPlaceholderText("Opcional")
        form.addRow("Motivo:", self._input_motivo)

        # Referencia (solo entrada/salida)
        if self._tipo in ("entrada", "salida"):
            self._input_ref = QLineEdit()
            self._input_ref.setFixedHeight(28)
            self._input_ref.setPlaceholderText("Nro factura, remito, etc.")
            form.addRow("Referencia:", self._input_ref)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(32)
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_ok = QPushButton("Confirmar")
        btn_ok.setFixedHeight(32)
        btn_ok.clicked.connect(self._confirmar)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def _confirmar(self):
        producto_id = self._combo_producto.currentData()
        deposito_id = self._combo_deposito.currentData()
        cantidad = self._spin_cantidad.value()
        motivo = self._input_motivo.text().strip()
        referencia = getattr(self, '_input_ref', None)
        ref = referencia.text().strip() if referencia else ""

        if not producto_id or not deposito_id:
            QMessageBox.warning(self, "Error", "Selecciona producto y deposito.")
            return

        try:
            if self._tipo == "entrada":
                inventario_service.registrar_entrada(producto_id, deposito_id, cantidad, motivo, ref)
            elif self._tipo == "salida":
                inventario_service.registrar_salida(producto_id, deposito_id, cantidad, motivo, ref)
            elif self._tipo == "transferencia":
                destino_id = self._combo_destino.currentData()
                inventario_service.registrar_transferencia(producto_id, deposito_id, destino_id, cantidad, motivo)
            elif self._tipo == "ajuste":
                inventario_service.registrar_ajuste(producto_id, deposito_id, cantidad, motivo)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
