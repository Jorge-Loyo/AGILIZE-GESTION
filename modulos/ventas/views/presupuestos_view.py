from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox, QMessageBox,
    QDateEdit, QTextEdit,
)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta
from services.ventas_service import ventas_service


class PresupuestosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Presupuestos")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        btn_nuevo = QPushButton("  Nuevo Presupuesto")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(32)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self._nuevo)
        header.addWidget(btn_nuevo)
        layout.addLayout(header)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Nro", "Fecha", "Cliente", "Total", "Validez", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabla, 1)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_aprobar = QPushButton("  Aprobar")
        btn_aprobar.setIcon(qta.icon("fa5s.check", color="#10b981"))
        btn_aprobar.setFixedHeight(30)
        btn_aprobar.clicked.connect(self._aprobar)
        btns.addWidget(btn_aprobar)
        btn_rechazar = QPushButton("  Rechazar")
        btn_rechazar.setIcon(qta.icon("fa5s.times", color="#ef4444"))
        btn_rechazar.setFixedHeight(30)
        btn_rechazar.clicked.connect(self._rechazar)
        btns.addWidget(btn_rechazar)
        layout.addLayout(btns)

    def _cargar(self):
        presupuestos = ventas_service.listar_presupuestos()
        self.tabla.setRowCount(len(presupuestos))
        for i, p in enumerate(presupuestos):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(p.numero)))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.fecha.strftime("%d/%m/%Y") if p.fecha else ""))
            self.tabla.setItem(i, 2, QTableWidgetItem(p.cliente_nombre))
            t = QTableWidgetItem(f"$ {p.total:,.2f}")
            t.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 3, t)
            self.tabla.setItem(i, 4, QTableWidgetItem(f"{p.validez_dias} dias"))
            self.tabla.setItem(i, 5, QTableWidgetItem(p.estado.capitalize()))

    def _nuevo(self):
        dlg = DocumentoComercialDialog("Presupuesto", parent=self)
        if dlg.exec() == QDialog.Accepted:
            datos = dlg.datos()
            try:
                ventas_service.crear_presupuesto(datos["nombre"], datos["items"], validez_dias=datos.get("validez", 15))
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _aprobar(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
        presupuestos = ventas_service.listar_presupuestos()
        if row < len(presupuestos):
            ventas_service.aprobar_presupuesto(presupuestos[row].id)
            self._cargar()

    def _rechazar(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
        presupuestos = ventas_service.listar_presupuestos()
        if row < len(presupuestos):
            ventas_service.rechazar_presupuesto(presupuestos[row].id)
            self._cargar()


class PedidosVentaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Pedidos de Venta")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        btn_nuevo = QPushButton("  Nuevo Pedido")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(32)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self._nuevo)
        header.addWidget(btn_nuevo)
        layout.addLayout(header)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Nro", "Fecha", "Cliente", "Total", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabla, 1)

    def _cargar(self):
        pedidos = ventas_service.listar_pedidos()
        self.tabla.setRowCount(len(pedidos))
        for i, p in enumerate(pedidos):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(p.numero)))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.fecha.strftime("%d/%m/%Y") if p.fecha else ""))
            self.tabla.setItem(i, 2, QTableWidgetItem(p.cliente_nombre))
            t = QTableWidgetItem(f"$ {p.total:,.2f}")
            t.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 3, t)
            self.tabla.setItem(i, 4, QTableWidgetItem(p.estado.replace("_", " ").capitalize()))

    def _nuevo(self):
        dlg = DocumentoComercialDialog("Pedido de Venta", parent=self)
        if dlg.exec() == QDialog.Accepted:
            datos = dlg.datos()
            try:
                ventas_service.crear_pedido(datos["nombre"], datos["items"])
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


class DocumentoComercialDialog(QDialog):
    """Dialog reutilizable para crear presupuestos, pedidos y ordenes de compra."""
    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Nuevo {titulo}")
        self.setMinimumWidth(550)
        self._items = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        form = QHBoxLayout()
        form.addWidget(QLabel("Cliente/Prov:"))
        self._input_nombre = QLineEdit()
        self._input_nombre.setFixedHeight(28)
        form.addWidget(self._input_nombre, 1)
        form.addWidget(QLabel("Validez:"))
        self._spin_validez = QSpinBox()
        self._spin_validez.setRange(1, 365)
        self._spin_validez.setValue(15)
        self._spin_validez.setFixedHeight(28)
        self._spin_validez.setFixedWidth(60)
        self._spin_validez.setSuffix(" dias")
        form.addWidget(self._spin_validez)
        layout.addLayout(form)

        # Items
        layout.addWidget(QLabel("Items:"))
        item_row = QHBoxLayout()
        self._input_desc = QLineEdit()
        self._input_desc.setFixedHeight(26)
        self._input_desc.setPlaceholderText("Descripcion")
        item_row.addWidget(self._input_desc, 1)
        self._spin_cant = QDoubleSpinBox()
        self._spin_cant.setRange(0.01, 99999)
        self._spin_cant.setValue(1)
        self._spin_cant.setFixedHeight(26)
        self._spin_cant.setFixedWidth(60)
        item_row.addWidget(self._spin_cant)
        self._spin_precio = QDoubleSpinBox()
        self._spin_precio.setRange(0, 99999999)
        self._spin_precio.setFixedHeight(26)
        self._spin_precio.setFixedWidth(100)
        self._spin_precio.setPrefix("$ ")
        item_row.addWidget(self._spin_precio)
        btn_add = QPushButton("+")
        btn_add.setFixedSize(26, 26)
        btn_add.clicked.connect(self._add_item)
        item_row.addWidget(btn_add)
        layout.addLayout(item_row)

        self._tabla = QTableWidget()
        self._tabla.setColumnCount(4)
        self._tabla.setHorizontalHeaderLabels(["Descripcion", "Cant", "Precio", "Subtotal"])
        self._tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tabla.setMaximumHeight(120)
        layout.addWidget(self._tabla)

        self._lbl_total = QLabel("Total: $ 0.00")
        self._lbl_total.setStyleSheet("font-weight: bold; font-size: 13px; color: #D4AF37;")
        layout.addWidget(self._lbl_total)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(30)
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_ok = QPushButton("Confirmar")
        btn_ok.setFixedHeight(30)
        btn_ok.clicked.connect(self._confirmar)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def _add_item(self):
        desc = self._input_desc.text().strip()
        if not desc:
            return
        self._items.append({
            "descripcion": desc,
            "cantidad": self._spin_cant.value(),
            "precio_unitario": self._spin_precio.value(),
        })
        self._input_desc.clear()
        self._spin_cant.setValue(1)
        self._spin_precio.setValue(0)
        self._refresh()

    def _refresh(self):
        self._tabla.setRowCount(len(self._items))
        total = 0
        for i, item in enumerate(self._items):
            st = item["cantidad"] * item["precio_unitario"]
            total += st
            self._tabla.setItem(i, 0, QTableWidgetItem(item["descripcion"]))
            self._tabla.setItem(i, 1, QTableWidgetItem(f"{item['cantidad']:.2f}"))
            self._tabla.setItem(i, 2, QTableWidgetItem(f"$ {item['precio_unitario']:,.2f}"))
            self._tabla.setItem(i, 3, QTableWidgetItem(f"$ {st:,.2f}"))
        self._lbl_total.setText(f"Total: $ {total:,.2f}")

    def _confirmar(self):
        if not self._input_nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return
        if not self._items:
            QMessageBox.warning(self, "Error", "Agrega al menos un item.")
            return
        self.accept()

    def datos(self) -> dict:
        return {
            "nombre": self._input_nombre.text().strip(),
            "items": self._items,
            "validez": self._spin_validez.value(),
        }
