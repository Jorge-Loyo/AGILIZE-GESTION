from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QPushButton, QHeaderView,
)
from PySide6.QtCore import Qt, Signal


class DataTable(QWidget):
    row_double_clicked = Signal(int)  # Emite el ID del registro

    def __init__(self, columns: list[str], parent=None):
        super().__init__(parent)
        self._columns = columns
        self._ids: list[int] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Barra superior: búsqueda + acciones
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar...")
        self.input_busqueda.setMinimumHeight(38)
        toolbar.addWidget(self.input_busqueda)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setMinimumHeight(38)
        toolbar.addWidget(self.btn_buscar)

        self.btn_nuevo = QPushButton("+ Nuevo")
        self.btn_nuevo.setMinimumHeight(38)
        toolbar.addWidget(self.btn_nuevo)

        layout.addLayout(toolbar)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(len(self._columns))
        self.table.setHorizontalHeaderLabels(self._columns)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table)

    def set_data(self, rows: list[tuple[int, list[str]]]):
        """rows: lista de (id, [col1, col2, ...])"""
        self._ids = []
        self.table.setRowCount(len(rows))
        for i, (row_id, values) in enumerate(rows):
            self._ids.append(row_id)
            for j, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(i, j, item)

    def selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row >= 0 and row < len(self._ids):
            return self._ids[row]
        return None

    def _on_double_click(self, index):
        row = index.row()
        if row < len(self._ids):
            self.row_double_clicked.emit(self._ids[row])
