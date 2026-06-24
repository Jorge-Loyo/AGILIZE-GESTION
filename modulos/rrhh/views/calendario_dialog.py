from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QFrame, QSpinBox,
)
from PySide6.QtCore import Qt
from datetime import date
import calendar
from services.rrhh.asistencia_service import asistencia_service
from services.rrhh.empleado_service import empleado_service


class CalendarioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calendario de Asistencia")
        self.setMinimumSize(650, 500)
        self.setModal(True)
        self._build_ui()
        self._cargar_calendario()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Calendario de Asistencia")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(8)

        filtros.addWidget(QLabel("Empleado:"))
        self.combo_empleado = QComboBox()
        self.combo_empleado.setMinimumHeight(32)
        self.combo_empleado.setMinimumWidth(200)
        emps = empleado_service.listar()
        emps_sorted = sorted(emps, key=lambda e: int(e.legajo) if e.legajo and e.legajo.isdigit() else 9999)
        for emp in emps_sorted:
            self.combo_empleado.addItem(f"{emp.legajo} - {emp.nombre} {emp.apellido or ''}", emp.id)
        self.combo_empleado.currentIndexChanged.connect(self._cargar_calendario)
        filtros.addWidget(self.combo_empleado)

        filtros.addWidget(QLabel("Mes:"))
        self.spin_mes = QSpinBox()
        self.spin_mes.setMinimumHeight(32)
        self.spin_mes.setRange(1, 12)
        self.spin_mes.setValue(date.today().month)
        self.spin_mes.valueChanged.connect(self._cargar_calendario)
        filtros.addWidget(self.spin_mes)

        filtros.addWidget(QLabel("Anio:"))
        self.spin_anio = QSpinBox()
        self.spin_anio.setMinimumHeight(32)
        self.spin_anio.setRange(2020, 2050)
        self.spin_anio.setValue(date.today().year)
        self.spin_anio.valueChanged.connect(self._cargar_calendario)
        filtros.addWidget(self.spin_anio)

        filtros.addStretch()
        layout.addLayout(filtros)

        # Resumen
        self.lbl_resumen = QLabel("")
        self.lbl_resumen.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        layout.addWidget(self.lbl_resumen)

        # Grid calendario
        self.cal_frame = QFrame()
        self.cal_layout = QGridLayout(self.cal_frame)
        self.cal_layout.setSpacing(4)
        layout.addWidget(self.cal_frame)

        # Leyenda
        leyenda = QHBoxLayout()
        leyenda.addWidget(self._leyenda_item("#10b981", "Presente"))
        leyenda.addWidget(self._leyenda_item("#ef4444", "Ausente"))
        leyenda.addWidget(self._leyenda_item("#f59e0b", "Incompleto"))
        leyenda.addWidget(self._leyenda_item("#333333", "No laboral"))
        leyenda.addStretch()
        layout.addLayout(leyenda)

        layout.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setMinimumHeight(38)
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar)

    def _leyenda_item(self, color: str, texto: str) -> QFrame:
        frame = QFrame()
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(0, 0, 8, 0)
        lay.setSpacing(4)
        dot = QLabel()
        dot.setFixedSize(12, 12)
        dot.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        lay.addWidget(dot)
        lay.addWidget(QLabel(texto))
        return frame

    def _cargar_calendario(self):
        # Limpiar grid anterior
        while self.cal_layout.count():
            item = self.cal_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        emp_id = self.combo_empleado.currentData()
        mes = self.spin_mes.value()
        anio = self.spin_anio.value()

        if not emp_id:
            return

        # Headers dias de la semana
        dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]
        for col, dia in enumerate(dias_semana):
            lbl = QLabel(dia)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight: bold; color: #888888; font-size: 11px;")
            self.cal_layout.addWidget(lbl, 0, col)

        # Obtener asistencias del mes
        desde = date(anio, mes, 1)
        if mes == 12:
            hasta = date(anio + 1, 1, 1)
        else:
            hasta = date(anio, mes + 1, 1)

        registros = asistencia_service.listar(empleado_id=emp_id, desde=desde, hasta=hasta)
        reg_map = {r.fecha: r for r in registros}

        # Obtener dias laborales del empleado
        emp = next((e for e in empleado_service.listar() if e.id == emp_id), None)
        dias_laborales = (emp.dias_laborales or "lun,mar,mie,jue,vie").split(",") if emp else []
        dia_map = {"lun": 0, "mar": 1, "mie": 2, "jue": 3, "vie": 4, "sab": 5, "dom": 6}
        dias_lab_nums = [dia_map.get(d, -1) for d in dias_laborales]

        # Generar calendario
        cal = calendar.monthcalendar(anio, mes)
        dias_presentes = 0
        dias_ausentes = 0
        dias_incompletos = 0

        for row_idx, semana in enumerate(cal):
            for col_idx, dia in enumerate(semana):
                if dia == 0:
                    continue

                fecha = date(anio, mes, dia)
                registro = reg_map.get(fecha)

                cell = QLabel(str(dia))
                cell.setAlignment(Qt.AlignCenter)
                cell.setFixedSize(50, 40)
                cell.setStyleSheet("border-radius: 6px; font-size: 12px; font-weight: bold;")

                if registro:
                    if getattr(registro, 'incompleto', False):
                        cell.setStyleSheet(cell.styleSheet() + "background-color: #f59e0b; color: #0f0f0f;")
                        cell.setToolTip(f"{fecha.strftime('%d/%m')} - INCOMPLETO\nEntrada: {registro.hora_entrada}")
                        dias_incompletos += 1
                    else:
                        cell.setStyleSheet(cell.styleSheet() + "background-color: #10b981; color: #0f0f0f;")
                        cell.setToolTip(f"{fecha.strftime('%d/%m')} - {registro.hora_entrada.strftime('%H:%M')}-{registro.hora_salida.strftime('%H:%M')}\nN:{registro.horas_normales}h E:{registro.horas_extra}h")
                        dias_presentes += 1
                elif col_idx in dias_lab_nums:
                    # Dia laboral sin registro = ausente
                    if fecha <= date.today():
                        cell.setStyleSheet(cell.styleSheet() + "background-color: #ef4444; color: #ffffff;")
                        cell.setToolTip(f"{fecha.strftime('%d/%m')} - AUSENTE")
                        dias_ausentes += 1
                    else:
                        cell.setStyleSheet(cell.styleSheet() + "background-color: #1f1f1f; color: #555555;")
                else:
                    cell.setStyleSheet(cell.styleSheet() + "background-color: #1a1a1a; color: #444444;")
                    cell.setToolTip(f"{fecha.strftime('%d/%m')} - No laboral")

                self.cal_layout.addWidget(cell, row_idx + 1, col_idx)

        self.lbl_resumen.setText(
            f"Presentes: {dias_presentes} | Ausentes: {dias_ausentes} | Incompletos: {dias_incompletos} | "
            f"Total dias trabajados: {dias_presentes + dias_incompletos}"
        )
