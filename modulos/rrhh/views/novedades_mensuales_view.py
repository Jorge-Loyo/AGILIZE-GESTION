from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QDateEdit, QDoubleSpinBox,
    QMessageBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, QDate
from datetime import date
from decimal import Decimal
from services.empleado_service import empleado_service
from services.permiso_ausencia_service import permiso_ausencia_service


class NovedadesMensualesView(QWidget):
    """Permite agregar faltas y horas extras a empleados mensuales (sin fichado)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar_empleados()
        self._cargar_tabla()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Novedades - Empleados Mensuales")
        title.setObjectName("title")
        layout.addWidget(title)

        layout.addWidget(QLabel("Registra faltas y horas extras para empleados que no fichan."))

        # Selector empleado
        sel = QHBoxLayout()
        sel.addWidget(QLabel("Empleado:"))
        self.combo_emp = QComboBox()
        self.combo_emp.setMinimumHeight(34)
        self.combo_emp.setMinimumWidth(250)
        sel.addWidget(self.combo_emp)
        sel.addStretch()
        layout.addLayout(sel)

        # === Registrar Falta ===
        grp_falta = QGroupBox("Registrar Falta (Ausencia Injustificada)")
        grp_falta.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        form_falta = QHBoxLayout(grp_falta)
        form_falta.setSpacing(10)

        form_falta.addWidget(QLabel("Fecha:"))
        self.falta_fecha = QDateEdit()
        self.falta_fecha.setMinimumHeight(34)
        self.falta_fecha.setMinimumWidth(140)
        self.falta_fecha.setCalendarPopup(True)
        self.falta_fecha.setDate(QDate.currentDate())
        self.falta_fecha.calendarWidget().setMinimumSize(300, 220)
        form_falta.addWidget(self.falta_fecha)

        btn_falta = QPushButton("Registrar Falta")
        btn_falta.setMinimumHeight(34)
        btn_falta.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_falta.clicked.connect(self._registrar_falta)
        form_falta.addWidget(btn_falta)
        form_falta.addStretch()
        layout.addWidget(grp_falta)

        # === Registrar Hs Extra ===
        grp_extra = QGroupBox("Registrar Horas Extra")
        grp_extra.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        form_extra = QHBoxLayout(grp_extra)
        form_extra.setSpacing(10)

        form_extra.addWidget(QLabel("Fecha:"))
        self.extra_fecha = QDateEdit()
        self.extra_fecha.setMinimumHeight(34)
        self.extra_fecha.setMinimumWidth(140)
        self.extra_fecha.setCalendarPopup(True)
        self.extra_fecha.setDate(QDate.currentDate())
        self.extra_fecha.calendarWidget().setMinimumSize(300, 220)
        form_extra.addWidget(self.extra_fecha)

        form_extra.addWidget(QLabel("Horas:"))
        self.extra_horas = QDoubleSpinBox()
        self.extra_horas.setMinimumHeight(34)
        self.extra_horas.setRange(0.5, 24)
        self.extra_horas.setDecimals(1)
        self.extra_horas.setValue(1.0)
        self.extra_horas.setSuffix(" hs")
        form_extra.addWidget(self.extra_horas)

        form_extra.addWidget(QLabel("Tipo:"))
        self.extra_tipo = QComboBox()
        self.extra_tipo.setMinimumHeight(34)
        self.extra_tipo.addItem("Hora Extra", "normal")
        self.extra_tipo.addItem("Feriado Trabajado", "feriado")
        form_extra.addWidget(self.extra_tipo)

        btn_extra = QPushButton("Registrar")
        btn_extra.setMinimumHeight(34)
        btn_extra.setStyleSheet("QPushButton { background-color: #f59e0b; color: #0f0f0f; } QPushButton:hover { background-color: #d97706; }")
        btn_extra.clicked.connect(self._registrar_extra)
        form_extra.addWidget(btn_extra)
        form_extra.addStretch()
        layout.addWidget(grp_extra)

        # === Tabla de novedades ===
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Empleado", "Fecha", "Tipo", "Detalle"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)

        # Boton eliminar
        btns = QHBoxLayout()
        btns.addStretch()
        btn_del = QPushButton("Eliminar Seleccionado")
        btn_del.setMinimumHeight(34)
        btn_del.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_del.clicked.connect(self._eliminar)
        btns.addWidget(btn_del)
        layout.addLayout(btns)

    def _cargar_empleados(self):
        emps = empleado_service.listar()
        mensuales = [e for e in emps if e.tipo_liquidacion == "mensual"]
        mensuales.sort(key=lambda e: int(e.legajo) if e.legajo and e.legajo.isdigit() else 9999)
        self.combo_emp.clear()
        for emp in mensuales:
            self.combo_emp.addItem(f"{emp.legajo} - {emp.nombre} {emp.apellido or ''}", emp.id)
        if not mensuales:
            self.combo_emp.addItem("(No hay empleados mensuales)", None)

    def _registrar_falta(self):
        emp_id = self.combo_emp.currentData()
        if not emp_id:
            QMessageBox.warning(self, "Error", "Selecciona un empleado mensual.")
            return
        fecha = self.falta_fecha.date().toPython()
        try:
            permiso_ausencia_service.registrar_ausencia(emp_id, fecha, justificada=False, motivo="Falta")
            QMessageBox.information(self, "OK", f"Falta registrada el {fecha.strftime('%d/%m/%Y')}.")
            self._cargar_tabla()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _registrar_extra(self):
        emp_id = self.combo_emp.currentData()
        if not emp_id:
            QMessageBox.warning(self, "Error", "Selecciona un empleado mensual.")
            return
        fecha = self.extra_fecha.date().toPython()
        horas = Decimal(str(self.extra_horas.value()))
        tipo_dia = self.extra_tipo.currentData()  # "normal" o "feriado"
        try:
            from services.asistencia_service import asistencia_service
            from datetime import time
            asistencia_service.registrar(emp_id, fecha, time(0, 0), time(0, 0), incompleto=False)
            from core.database import get_db
            from models.asistencia import Asistencia
            with get_db() as db:
                reg = db.query(Asistencia).filter(
                    Asistencia.empleado_id == emp_id,
                    Asistencia.fecha == fecha,
                ).order_by(Asistencia.id.desc()).first()
                if reg:
                    reg.horas_normales = Decimal("0") if tipo_dia == "normal" else horas
                    reg.horas_extra = horas if tipo_dia == "normal" else Decimal("0")
                    reg.tipo_dia = tipo_dia
            tipo_label = "Hs extra" if tipo_dia == "normal" else "Feriado trabajado"
            QMessageBox.information(self, "OK", f"{tipo_label}: {horas} hs registradas el {fecha.strftime('%d/%m/%Y')}.")
            self._cargar_tabla()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _cargar_tabla(self):
        emp_id = self.combo_emp.currentData()
        filas = []

        if emp_id:
            # Faltas del empleado
            ausencias = permiso_ausencia_service.listar_ausencias()
            for a in ausencias:
                if a.empleado_id == emp_id and not a.justificada:
                    nombre = f"{a.empleado.nombre} {a.empleado.apellido or ''}" if a.empleado else ""
                    filas.append((a.id, "ausencia", nombre, a.fecha.strftime("%d/%m/%Y"), "FALTA", a.motivo or ""))

            # Hs extra del empleado (registros con hora 00:00)
            from core.database import get_db
            from models.asistencia import Asistencia
            from datetime import time
            with get_db() as db:
                extras = db.query(Asistencia).filter(
                    Asistencia.empleado_id == emp_id,
                    Asistencia.hora_entrada == time(0, 0),
                ).order_by(Asistencia.fecha.desc()).all()
                emp = empleado_service.obtener(emp_id)
                nombre = f"{emp.nombre} {emp.apellido or ''}" if emp else ""
                for r in extras:
                    if r.tipo_dia == "feriado":
                        filas.append((r.id, "asistencia", nombre, r.fecha.strftime("%d/%m/%Y"), "FERIADO", f"{r.horas_normales} hs"))
                    elif r.horas_extra > 0:
                        filas.append((r.id, "asistencia", nombre, r.fecha.strftime("%d/%m/%Y"), "HS EXTRA", f"{r.horas_extra} hs"))

        self._filas = filas
        self.tabla.setRowCount(len(filas))
        for i, (rid, tipo, nombre, fecha, tipo_nov, detalle) in enumerate(filas):
            self.tabla.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla.setItem(i, 1, QTableWidgetItem(fecha))
            item_tipo = QTableWidgetItem(tipo_nov)
            if tipo_nov == "FALTA":
                item_tipo.setForeground(Qt.red)
            else:
                item_tipo.setForeground(Qt.yellow)
            self.tabla.setItem(i, 2, item_tipo)
            self.tabla.setItem(i, 3, QTableWidgetItem(detalle))

    def _eliminar(self):
        row = self.tabla.currentRow()
        if row < 0 or row >= len(self._filas):
            QMessageBox.information(self, "Seleccion", "Selecciona un registro.")
            return
        rid, tipo, nombre, fecha, tipo_nov, detalle = self._filas[row]
        resp = QMessageBox.question(self, "Eliminar", f"Eliminar {tipo_nov} de {nombre} el {fecha}?", QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            try:
                from core.database import get_db
                if tipo == "ausencia":
                    from models.permiso_empleado import Ausencia
                    with get_db() as db:
                        obj = db.get(Ausencia, rid)
                        if obj:
                            db.delete(obj)
                else:
                    from models.asistencia import Asistencia
                    with get_db() as db:
                        obj = db.get(Asistencia, rid)
                        if obj:
                            db.delete(obj)
                self._cargar_tabla()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
