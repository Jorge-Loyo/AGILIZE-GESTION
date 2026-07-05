from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, Signal
from services.rrhh.empleado_service import empleado_service
from services.core.pais_config_service import label_doc_identidad, label_id_fiscal, moneda


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
            (label_doc_identidad(), emp.dni),
            (label_id_fiscal(), emp.cuil),
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
            ("Valor Hora", f"{moneda()} {emp.valor_hora:,.2f}" if emp.valor_hora else "—"),
            ("Sueldo Mensual", f"{moneda()} {emp.sueldo_mensual:,.2f}" if emp.sueldo_mensual else "—"),
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

        # Histórico de Sueldo
        historico = self._obtener_historico(self._empleado_id)
        if historico:
            row += 1
            lbl_hist = QLabel("Histórico de Sueldo")
            lbl_hist.setStyleSheet("color: #D4AF37; font-size: 14px; font-weight: bold; margin-top: 12px;")
            grid.addWidget(lbl_hist, row, 0, 1, 4)

            row += 1
            tabla = QTableWidget(len(historico), 4)
            tabla.setHorizontalHeaderLabels(["Fecha", "Campo", "Anterior", "Nuevo"])
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tabla.setEditTriggers(QTableWidget.NoEditTriggers)
            tabla.setMaximumHeight(150)
            nombres_campo = {"valor_hora": "Valor Hora", "valor_hora_extra": "Valor Hora Extra", "sueldo_mensual": "Sueldo Mensual"}
            for i, reg in enumerate(historico):
                tabla.setItem(i, 0, QTableWidgetItem(reg.fecha_cambio.strftime("%d/%m/%Y %H:%M")))
                tabla.setItem(i, 1, QTableWidgetItem(nombres_campo.get(reg.campo, reg.campo)))
                tabla.setItem(i, 2, QTableWidgetItem(f"{moneda()} {reg.valor_anterior:,.2f}"))
                tabla.setItem(i, 3, QTableWidgetItem(f"{moneda()} {reg.valor_nuevo:,.2f}"))
            grid.addWidget(tabla, row, 0, 1, 4)

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

    def _obtener_historico(self, empleado_id: int):
        from core.database import get_db
        from models.historico_sueldo import HistoricoSueldo
        with get_db() as db:
            return db.query(HistoricoSueldo).filter(
                HistoricoSueldo.empleado_id == empleado_id
            ).order_by(HistoricoSueldo.fecha_cambio.desc()).all()

    def _on_editar(self):
        self.editar_clicked.emit(self._empleado_id)
        self.close()
