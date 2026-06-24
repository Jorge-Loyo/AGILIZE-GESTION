from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QMessageBox,
    QDateEdit, QSpinBox, QTextEdit,
)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta
from services.finanzas.finanzas_service import finanzas_service
from services.core.empresa_service import empresa_service


class FacturacionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Facturacion")
        title.setObjectName("title")
        header.addWidget(title)

        lbl_pais = QLabel(f"Pais: {self._pais}")
        lbl_pais.setStyleSheet("font-size: 11px; color: #D4AF37; font-weight: bold;")
        header.addWidget(lbl_pais)
        header.addStretch()

        btn_nueva = QPushButton("  Nueva Factura")
        btn_nueva.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nueva.setFixedHeight(32)
        btn_nueva.setCursor(Qt.PointingHandCursor)
        btn_nueva.clicked.connect(self._nueva_factura)
        header.addWidget(btn_nueva)
        layout.addLayout(header)

        # Info impositiva
        if self._pais == "Venezuela":
            info = "IVA 16% | Factura Fiscal | Nota de Credito | Nota de Debito"
        else:
            info = "IVA 21% | Factura A/B/C | Nota de Credito | Nota de Debito"
        lbl_info = QLabel(info)
        lbl_info.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(lbl_info)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Tipo", "Numero", "Fecha", "Cliente/Proveedor", "Subtotal", "IVA", "Total"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla, 1)

    def _cargar(self):
        facturas = finanzas_service.listar_facturas()
        self.tabla.setRowCount(len(facturas))
        for i, f in enumerate(facturas):
            tipo_txt = f.tipo_comprobante.replace("_", " ").capitalize()
            if f.letra:
                tipo_txt += f" {f.letra}"
            self.tabla.setItem(i, 0, QTableWidgetItem(tipo_txt))
            self.tabla.setItem(i, 1, QTableWidgetItem(f"{f.punto_venta:04d}-{f.numero:08d}"))
            self.tabla.setItem(i, 2, QTableWidgetItem(f.fecha.strftime("%d/%m/%Y") if f.fecha else ""))
            self.tabla.setItem(i, 3, QTableWidgetItem(f.entidad_nombre))
            self.tabla.setItem(i, 4, QTableWidgetItem(f"$ {f.subtotal:,.2f}"))
            self.tabla.setItem(i, 5, QTableWidgetItem(f"$ {f.impuesto_monto:,.2f}"))
            self.tabla.setItem(i, 6, QTableWidgetItem(f"$ {f.total:,.2f}"))

    def _nueva_factura(self):
        dlg = FacturaDialog(self._pais, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()


class FacturaDialog(QDialog):
    def __init__(self, pais: str, parent=None):
        super().__init__(parent)
        self._pais = pais
        self._items = []
        self.setWindowTitle("Nueva Factura")
        self.setMinimumWidth(600)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        form = QHBoxLayout()
        form.setSpacing(10)

        # Tipo comprobante
        form.addWidget(QLabel("Tipo:"))
        self._combo_tipo = QComboBox()
        self._combo_tipo.setFixedHeight(28)
        self._combo_tipo.addItems(["Factura", "Nota de Credito", "Nota de Debito"])
        form.addWidget(self._combo_tipo)

        # Letra (solo Argentina)
        if self._pais == "Argentina":
            form.addWidget(QLabel("Letra:"))
            self._combo_letra = QComboBox()
            self._combo_letra.setFixedHeight(28)
            self._combo_letra.addItems(["A", "B", "C"])
            form.addWidget(self._combo_letra)
        else:
            self._combo_letra = None

        form.addWidget(QLabel("Fecha:"))
        self._date = QDateEdit()
        self._date.setDate(QDate.currentDate())
        self._date.setCalendarPopup(True)
        self._date.setFixedHeight(28)
        form.addWidget(self._date)
        layout.addLayout(form)

        # Cliente
        cli_form = QHBoxLayout()
        cli_form.addWidget(QLabel("Cliente/Prov:"))
        self._input_nombre = QLineEdit()
        self._input_nombre.setFixedHeight(28)
        self._input_nombre.setPlaceholderText("Nombre o razon social")
        cli_form.addWidget(self._input_nombre, 1)
        cli_form.addWidget(QLabel("Doc:"))
        self._input_doc = QLineEdit()
        self._input_doc.setFixedHeight(28)
        self._input_doc.setFixedWidth(120)
        cli_form.addWidget(self._input_doc)
        layout.addLayout(cli_form)

        # Items
        layout.addWidget(QLabel("Items:"))
        item_form = QHBoxLayout()
        self._input_item_desc = QLineEdit()
        self._input_item_desc.setFixedHeight(26)
        self._input_item_desc.setPlaceholderText("Descripcion")
        item_form.addWidget(self._input_item_desc, 1)
        item_form.addWidget(QLabel("Cant:"))
        self._spin_cant = QDoubleSpinBox()
        self._spin_cant.setRange(0.01, 99999)
        self._spin_cant.setValue(1)
        self._spin_cant.setFixedHeight(26)
        self._spin_cant.setFixedWidth(60)
        item_form.addWidget(self._spin_cant)
        item_form.addWidget(QLabel("Precio:"))
        self._spin_precio = QDoubleSpinBox()
        self._spin_precio.setRange(0, 99999999)
        self._spin_precio.setFixedHeight(26)
        self._spin_precio.setFixedWidth(100)
        item_form.addWidget(self._spin_precio)
        btn_add = QPushButton("+")
        btn_add.setFixedSize(28, 26)
        btn_add.clicked.connect(self._agregar_item)
        item_form.addWidget(btn_add)
        layout.addLayout(item_form)

        self._tabla_items = QTableWidget()
        self._tabla_items.setColumnCount(4)
        self._tabla_items.setHorizontalHeaderLabels(["Descripcion", "Cant", "Precio", "Subtotal"])
        self._tabla_items.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tabla_items.setMaximumHeight(120)
        layout.addWidget(self._tabla_items)

        # Totales
        iva_pct = 16 if self._pais == "Venezuela" else 21
        self._lbl_totales = QLabel(f"Subtotal: $ 0.00 | IVA ({iva_pct}%): $ 0.00 | Total: $ 0.00")
        self._lbl_totales.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self._lbl_totales)

        # Botones
        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(30)
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("Emitir Factura")
        btn_guardar.setFixedHeight(30)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _agregar_item(self):
        desc = self._input_item_desc.text().strip()
        if not desc:
            return
        cant = self._spin_cant.value()
        precio = self._spin_precio.value()
        self._items.append({"descripcion": desc, "cantidad": cant, "precio_unitario": precio})
        self._input_item_desc.clear()
        self._spin_cant.setValue(1)
        self._spin_precio.setValue(0)
        self._actualizar_items()

    def _actualizar_items(self):
        self._tabla_items.setRowCount(len(self._items))
        subtotal = 0
        for i, item in enumerate(self._items):
            st = item["cantidad"] * item["precio_unitario"]
            subtotal += st
            self._tabla_items.setItem(i, 0, QTableWidgetItem(item["descripcion"]))
            self._tabla_items.setItem(i, 1, QTableWidgetItem(f"{item['cantidad']:.2f}"))
            self._tabla_items.setItem(i, 2, QTableWidgetItem(f"$ {item['precio_unitario']:,.2f}"))
            self._tabla_items.setItem(i, 3, QTableWidgetItem(f"$ {st:,.2f}"))
        iva_pct = 16 if self._pais == "Venezuela" else 21
        iva = subtotal * iva_pct / 100
        total = subtotal + iva
        self._lbl_totales.setText(f"Subtotal: $ {subtotal:,.2f} | IVA ({iva_pct}%): $ {iva:,.2f} | Total: $ {total:,.2f}")

    def _guardar(self):
        if not self._items:
            QMessageBox.warning(self, "Error", "Agrega al menos un item.")
            return
        nombre = self._input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre del cliente/proveedor es obligatorio.")
            return

        tipos_map = {"Factura": "factura", "Nota de Credito": "nota_credito", "Nota de Debito": "nota_debito"}
        iva_pct = 16 if self._pais == "Venezuela" else 21

        datos = {
            "tipo_comprobante": tipos_map[self._combo_tipo.currentText()],
            "letra": self._combo_letra.currentText() if self._combo_letra else "",
            "fecha": self._date.date().toPython(),
            "tipo_entidad": "cliente",
            "entidad_nombre": nombre,
            "entidad_documento": self._input_doc.text().strip(),
            "impuesto_porcentaje": iva_pct,
        }

        try:
            finanzas_service.crear_factura(datos, self._items)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
