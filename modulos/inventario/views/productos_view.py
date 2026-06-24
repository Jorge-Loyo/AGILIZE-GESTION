from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox,
    QMessageBox, QTextEdit,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.inventario import inventario_service


class ProductosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Productos")
        title.setObjectName("title")
        layout.addWidget(title)

        # Toolbar
        toolbar = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar por nombre o codigo...")
        self._search.setFixedHeight(32)
        self._search.textChanged.connect(self._buscar)
        toolbar.addWidget(self._search)

        btn_nuevo = QPushButton("  Nuevo Producto")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(32)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self._nuevo)
        toolbar.addWidget(btn_nuevo)

        btn_cat = QPushButton("  Categorias")
        btn_cat.setIcon(qta.icon("fa5s.tags", color="#F8F9FA"))
        btn_cat.setFixedHeight(32)
        btn_cat.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; }")
        btn_cat.setCursor(Qt.PointingHandCursor)
        btn_cat.clicked.connect(self._gestionar_categorias)
        toolbar.addWidget(btn_cat)

        layout.addLayout(toolbar)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Codigo", "Nombre", "Categoria", "P. Costo", "P. Venta", "Stock Total", "Estado"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.doubleClicked.connect(self._editar_seleccionado)
        layout.addWidget(self.tabla, 1)

    def _cargar(self):
        productos = inventario_service.listar_productos()
        self.tabla.setRowCount(len(productos))
        for i, p in enumerate(productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.nombre))
            self.tabla.setItem(i, 2, QTableWidgetItem(p.categoria.nombre if p.categoria else ""))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"{p.precio_costo:,.2f}"))
            self.tabla.setItem(i, 4, QTableWidgetItem(f"{p.precio_venta:,.2f}"))
            self.tabla.setItem(i, 5, QTableWidgetItem(str(p.stock_total)))
            self.tabla.setItem(i, 6, QTableWidgetItem("Activo" if p.activo else "Inactivo"))

    def _buscar(self, texto):
        if not texto:
            self._cargar()
            return
        productos = inventario_service.buscar_productos(texto)
        self.tabla.setRowCount(len(productos))
        for i, p in enumerate(productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.nombre))
            self.tabla.setItem(i, 2, QTableWidgetItem(p.categoria.nombre if p.categoria else ""))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"{p.precio_costo:,.2f}"))
            self.tabla.setItem(i, 4, QTableWidgetItem(f"{p.precio_venta:,.2f}"))
            self.tabla.setItem(i, 5, QTableWidgetItem(str(p.stock_total)))
            self.tabla.setItem(i, 6, QTableWidgetItem("Activo" if p.activo else "Inactivo"))

    def _nuevo(self):
        dlg = ProductoDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()

    def _editar_seleccionado(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
        codigo = self.tabla.item(row, 0).text()
        productos = inventario_service.buscar_productos(codigo)
        if productos:
            dlg = ProductoDialog(producto=productos[0], parent=self)
            if dlg.exec() == QDialog.Accepted:
                self._cargar()

    def _gestionar_categorias(self):
        from PySide6.QtWidgets import QInputDialog
        nombre, ok = QInputDialog.getText(self, "Nueva Categoria", "Nombre:")
        if ok and nombre.strip():
            try:
                inventario_service.crear_categoria(nombre.strip())
                QMessageBox.information(self, "OK", f"Categoria '{nombre}' creada.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


class ProductoDialog(QDialog):
    def __init__(self, producto=None, parent=None):
        super().__init__(parent)
        self._producto = producto
        self.setWindowTitle("Editar Producto" if producto else "Nuevo Producto")
        self.setMinimumWidth(450)
        self._build_ui()
        if producto:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        form = QFormLayout()
        form.setSpacing(8)

        self._input_codigo = QLineEdit()
        self._input_codigo.setFixedHeight(28)
        form.addRow("Codigo:", self._input_codigo)

        self._input_nombre = QLineEdit()
        self._input_nombre.setFixedHeight(28)
        form.addRow("Nombre:", self._input_nombre)

        self._input_desc = QTextEdit()
        self._input_desc.setMaximumHeight(60)
        form.addRow("Descripcion:", self._input_desc)

        self._combo_cat = QComboBox()
        self._combo_cat.setFixedHeight(28)
        self._combo_cat.addItem("Sin categoria", None)
        for cat in inventario_service.listar_categorias():
            self._combo_cat.addItem(cat.nombre, cat.id)
        form.addRow("Categoria:", self._combo_cat)

        self._input_unidad = QLineEdit()
        self._input_unidad.setFixedHeight(28)
        self._input_unidad.setText("unidad")
        form.addRow("Unidad medida:", self._input_unidad)

        self._input_costo = QDoubleSpinBox()
        self._input_costo.setRange(0, 99999999)
        self._input_costo.setDecimals(2)
        self._input_costo.setFixedHeight(28)
        form.addRow("Precio costo:", self._input_costo)

        self._input_venta = QDoubleSpinBox()
        self._input_venta.setRange(0, 99999999)
        self._input_venta.setDecimals(2)
        self._input_venta.setFixedHeight(28)
        form.addRow("Precio venta:", self._input_venta)

        self._input_minimo = QSpinBox()
        self._input_minimo.setRange(0, 99999)
        self._input_minimo.setFixedHeight(28)
        form.addRow("Stock minimo:", self._input_minimo)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(32)
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setFixedHeight(32)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _cargar_datos(self):
        p = self._producto
        self._input_codigo.setText(p.codigo)
        self._input_nombre.setText(p.nombre)
        self._input_desc.setPlainText(p.descripcion)
        self._input_unidad.setText(p.unidad_medida)
        self._input_costo.setValue(p.precio_costo)
        self._input_venta.setValue(p.precio_venta)
        self._input_minimo.setValue(p.stock_minimo)
        if p.categoria_id:
            idx = self._combo_cat.findData(p.categoria_id)
            if idx >= 0:
                self._combo_cat.setCurrentIndex(idx)

    def _guardar(self):
        codigo = self._input_codigo.text().strip()
        nombre = self._input_nombre.text().strip()
        if not codigo or not nombre:
            QMessageBox.warning(self, "Error", "Codigo y nombre son obligatorios.")
            return

        datos = {
            "codigo": codigo,
            "nombre": nombre,
            "descripcion": self._input_desc.toPlainText().strip(),
            "categoria_id": self._combo_cat.currentData(),
            "unidad_medida": self._input_unidad.text().strip(),
            "precio_costo": self._input_costo.value(),
            "precio_venta": self._input_venta.value(),
            "stock_minimo": self._input_minimo.value(),
        }

        try:
            if self._producto:
                inventario_service.actualizar_producto(self._producto.id, datos)
            else:
                inventario_service.crear_producto(datos)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
