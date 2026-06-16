from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QDateEdit, QTimeEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal, QDate, QTime
from services.asistencia_service import asistencia_service
from core.database import get_db
from models.asistencia import Asistencia


class RegistroManualDialog(QDialog):
    registro_creado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registro Manual de Asistencia")
        self.setFixedSize(450, 300)
        self.setModal(True)
        self._empleados = []
        self._build_ui()
        self._cargar_empleados()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Nuevo Registro de Asistencia")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        form = QGridLayout()
        form.setSpacing(10)
        form.setColumnStretch(1, 1)

        form.addWidget(QLabel("Empleado:"), 0, 0)
        self.combo_empleado = QComboBox()
        self.combo_empleado.setMinimumHeight(34)
        self.combo_empleado.currentIndexChanged.connect(self._on_empleado_changed)
        form.addWidget(self.combo_empleado, 0, 1)

        form.addWidget(QLabel("Fecha:"), 1, 0)
        self.input_fecha = QDateEdit()
        self.input_fecha.setMinimumHeight(34)
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate.currentDate())
        self.input_fecha.dateChanged.connect(self._verificar_duplicado)
        form.addWidget(self.input_fecha, 1, 1)

        form.addWidget(QLabel("Entrada:"), 2, 0)
        self.input_entrada = QTimeEdit()
        self.input_entrada.setMinimumHeight(34)
        self.input_entrada.setDisplayFormat("HH:mm")
        self.input_entrada.setTime(QTime(8, 0))
        form.addWidget(self.input_entrada, 2, 1)

        form.addWidget(QLabel("Salida:"), 3, 0)
        self.input_salida = QTimeEdit()
        self.input_salida.setMinimumHeight(34)
        self.input_salida.setDisplayFormat("HH:mm")
        self.input_salida.setTime(QTime(17, 0))
        form.addWidget(self.input_salida, 3, 1)

        # Aviso duplicado
        self.lbl_aviso = QLabel("")
        self.lbl_aviso.setStyleSheet("color: #f59e0b; font-size: 12px;")
        form.addWidget(self.lbl_aviso, 4, 0, 1, 2)

        layout.addLayout(form)

        # Botones
        btns = QHBoxLayout()
        btns.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(38)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)

        btn_guardar = QPushButton("Registrar")
        btn_guardar.setMinimumHeight(38)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)

        layout.addLayout(btns)

    def _cargar_empleados(self):
        self._empleados = asistencia_service.listar_empleados_activos()
        self.combo_empleado.clear()
        for emp in self._empleados:
            self.combo_empleado.addItem(f"{emp.legajo} - {emp.nombre} {emp.apellido or ''}", emp.id)
        if self._empleados:
            self._on_empleado_changed()

    def _on_empleado_changed(self):
        idx = self.combo_empleado.currentIndex()
        if idx < 0 or idx >= len(self._empleados):
            return
        emp = self._empleados[idx]
        if emp.hora_entrada:
            h, m = emp.hora_entrada.split(":")
            self.input_entrada.setTime(QTime(int(h), int(m)))
        if emp.hora_salida:
            h, m = emp.hora_salida.split(":")
            self.input_salida.setTime(QTime(int(h), int(m)))
        self._verificar_duplicado()

    def _verificar_duplicado(self):
        emp_id = self.combo_empleado.currentData()
        if not emp_id:
            return
        fecha = self.input_fecha.date().toPython()
        with get_db() as db:
            existente = db.query(Asistencia).filter_by(empleado_id=emp_id, fecha=fecha).first()
            if existente:
                self.lbl_aviso.setText(f"Este empleado ya tiene registro el {fecha.strftime('%d/%m/%Y')}. Se sobreescribira.")
            else:
                self.lbl_aviso.setText("")

    def _guardar(self):
        emp_id = self.combo_empleado.currentData()
        if not emp_id:
            QMessageBox.warning(self, "Error", "Selecciona un empleado.")
            return

        fecha = self.input_fecha.date().toPython()
        entrada = self.input_entrada.time().toPython()
        salida = self.input_salida.time().toPython()

        if entrada == salida:
            QMessageBox.warning(self, "Error", "Entrada y salida no pueden ser iguales.")
            return

        try:
            reg = asistencia_service.registrar(emp_id, fecha, entrada, salida)
            QMessageBox.information(self, "Registrado",
                f"Dia: {reg.tipo_dia.upper()} | Normales: {reg.horas_normales}h | Extra: {reg.horas_extra}h")
            self.registro_creado.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
