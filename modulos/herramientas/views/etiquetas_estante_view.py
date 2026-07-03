"""
Etiquetas de Estante - Genera etiquetas para gondola/estante
con nombre del producto, precio y codigo.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox,
    QFileDialog, QMessageBox, QGroupBox, QLineEdit, QComboBox,
    QCheckBox, QDialog, QDialogButtonBox, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt
import qtawesome as qta


class EtiquetasEstanteView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        title = QLabel("Etiquetas de Estante")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Genera etiquetas para gondola con nombre, precio y codigo del producto.")
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
        self._input_codigo.setFixedWidth(100)
        self._input_codigo.setPlaceholderText("COD001")
        form.addWidget(self._input_codigo)

        form.addWidget(QLabel("Descripcion:"))
        self._input_desc = QLineEdit()
        self._input_desc.setFixedHeight(28)
        self._input_desc.setPlaceholderText("Nombre del producto")
        form.addWidget(self._input_desc, 1)

        form.addWidget(QLabel("Precio:"))
        self._input_precio = QLineEdit()
        self._input_precio.setFixedHeight(28)
        self._input_precio.setFixedWidth(100)
        self._input_precio.setPlaceholderText("0.00")
        form.addWidget(self._input_precio)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.setFixedHeight(28)
        btn_agregar.setFixedWidth(80)
        btn_agregar.setCursor(Qt.PointingHandCursor)
        btn_agregar.clicked.connect(self._agregar)
        form.addWidget(btn_agregar)

        layout.addWidget(grp)

        # Fila: Excel + Filtros
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)

        btn_excel = QPushButton("  Cargar desde Excel")
        btn_excel.setIcon(qta.icon("fa5s.file-excel", color="#10b981"))
        btn_excel.setFixedHeight(30)
        btn_excel.setCursor(Qt.PointingHandCursor)
        btn_excel.clicked.connect(self._cargar_excel)
        filter_row.addWidget(btn_excel)

        filter_row.addWidget(QLabel("Buscar:"))
        self._input_buscar = QLineEdit()
        self._input_buscar.setFixedHeight(28)
        self._input_buscar.setFixedWidth(180)
        self._input_buscar.setPlaceholderText("Filtrar por nombre/codigo...")
        self._input_buscar.textChanged.connect(self._filtrar_tabla)
        filter_row.addWidget(self._input_buscar)

        self._chk_ocultar_sin_precio = QCheckBox("Ocultar precio 0")
        self._chk_ocultar_sin_precio.stateChanged.connect(self._filtrar_tabla)
        filter_row.addWidget(self._chk_ocultar_sin_precio)

        filter_row.addStretch()

        filter_row.addWidget(QLabel("Tamano:"))
        self._combo_tamano = QComboBox()
        self._combo_tamano.setFixedHeight(28)
        self._combo_tamano.addItems(["Pequeno (3x5 cm)", "Mediano (5x7 cm)", "Grande (7x10 cm)"])
        self._combo_tamano.setCurrentIndex(1)
        filter_row.addWidget(self._combo_tamano)

        layout.addLayout(filter_row)

        # Seleccion masiva
        sel_row = QHBoxLayout()
        sel_row.setSpacing(8)

        btn_sel_todos = QPushButton("Seleccionar todos")
        btn_sel_todos.setFixedHeight(26)
        btn_sel_todos.setCursor(Qt.PointingHandCursor)
        btn_sel_todos.clicked.connect(self._seleccionar_todos)
        sel_row.addWidget(btn_sel_todos)

        btn_desel_todos = QPushButton("Deseleccionar todos")
        btn_desel_todos.setFixedHeight(26)
        btn_desel_todos.setCursor(Qt.PointingHandCursor)
        btn_desel_todos.clicked.connect(self._deseleccionar_todos)
        sel_row.addWidget(btn_desel_todos)

        btn_eliminar_sel = QPushButton("Eliminar seleccionados")
        btn_eliminar_sel.setFixedHeight(26)
        btn_eliminar_sel.setCursor(Qt.PointingHandCursor)
        btn_eliminar_sel.setStyleSheet("QPushButton { color: #ef4444; } QPushButton:hover { color: #dc2626; }")
        btn_eliminar_sel.clicked.connect(self._eliminar_seleccionados)
        sel_row.addWidget(btn_eliminar_sel)

        sel_row.addStretch()

        btn_limpiar = QPushButton("Limpiar todo")
        btn_limpiar.setFixedHeight(26)
        btn_limpiar.setCursor(Qt.PointingHandCursor)
        btn_limpiar.clicked.connect(self._limpiar)
        sel_row.addWidget(btn_limpiar)

        layout.addLayout(sel_row)

        # Tabla sin columna cantidad
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["", "Codigo", "Descripcion", "Precio"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setColumnWidth(0, 30)
        self.tabla.setColumnWidth(1, 120)
        self.tabla.setColumnWidth(3, 100)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla, 1)

        # Boton generar
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._lbl_total = QLabel("0 productos seleccionados")
        self._lbl_total.setStyleSheet("font-size: 12px; color: #888;")
        btn_row.addWidget(self._lbl_total)

        btn_generar = QPushButton("  Generar PDF")
        btn_generar.setIcon(qta.icon("fa5s.file-pdf", color="#0f0f0f"))
        btn_generar.setFixedHeight(34)
        btn_generar.setFixedWidth(180)
        btn_generar.setCursor(Qt.PointingHandCursor)
        btn_generar.clicked.connect(self._generar_pdf)
        btn_row.addWidget(btn_generar)
        layout.addLayout(btn_row)

    def _agregar(self):
        desc = self._input_desc.text().strip()
        if not desc:
            QMessageBox.warning(self, "Error", "La descripcion es obligatoria.")
            return
        self._items.append({
            "codigo": self._input_codigo.text().strip(),
            "descripcion": desc,
            "precio": self._input_precio.text().strip(),
            "selected": True,
        })
        self._filtrar_tabla()
        self._input_codigo.clear()
        self._input_desc.clear()
        self._input_precio.clear()
        self._input_codigo.setFocus()

    def _cargar_excel(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar productos", "", "Excel (*.xls *.xlsx)")
        if not ruta:
            return
        try:
            import pandas as pd
            engine = "xlrd" if ruta.endswith(".xls") else "openpyxl"
            df = pd.read_excel(ruta, engine=engine)
            count = 0
            for _, row in df.iterrows():
                codigo = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                desc = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                precio = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                if desc:
                    self._items.append({"codigo": codigo, "descripcion": desc, "precio": precio, "selected": True})
                    count += 1
            self._filtrar_tabla()
            QMessageBox.information(self, "OK", f"{count} productos cargados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _limpiar(self):
        self._items.clear()
        self._filtrar_tabla()

    def _filtrar_tabla(self):
        busqueda = self._input_buscar.text().strip().lower()
        ocultar_sin_precio = self._chk_ocultar_sin_precio.isChecked()

        visibles = []
        for i, item in enumerate(self._items):
            if ocultar_sin_precio:
                try:
                    p = float(item["precio"]) if item["precio"] else 0
                except ValueError:
                    p = 0
                if p == 0:
                    continue
            if busqueda:
                if busqueda not in item["descripcion"].lower() and busqueda not in item["codigo"].lower():
                    continue
            visibles.append((i, item))

        self.tabla.setRowCount(len(visibles))
        sel_count = 0
        for row, (idx, item) in enumerate(visibles):
            chk = QCheckBox()
            chk.setChecked(item.get("selected", True))
            chk.stateChanged.connect(lambda state, i=idx: self._toggle_item(i, state))
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.tabla.setCellWidget(row, 0, chk_widget)

            self.tabla.setItem(row, 1, QTableWidgetItem(item["codigo"]))
            self.tabla.setItem(row, 2, QTableWidgetItem(item["descripcion"]))
            self.tabla.setItem(row, 3, QTableWidgetItem(item["precio"]))

            if item.get("selected", True):
                sel_count += 1

        self._lbl_total.setText(f"{sel_count} productos seleccionados")

    def _toggle_item(self, idx: int, state: int):
        self._items[idx]["selected"] = (state == Qt.Checked.value)
        sel_count = sum(1 for it in self._items if it.get("selected"))
        self._lbl_total.setText(f"{sel_count} productos seleccionados")

    def _seleccionar_todos(self):
        for item in self._items:
            item["selected"] = True
        self._filtrar_tabla()

    def _deseleccionar_todos(self):
        for item in self._items:
            item["selected"] = False
        self._filtrar_tabla()

    def _eliminar_seleccionados(self):
        self._items = [it for it in self._items if not it.get("selected")]
        self._filtrar_tabla()

    def _generar_pdf(self):
        seleccionados = [it for it in self._items if it.get("selected")]
        if not seleccionados:
            QMessageBox.warning(self, "Error", "No hay productos seleccionados.")
            return

        # Dialogo para pedir cantidad de cada etiqueta
        dlg = _DialogoCantidades(seleccionados, self)
        if dlg.exec() != QDialog.Accepted:
            return

        items_con_cantidad = dlg.get_items()
        if not items_con_cantidad:
            return

        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar etiquetas", "etiquetas_estante.pdf", "PDF (*.pdf)")
        if not ruta:
            return

        try:
            from services.herramientas.etiquetas_service import generar_etiquetas_estante
            tamano_idx = self._combo_tamano.currentIndex()
            tamanos = [(3, 5), (5, 7), (7, 10)]
            tamano = tamanos[tamano_idx]
            generar_etiquetas_estante(items_con_cantidad, ruta, tamano)
            QMessageBox.information(self, "OK", f"Etiquetas generadas:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class _DialogoCantidades(QDialog):
    """Dialogo que pide cuantas etiquetas imprimir de cada producto."""

    def __init__(self, items: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cantidad de etiquetas")
        self.setMinimumWidth(420)
        self._items = items
        self._spins = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        lbl = QLabel("Indica cuantas etiquetas imprimir de cada producto:")
        lbl.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(lbl)

        # Scroll area por si hay muchos productos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        form_layout = QVBoxLayout(container)
        form_layout.setSpacing(6)

        for item in self._items:
            row = QHBoxLayout()
            row.setSpacing(8)
            nombre = QLabel(f"{item['descripcion'][:35]}")
            nombre.setFixedWidth(250)
            row.addWidget(nombre)
            spin = QSpinBox()
            spin.setRange(1, 200)
            spin.setValue(1)
            spin.setFixedWidth(70)
            spin.setFixedHeight(26)
            row.addWidget(spin)
            row.addStretch()
            form_layout.addLayout(row)
            self._spins.append(spin)

        form_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_items(self) -> list:
        result = []
        for item, spin in zip(self._items, self._spins):
            result.append({**item, "cantidad": spin.value()})
        return result
