from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QWidget,
)
from PySide6.QtCore import Qt, Signal
from services.empleado_service import empleado_service


class EmpleadoDetalleDialog(QDialog):
    editar_clicked = Signal(int)

    def __init__(self, empleado_id: int, parent=None):
        super().__init__(parent)
        self._empleado_id = empleado_id
        self.setWindowTitle("Detalle del Empleado")
        self.setMinimumSize(550, 500)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        emp = empleado_service.obtener(self._empleado_id)
        if not emp:
            return

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QHBoxLayout()
        nombre_lbl = QLabel(f"{emp.nombre} {emp.apellido}")
        nombre_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #D4AF37;")
        header.addWidget(nombre_lbl)
        header.addStretch()
        estado_lbl = QLabel("Activo" if emp.activo else "Inactivo")
        estado_lbl.setStyleSheet(f"font-weight: bold; color: {'#10b981' if emp.activo else '#ef4444'};")
        header.addWidget(estado_lbl)
        layout.addLayout(header)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        grid = QGridLayout(content)
        grid.setSpacing(8)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        row = 0
        datos = [
            ("DNI", emp.dni),
            ("CUIL", emp.cuil),
            ("Email", emp.email or "—"),
            ("Teléfono", emp.telefono or "—"),
            ("Dirección", emp.direccion or "—"),
            ("Fecha Nac.", emp.fecha_nacimiento.strftime("%d/%m/%Y") if emp.fecha_nacimiento else "—"),
            ("Edad", f"{emp.edad} años" if emp.edad else "—"),
            ("Fecha Ingreso", emp.fecha_ingreso.strftime("%d/%m/%Y") if emp.fecha_ingreso else "—"),
            ("Departamento", emp.departamento.nombre if emp.departamento else "—"),
            ("Cargo", emp.cargo.nombre if emp.cargo else "—"),
            ("Jornada", f"{emp.horas_jornada} hs/día" if emp.horas_jornada else "—"),
            ("Horario", f"{emp.hora_entrada} a {emp.hora_salida}" if emp.hora_entrada else "—"),
            ("Días", (emp.dias_laborales or "").replace(",", ", ").upper()),
            ("Valor Hora", f"$ {emp.valor_hora:,.2f}" if emp.valor_hora else "—"),
            ("Sueldo Mensual", f"$ {emp.sueldo_mensual:,.2f}" if emp.sueldo_mensual else "—"),
        ]

        col = 0
        for label, valor in datos:
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #a0a0a0; font-size: 12px;")
            val = QLabel(str(valor))
            val.setStyleSheet("font-size: 13px;")
            val.setWordWrap(True)

            grid.addWidget(lbl, row, col)
            grid.addWidget(val, row, col + 1)

            col += 2
            if col > 2:
                col = 0
                row += 1

        if emp.observaciones:
            row += 1
            lbl_obs = QLabel("Observaciones")
            lbl_obs.setStyleSheet("color: #a0a0a0; font-size: 12px;")
            grid.addWidget(lbl_obs, row, 0)
            val_obs = QLabel(emp.observaciones)
            val_obs.setWordWrap(True)
            val_obs.setStyleSheet("font-size: 13px;")
            grid.addWidget(val_obs, row, 1, 1, 3)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Botones
        btns = QHBoxLayout()
        btns.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setMinimumHeight(38)
        btn_cerrar.setMinimumWidth(100)
        btn_cerrar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_cerrar.clicked.connect(self.close)
        btns.addWidget(btn_cerrar)

        btn_editar = QPushButton("Editar")
        btn_editar.setMinimumHeight(38)
        btn_editar.setMinimumWidth(100)
        btn_editar.clicked.connect(self._on_editar)
        btns.addWidget(btn_editar)

        layout.addLayout(btns)

    def _on_editar(self):
        self.editar_clicked.emit(self._empleado_id)
        self.close()
