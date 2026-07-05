from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QComboBox,
)
from PySide6.QtCore import Qt, QThread, Signal
import qtawesome as qta


class CategoriasView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title = QLabel("Limpiador de Categorías")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()

        self.btn_cargar = QPushButton("  Cargar Reporte")
        self.btn_cargar.setIcon(qta.icon("fa5s.upload", color="#0f0f0f"))
        self.btn_cargar.setCursor(Qt.PointingHandCursor)
        self.btn_cargar.setFixedHeight(36)
        self.btn_cargar.clicked.connect(self._on_cargar)
        header.addWidget(self.btn_cargar)

        self.btn_exportar = QPushButton("  Exportar")
        self.btn_exportar.setIcon(qta.icon("fa5s.file-export", color="#0f0f0f"))
        self.btn_exportar.setCursor(Qt.PointingHandCursor)
        self.btn_exportar.setFixedHeight(36)
        self.btn_exportar.setEnabled(False)
        self.btn_exportar.clicked.connect(self._on_exportar)
        header.addWidget(self.btn_exportar)

        layout.addLayout(header)

        # Info
        self.lbl_info = QLabel(
            "Cargue el Reporte de Categorías (.xlsx) para extraer y limpiar categorías con sus productos"
        )
        self.lbl_info.setObjectName("subtitle")
        layout.addWidget(self.lbl_info)

        # Stats
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)

        self._stat_categorias = self._create_stat_card("Categorías", "0")
        self._stat_productos = self._create_stat_card("Productos", "0")
        stats_layout.addWidget(self._stat_categorias)
        stats_layout.addWidget(self._stat_productos)
        stats_layout.addStretch()
        layout.addWidget(stats_frame)

        # Filtro por categoría
        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Filtrar por categoría:"))
        self.combo_cat = QComboBox()
        self.combo_cat.setMinimumWidth(250)
        self.combo_cat.addItem("-- Todas --")
        self.combo_cat.currentIndexChanged.connect(self._on_filtro)
        filtro_layout.addWidget(self.combo_cat)
        filtro_layout.addStretch()
        layout.addLayout(filtro_layout)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Categoría", "Código", "Descripción", "Existencia"])
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.verticalHeader().setVisible(False)
        h = self.tabla.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.Stretch)
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.tabla, 1)

    def _create_stat_card(self, label: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(130)
        card.setMinimumHeight(70)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px; color: #888;")
        card_layout.addWidget(lbl)
        val = QLabel(value)
        val.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        card_layout.addWidget(val)
        card._value_label = val
        return card

    def _on_cargar(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Reporte de Categorías", "",
            "Excel (*.xlsx);;Todos (*.*)"
        )
        if not ruta:
            return

        self.btn_cargar.setEnabled(False)
        self.btn_cargar.setText("  Cargando...")

        class Worker(QThread):
            finished = Signal(object)
            error = Signal(str)

            def __init__(self, ruta):
                super().__init__()
                self._ruta = ruta

            def run(self):
                try:
                    from services.herramientas.categorias_service import categorias_service
                    categorias_service.cargar_reporte(self._ruta)
                    self.finished.emit(categorias_service)
                except Exception as e:
                    self.error.emit(str(e))

        self._worker = Worker(ruta)
        self._worker.finished.connect(self._on_carga_ok)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_carga_ok(self, service):
        self.btn_cargar.setEnabled(True)
        self.btn_cargar.setText("  Cargar Reporte")
        self.btn_exportar.setEnabled(True)

        master = service.master
        self._stat_categorias._value_label.setText(str(len(master.lista_categorias)))
        self._stat_productos._value_label.setText(str(master.total_productos))

        self.lbl_info.setText(
            f"✓ {len(master.lista_categorias)} categorías y "
            f"{master.total_productos} productos extraídos"
        )
        self.lbl_info.setStyleSheet("font-size: 12px; color: #10b981;")

        # Poblar combo
        self.combo_cat.blockSignals(True)
        self.combo_cat.clear()
        self.combo_cat.addItem("-- Todas --")
        for cat in master.lista_categorias:
            self.combo_cat.addItem(f"{cat} ({len(master.categorias[cat])})")
        self.combo_cat.blockSignals(False)

        self._poblar_tabla(None)

    def _on_error(self, msg: str):
        self.btn_cargar.setEnabled(True)
        self.btn_cargar.setText("  Cargar Reporte")
        self.lbl_info.setText(f"Error: {msg}")
        self.lbl_info.setStyleSheet("font-size: 12px; color: #ef4444;")
        QMessageBox.critical(self, "Error", msg)

    def _on_filtro(self):
        idx = self.combo_cat.currentIndex()
        if idx <= 0:
            self._poblar_tabla(None)
        else:
            from services.herramientas.categorias_service import categorias_service
            master = categorias_service.master
            if master:
                cat = master.lista_categorias[idx - 1]
                self._poblar_tabla(cat)

    def _poblar_tabla(self, categoria: str | None):
        from services.herramientas.categorias_service import categorias_service
        master = categorias_service.master
        if not master:
            return

        if categoria:
            productos = master.categorias.get(categoria, [])
        else:
            productos = [p for prods in master.categorias.values() for p in prods]

        self.tabla.setRowCount(len(productos))
        for i, p in enumerate(productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(p.categoria))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 2, QTableWidgetItem(p.descripcion))
            item = QTableWidgetItem(f"{p.existencia:,.0f}")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 3, item)

    def _on_exportar(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar categorías limpias",
            "Categorias_Productos.xlsx", "Excel (*.xlsx)"
        )
        if not ruta:
            return
        try:
            from services.herramientas.categorias_service import categorias_service
            result = categorias_service.exportar(ruta)
            QMessageBox.information(
                self, "Exportación completada",
                f"Archivo generado con categorías y productos:\n\n{result}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
