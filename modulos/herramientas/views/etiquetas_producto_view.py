"""
Etiquetas de Producto - Genera etiquetas con codigo de barras
para pegar en los productos.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox,
    QFileDialog, QMessageBox, QGroupBox, QLineEdit, QComboBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta


class EtiquetasProductoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Etiquetas de Producto (Codigo de Barras)")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Genera etiquetas con codigo de barras para pegar directamente en los productos.")
        subtitle.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(subtitle)

        # Agregar producto
        grp = QGroupBox("Agregar Producto")
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; padding-top: 14px; }")
        form = QHBoxLayout(grp)
        form.setSpacing(8)

        form.addWidget(QLabel("Codigo:"))
        self._input_codigo = QLineEdit()
        self._input_codigo.setFixedHeight(28)
        self._input_codigo.setFixedWidth(120)
        self._input_codigo.setPlaceholderText("7891234567890")
        form.addWidget(self._input_codigo)

        form.addWidget(QLabel("Descripcion:"))
        self._input_desc = QLineEdit()
        self._input_desc.setFixedHeight(28)
        self._input_desc.setPlaceholderText("Nombre (opcional)")
        form.addWidget(self._input_desc, 1)

        form.addWidget(QLabel("Precio:"))
        self._input_precio = QLineEdit()
        self._input_precio.setFixedHeight(28)
        self._input_precio.setFixedWidth(90)
        self._input_precio.setPlaceholderText("0.00")
        form.addWidget(self._input_precio)

        form.addWidget(QLabel("Cant:"))
        self._spin_cant = QSpinBox()
        self._spin_cant.setRange(1, 500)
        self._spin_cant.setValue(1)
        self._spin_cant.setFixedHeight(28)
        self._spin_cant.setFixedWidth(60)
        form.addWidget(self._spin_cant)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.setFixedHeight(28)
        btn_agregar.setFixedWidth(80)
        btn_agregar.setCursor(Qt.PointingHandCursor)
        btn_agregar.clicked.connect(self._agregar)
        form.addWidget(btn_agregar)

        layout.addWidget(grp)

        # Opciones
        opts_row = QHBoxLayout()

        btn_excel = QPushButton("  Cargar desde Excel")
        btn_excel.setIcon(qta.icon("fa5s.file-excel", color="#10b981"))
        btn_excel.setFixedHeight(30)
        btn_excel.setCursor(Qt.PointingHandCursor)
        btn_excel.clicked.connect(self._cargar_excel)
        opts_row.addWidget(btn_excel)

        opts_row.addStretch()

        opts_row.addWidget(QLabel("Formato:"))
        self._combo_formato = QComboBox()
        self._combo_formato.setFixedHeight(28)
        self._combo_formato.addItems([
            "EAN-13 (13 digitos)",
            "Code128 (alfanumerico)",
            "Code39 (alfanumerico)",
        ])
        opts_row.addWidget(self._combo_formato)

        opts_row.addWidget(QLabel("Columnas:"))
        self._spin_cols = QSpinBox()
        self._spin_cols.setRange(2, 5)
        self._spin_cols.setValue(3)
        self._spin_cols.setFixedHeight(28)
        self._spin_cols.setFixedWidth(50)
        opts_row.addWidget(self._spin_cols)

        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setFixedHeight(30)
        btn_limpiar.setCursor(Qt.PointingHandCursor)
        btn_limpiar.clicked.connect(self._limpiar)
        opts_row.addWidget(btn_limpiar)

        layout.addLayout(opts_row)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Codigo", "Descripcion", "Precio", "Cantidad"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla, 1)

        # Generar
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._lbl_total = QLabel("0 etiquetas")
        self._lbl_total.setStyleSheet("font-size: 12px; color: #888;")
        btn_row.addWidget(self._lbl_total)

        btn_generar = QPushButton("  Generar PDF")
        btn_generar.setIcon(qta.icon("fa5s.file-pdf", color="#0f0f0f"))
        btn_generar.setFixedHeight(34)
        btn_generar.setFixedWidth(160)
        btn_generar.setCursor(Qt.PointingHandCursor)
        btn_generar.clicked.connect(self._generar_pdf)
        btn_row.addWidget(btn_generar)
        layout.addLayout(btn_row)

    def _agregar(self):
        codigo = self._input_codigo.text().strip()
        desc = self._input_desc.text().strip()
        precio = self._input_precio.text().strip()
        cant = self._spin_cant.value()

        if not codigo:
            QMessageBox.warning(self, "Error", "El codigo es obligatorio para generar codigo de barras.")
            return

        self._items.append({"codigo": codigo, "descripcion": desc, "precio": precio, "cantidad": cant})
        self._actualizar_tabla()
        self._input_codigo.clear()
        self._input_desc.clear()
        self._input_precio.clear()
        self._spin_cant.setValue(1)
        self._input_codigo.setFocus()

    def _cargar_excel(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar productos", "", "Excel (*.xls *.xlsx)")
        if not ruta:
            return
        try:
            import pandas as pd
            engine = "xlrd" if ruta.endswith(".xls") else "openpyxl"
            df = pd.read_excel(ruta, engine=engine)
            for _, row in df.iterrows():
                codigo = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                desc = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                precio = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                if codigo:
                    self._items.append({"codigo": codigo, "descripcion": desc, "precio": precio, "cantidad": 1})
            self._actualizar_tabla()
            QMessageBox.information(self, "OK", f"{len(df)} productos cargados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _limpiar(self):
        self._items.clear()
        self._actualizar_tabla()

    def _actualizar_tabla(self):
        self.tabla.setRowCount(len(self._items))
        total = 0
        for i, item in enumerate(self._items):
            self.tabla.setItem(i, 0, QTableWidgetItem(item["codigo"]))
            self.tabla.setItem(i, 1, QTableWidgetItem(item["descripcion"]))
            self.tabla.setItem(i, 2, QTableWidgetItem(item["precio"]))
            self.tabla.setItem(i, 3, QTableWidgetItem(str(item["cantidad"])))
            total += item["cantidad"]
        self._lbl_total.setText(f"{total} etiquetas")

    def _generar_pdf(self):
        if not self._items:
            QMessageBox.warning(self, "Error", "No hay productos para generar etiquetas.")
            return

        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar etiquetas", "etiquetas_producto.pdf", "PDF (*.pdf)")
        if not ruta:
            return

        try:
            from services.etiquetas_service import generar_etiquetas_producto
            formatos = ["ean13", "code128", "code39"]
            formato = formatos[self._combo_formato.currentIndex()]
            columnas = self._spin_cols.value()
            generar_etiquetas_producto(self._items, ruta, formato, columnas)
            QMessageBox.information(self, "OK", f"Etiquetas generadas:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
