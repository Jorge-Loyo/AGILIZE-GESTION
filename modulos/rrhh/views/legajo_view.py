"""Vista de Legajo Digital - Historial de eventos por empleado."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox, QDialog, QLineEdit, QTextEdit, QFormLayout,
)
from PySide6.QtCore import Qt
import qtawesome as qta


class LegajoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("Legajo Digital")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        # Selector empleado
        row = QHBoxLayout()
        row.addWidget(QLabel("Empleado:"))
        self._combo_emp = QComboBox()
        self._combo_emp.setFixedHeight(28)
        self._combo_emp.setMinimumWidth(250)
        self._cargar_empleados()
        self._combo_emp.currentIndexChanged.connect(self._cargar_legajo)
        row.addWidget(self._combo_emp)
        row.addStretch()

        btn_nuevo = QPushButton("  Registrar Evento")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(28)
        btn_nuevo.clicked.connect(self._nuevo_evento)
        row.addWidget(btn_nuevo)
        layout.addLayout(row)

        # Tabla
        self._tabla = QTableWidget()
        self._tabla.setColumnCount(5)
        self._tabla.setHorizontalHeaderLabels(["Fecha", "Tipo", "Titulo", "Anterior", "Nuevo"])
        self._tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._tabla.setAlternatingRowColors(True)
        self._tabla.verticalHeader().setVisible(False)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._tabla, 1)

    def _cargar_empleados(self):
        from services.rrhh.empleado_service import empleado_service
        empleados = empleado_service.listar()
        for e in empleados:
            self._combo_emp.addItem(f"{e.legajo} - {e.apellido}, {e.nombre}", e.id)

    def _cargar_legajo(self):
        emp_id = self._combo_emp.currentData()
        if not emp_id:
            return
        from services.rrhh.empleado_service import empleado_service
        eventos = empleado_service.listar_legajo(emp_id)
        self._tabla.setRowCount(len(eventos))
        for i, ev in enumerate(eventos):
            self._tabla.setItem(i, 0, QTableWidgetItem(ev.fecha.strftime("%d/%m/%Y") if ev.fecha else ""))
            tipo_item = QTableWidgetItem(ev.tipo.replace("_", " ").capitalize())
            self._tabla.setItem(i, 1, tipo_item)
            self._tabla.setItem(i, 2, QTableWidgetItem(ev.titulo))
            self._tabla.setItem(i, 3, QTableWidgetItem(ev.valor_anterior))
            self._tabla.setItem(i, 4, QTableWidgetItem(ev.valor_nuevo))

    def _nuevo_evento(self):
        emp_id = self._combo_emp.currentData()
        if not emp_id:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Registrar Evento en Legajo")
        dlg.setMinimumWidth(450)
        lay = QVBoxLayout(dlg)
        form = QFormLayout()

        combo_tipo = QComboBox()
        combo_tipo.addItems(["ascenso", "cambio_sueldo", "sancion", "herramienta", "evaluacion", "capacitacion", "otro"])
        form.addRow("Tipo:", combo_tipo)
        input_titulo = QLineEdit()
        input_titulo.setMaxLength(200)
        form.addRow("Titulo:", input_titulo)
        input_desc = QTextEdit()
        input_desc.setMaximumHeight(80)
        form.addRow("Descripcion:", input_desc)
        input_ant = QLineEdit()
        input_ant.setMaxLength(100)
        form.addRow("Valor anterior:", input_ant)
        input_new = QLineEdit()
        input_new.setMaxLength(100)
        form.addRow("Valor nuevo:", input_new)
        lay.addLayout(form)

        btn = QPushButton("Registrar")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)

        if dlg.exec() == QDialog.Accepted:
            from services.rrhh.empleado_service import empleado_service
            empleado_service.registrar_evento_legajo(
                emp_id, combo_tipo.currentText(), input_titulo.text(),
                input_desc.toPlainText(), input_ant.text(), input_new.text()
            )
            self._cargar_legajo()
