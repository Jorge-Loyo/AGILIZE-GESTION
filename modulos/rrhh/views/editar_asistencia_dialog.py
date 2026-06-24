from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTimeEdit, QDateEdit, QComboBox,
    QMessageBox, QWidget,
)
from PySide6.QtCore import Qt, Signal, QDate, QTime
from services.rrhh.asistencia_service import asistencia_service


class EditarAsistenciaDialog(QDialog):
    registro_actualizado = Signal()

    def __init__(self, registro, parent=None):
        super().__init__(parent)
        self._reg = registro
        self.setWindowTitle("Editar Registro de Asistencia")
        self.setFixedSize(400, 280)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Info empleado
        nombre = f"{self._reg.empleado.apellido}, {self._reg.empleado.nombre}" if self._reg.empleado else "—"
        lbl_emp = QLabel(nombre)
        lbl_emp.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(lbl_emp)

        # Form
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)

        grid.addWidget(QLabel("Fecha:"), 0, 0)
        self.input_fecha = QDateEdit()
        self.input_fecha.setMinimumHeight(36)
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate(self._reg.fecha.year, self._reg.fecha.month, self._reg.fecha.day))
        grid.addWidget(self.input_fecha, 0, 1)

        grid.addWidget(QLabel("Entrada:"), 1, 0)
        self.input_entrada = QTimeEdit()
        self.input_entrada.setMinimumHeight(36)
        self.input_entrada.setDisplayFormat("HH:mm")
        if self._reg.hora_entrada:
            self.input_entrada.setTime(QTime(self._reg.hora_entrada.hour, self._reg.hora_entrada.minute))
        grid.addWidget(self.input_entrada, 1, 1)

        grid.addWidget(QLabel("Salida:"), 2, 0)
        self.input_salida = QTimeEdit()
        self.input_salida.setMinimumHeight(36)
        self.input_salida.setDisplayFormat("HH:mm")
        if self._reg.hora_salida:
            self.input_salida.setTime(QTime(self._reg.hora_salida.hour, self._reg.hora_salida.minute))
        grid.addWidget(self.input_salida, 2, 1)

        # Info tipo día
        grid.addWidget(QLabel("Tipo día:"), 3, 0)
        self.lbl_tipo = QLabel(self._reg.tipo_dia.capitalize())
        self.lbl_tipo.setStyleSheet("font-weight: bold;")
        grid.addWidget(self.lbl_tipo, 3, 1)

        layout.addLayout(grid)

        # Botones
        btns = QHBoxLayout()
        btns.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(38)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_cancelar.clicked.connect(self.close)
        btns.addWidget(btn_cancelar)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setMinimumHeight(38)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)

        layout.addLayout(btns)

    def _guardar(self):
        fecha = self.input_fecha.date().toPython()
        entrada = self.input_entrada.time().toPython()
        salida = self.input_salida.time().toPython()

        if entrada == salida:
            QMessageBox.warning(self, "Error", "Entrada y salida no pueden ser iguales.")
            return

        try:
            asistencia_service.registrar(self._reg.empleado_id, fecha, entrada, salida)
            self.registro_actualizado.emit()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
