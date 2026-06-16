from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox,
)
from PySide6.QtCore import Qt
from services.empleado_service import empleado_service


class MapeoFichadasDialog(QDialog):
    """Dialog para mapear hojas XLSX no encontradas a empleados."""

    def __init__(self, no_encontrados: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mapeo de Empleados")
        self.setMinimumSize(550, 400)
        self.setModal(True)
        self._no_encontrados = no_encontrados
        self._combos: list[QComboBox] = []
        self._resultado: dict[str, int | None] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl = QLabel(
            "Las siguientes hojas no se pudieron vincular automáticamente.\n"
            "Seleccioná el empleado correspondiente o dejá 'Ignorar'."
        )
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-size: 13px;")
        layout.addWidget(lbl)

        # Tabla con combos
        self.tabla = QTableWidget(len(self._no_encontrados), 2)
        self.tabla.setHorizontalHeaderLabels(["Hoja del archivo", "Empleado"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        emps = empleado_service.listar()
        emps.sort(key=lambda e: int(e.legajo) if e.legajo and e.legajo.isdigit() else 9999)

        for i, nombre_hoja in enumerate(self._no_encontrados):
            self.tabla.setItem(i, 0, QTableWidgetItem(nombre_hoja))
            combo = QComboBox()
            combo.addItem("— Ignorar —", None)
            for emp in emps:
                combo.addItem(f"{emp.legajo} - {emp.nombre} {emp.apellido or ''}", emp.id)
            self._combos.append(combo)
            self.tabla.setCellWidget(i, 1, combo)

        layout.addWidget(self.tabla)

        # Botones
        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(36)
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)

        btn_aplicar = QPushButton("Aplicar Mapeo")
        btn_aplicar.setMinimumHeight(36)
        btn_aplicar.setStyleSheet("QPushButton { background-color: #D4AF37; color: #121212; font-weight: bold; }")
        btn_aplicar.clicked.connect(self._aplicar)
        btns.addWidget(btn_aplicar)
        layout.addLayout(btns)

    def _aplicar(self):
        for i, nombre_hoja in enumerate(self._no_encontrados):
            emp_id = self._combos[i].currentData()
            if emp_id is not None:
                self._resultado[nombre_hoja] = emp_id
        self.accept()

    def get_mapeo(self) -> dict[str, int]:
        """Retorna {nombre_hoja: empleado_id} para los mapeados."""
        return self._resultado
