from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QMessageBox, QDialog, QGridLayout, QDateEdit, QDoubleSpinBox,
)
from PySide6.QtCore import Qt, QDate
from datetime import date
from decimal import Decimal
from services.rrhh.cierre_service import cierre_service
from services.rrhh.calculo_asistencia_service import calculo_asistencia_service
from services.rrhh.empleado_service import empleado_service
from services.rrhh.nomina_service import nomina_service
from services.core.pais_config_service import moneda


class ResumenMensualView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Resumen Mensual / Quincenal")
        title.setObjectName("title")
        layout.addWidget(title)

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(8)

        filtros.addWidget(QLabel("Mes:"))
        self.spin_mes = QSpinBox()
        self.spin_mes.setMinimumHeight(32)
        self.spin_mes.setRange(1, 12)
        self.spin_mes.setValue(date.today().month)
        filtros.addWidget(self.spin_mes)

        filtros.addWidget(QLabel("Anio:"))
        self.spin_anio = QSpinBox()
        self.spin_anio.setMinimumHeight(32)
        self.spin_anio.setRange(2020, 2050)
        self.spin_anio.setValue(date.today().year)
        filtros.addWidget(self.spin_anio)

        filtros.addWidget(QLabel("Vista:"))
        self.combo_vista = QComboBox()
        self.combo_vista.setMinimumHeight(32)
        self.combo_vista.addItem("Mes completo", "mes")
        self.combo_vista.addItem("Quincena 1", "q1")
        self.combo_vista.addItem("Quincena 2", "q2")
        self.combo_vista.addItem("Comparar Q1 vs Q2", "comparar")
        filtros.addWidget(self.combo_vista)

        btn_cargar = QPushButton("Ver Resumen")
        btn_cargar.setMinimumHeight(32)
        btn_cargar.clicked.connect(self._cargar)
        filtros.addWidget(btn_cargar)

        filtros.addStretch()
        layout.addLayout(filtros)

        # Estado cierres
        self.lbl_cierres = QLabel("")
        self.lbl_cierres.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(self.lbl_cierres)

        # Tabla resumen
        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)

        # Totales
        self.lbl_totales = QLabel("")
        self.lbl_totales.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(self.lbl_totales)

    def _cargar(self):
        vista = self.combo_vista.currentData()
        if vista == "comparar":
            self._cargar_comparacion()
        else:
            self._cargar_normal(vista)

    def _cargar_normal(self, vista: str):
        mes = self.spin_mes.value()
        anio = self.spin_anio.value()
        periodo = f"{anio}-{mes:02d}"

        # Determinar rango de fechas según vista
        if vista == "q1":
            desde = date(anio, mes, 1)
            hasta = date(anio, mes, 15)
        elif vista == "q2":
            desde = date(anio, mes, 16)
            if mes == 12:
                hasta = date(anio + 1, 1, 1)
            else:
                hasta = date(anio, mes + 1, 1)
            from datetime import timedelta
            hasta = hasta - timedelta(days=1)
        else:
            desde = None
            hasta = None

        # Estado de cierres
        cierres = cierre_service.listar_cierres_asistencia()
        cierres_mes = [c for c in cierres if c.periodo == periodo and c.cerrado]
        self._mostrar_estado_cierres(cierres_mes, periodo)

        # Tabla normal
        headers = ["Legajo", "Empleado", "Dias Trab.", "Hs Normales", "Hs Extra", "Bruto", "Liquidado", "Estado"]
        self.tabla.setColumnCount(len(headers))
        self.tabla.setHorizontalHeaderLabels(headers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        empleados = empleado_service.listar()
        empleados.sort(key=lambda e: int(e.legajo) if e.legajo and e.legajo.isdigit() else 9999)

        liquidaciones = nomina_service.listar_liquidaciones(periodo=periodo)
        liq_map = {l.empleado_id: l for l in liquidaciones}

        total_bruto = Decimal("0")
        total_liquidado = Decimal("0")
        filas = []

        for emp in empleados:
            if desde and hasta:
                calc = self._calcular_rango(emp.id, desde, hasta)
            else:
                calc = calculo_asistencia_service.calcular_bruto_periodo(emp.id, periodo)

            if calc["dias_trabajados"] == 0:
                continue

            liq = liq_map.get(emp.id)
            liquidado = liq.neto if liq else Decimal("0")
            estado = "Liquidado" if liq else "Pendiente"

            total_bruto += calc["bruto"]
            total_liquidado += liquidado

            filas.append((
                emp.legajo or "",
                f"{emp.nombre} {emp.apellido or ''}",
                str(calc["dias_trabajados"]),
                str(calc["hs_normales"]),
                str(calc["hs_extra"]),
                f"{moneda()} {calc['bruto']:,.2f}",
                f"{moneda()} {liquidado:,.2f}" if liq else "-",
                estado,
            ))

        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, val in enumerate(fila):
                item = QTableWidgetItem(val)
                if j == 7 and val == "Pendiente":
                    item.setForeground(Qt.red)
                self.tabla.setItem(i, j, item)

        vista_label = {"mes": "Mes completo", "q1": "Quincena 1", "q2": "Quincena 2"}[vista]
        self.lbl_totales.setText(
            f"{vista_label}  |  Total Bruto: {moneda()} {total_bruto:,.2f}  |  "
            f"Total Liquidado: {moneda()} {total_liquidado:,.2f}  |  Empleados: {len(filas)}"
        )

    def _cargar_comparacion(self):
        mes = self.spin_mes.value()
        anio = self.spin_anio.value()
        periodo = f"{anio}-{mes:02d}"

        desde_q1 = date(anio, mes, 1)
        hasta_q1 = date(anio, mes, 15)
        desde_q2 = date(anio, mes, 16)
        if mes == 12:
            hasta_q2 = date(anio, 12, 31)
        else:
            from datetime import timedelta
            hasta_q2 = date(anio, mes + 1, 1) - timedelta(days=1)

        # Estado cierres
        cierres = cierre_service.listar_cierres_asistencia()
        cierres_mes = [c for c in cierres if c.periodo == periodo and c.cerrado]
        self._mostrar_estado_cierres(cierres_mes, periodo)

        # Tabla comparación
        headers = ["Legajo", "Empleado", "Dias Q1", "Bruto Q1", "Dias Q2", "Bruto Q2", "Diferencia"]
        self.tabla.setColumnCount(len(headers))
        self.tabla.setHorizontalHeaderLabels(headers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        empleados = empleado_service.listar()
        empleados.sort(key=lambda e: int(e.legajo) if e.legajo and e.legajo.isdigit() else 9999)

        filas = []
        total_q1 = Decimal("0")
        total_q2 = Decimal("0")

        for emp in empleados:
            calc_q1 = self._calcular_rango(emp.id, desde_q1, hasta_q1)
            calc_q2 = self._calcular_rango(emp.id, desde_q2, hasta_q2)

            if calc_q1["dias_trabajados"] == 0 and calc_q2["dias_trabajados"] == 0:
                continue

            diff = calc_q2["bruto"] - calc_q1["bruto"]
            total_q1 += calc_q1["bruto"]
            total_q2 += calc_q2["bruto"]

            filas.append((
                emp.legajo or "",
                f"{emp.nombre} {emp.apellido or ''}",
                str(calc_q1["dias_trabajados"]),
                f"{moneda()} {calc_q1['bruto']:,.2f}",
                str(calc_q2["dias_trabajados"]),
                f"{moneda()} {calc_q2['bruto']:,.2f}",
                f"{moneda()} {diff:,.2f}",
            ))

        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, val in enumerate(fila):
                item = QTableWidgetItem(val)
                if j == 6:  # Diferencia
                    if val.replace("$ ", "").replace(",", "").startswith("-"):
                        item.setForeground(Qt.red)
                    else:
                        item.setForeground(Qt.green)
                self.tabla.setItem(i, j, item)

        diff_total = total_q2 - total_q1
        self.lbl_totales.setText(
            f"Q1: {moneda()} {total_q1:,.2f}  |  Q2: {moneda()} {total_q2:,.2f}  |  "
            f"Diferencia: {moneda()} {diff_total:,.2f}  |  Empleados: {len(filas)}"
        )

    def _calcular_rango(self, empleado_id: int, desde: date, hasta: date) -> dict:
        """Calcula bruto de un empleado para un rango específico de fechas."""
        from core.database import get_db
        from models.asistencia import Asistencia
        from models.empleado import Empleado
        from services.rrhh.config_nomina_service import config_nomina_service

        params = config_nomina_service.obtener_todos()
        mult_extra = params["mult_hora_extra"]
        mult_sabado = params["mult_hora_sabado"]
        mult_domingo = params["mult_hora_domingo"]
        mult_feriado = params["mult_hora_feriado"]

        with get_db() as db:
            emp = db.get(Empleado, empleado_id)
            if not emp:
                return {"dias_trabajados": 0, "hs_normales": Decimal("0"), "hs_extra": Decimal("0"), "bruto": Decimal("0")}

            valor_hora = emp.valor_hora or Decimal("0")
            valor_hora_extra = emp.valor_hora_extra if emp.valor_hora_extra else valor_hora

            registros = db.query(Asistencia).filter(
                Asistencia.empleado_id == empleado_id,
                Asistencia.fecha >= desde,
                Asistencia.fecha <= hasta,
            ).all()

            hs_normales = Decimal("0")
            hs_extra = Decimal("0")

            bruto = Decimal("0")
            for r in registros:
                if r.tipo_dia == "feriado":
                    bruto += (r.horas_normales + r.horas_extra) * valor_hora_extra * mult_feriado
                elif r.tipo_dia == "sabado":
                    bruto += (r.horas_normales + r.horas_extra) * valor_hora_extra * mult_sabado
                elif r.tipo_dia == "domingo":
                    bruto += (r.horas_normales + r.horas_extra) * valor_hora_extra * mult_domingo
                else:
                    hs_normales += r.horas_normales
                    hs_extra += r.horas_extra
                    bruto += r.horas_normales * valor_hora
                    bruto += r.horas_extra * valor_hora_extra * mult_extra

        return {
            "dias_trabajados": len(registros),
            "hs_normales": hs_normales,
            "hs_extra": hs_extra,
            "bruto": bruto.quantize(Decimal("0.01")),
        }

    def _mostrar_estado_cierres(self, cierres_mes, periodo):
        if len(cierres_mes) >= 2:
            self.lbl_cierres.setText(f"Periodo {periodo}: CERRADO (ambas quincenas)")
            self.lbl_cierres.setStyleSheet("font-size: 12px; font-weight: bold; color: #10b981;")
        elif len(cierres_mes) == 1:
            q = cierres_mes[0].quincena
            self.lbl_cierres.setText(f"Periodo {periodo}: Quincena {q} cerrada, falta Q{3-q}")
            self.lbl_cierres.setStyleSheet("font-size: 12px; font-weight: bold; color: #f59e0b;")
        else:
            self.lbl_cierres.setText(f"Periodo {periodo}: ABIERTO (sin cierres)")
            self.lbl_cierres.setStyleSheet("font-size: 12px; font-weight: bold; color: #ef4444;")

    def _get_selected_emp(self):
        row = self.tabla.currentRow()
        if row < 0 or not hasattr(self, '_empleados_tabla') or row >= len(self._empleados_tabla):
            QMessageBox.information(self, "Seleccion", "Selecciona un empleado de la tabla.")
            return None
        return self._empleados_tabla[row]

    def _agregar_falta(self):
        emp = self._get_selected_emp()
        if not emp:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Agregar Falta — {emp.nombre} {emp.apellido or ''}")
        dialog.setFixedSize(350, 180)
        dialog.setModal(True)
        dlayout = QVBoxLayout(dialog)
        dlayout.setSpacing(10)

        form = QGridLayout()
        form.addWidget(QLabel("Fecha de la falta:"), 0, 0)
        date_edit = QDateEdit()
        date_edit.setMinimumHeight(32)
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        form.addWidget(date_edit, 0, 1)

        form.addWidget(QLabel("Motivo:"), 1, 0)
        from PySide6.QtWidgets import QLineEdit
        motivo_edit = QLineEdit()
        motivo_edit.setMinimumHeight(32)
        motivo_edit.setPlaceholderText("Opcional")
        form.addWidget(motivo_edit, 1, 1)
        dlayout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dialog.reject)
        btns.addWidget(btn_cancel)
        btn_ok = QPushButton("Registrar Falta")
        btn_ok.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_ok.clicked.connect(dialog.accept)
        btns.addWidget(btn_ok)
        dlayout.addLayout(btns)

        if dialog.exec() == QDialog.Accepted:
            fecha = date_edit.date().toPython()
            motivo = motivo_edit.text().strip()
            try:
                from services.rrhh.permiso_ausencia_service import permiso_ausencia_service
                permiso_ausencia_service.registrar_ausencia(emp.id, fecha, justificada=False, motivo=motivo)
                QMessageBox.information(self, "OK", f"Falta registrada para {emp.nombre} el {fecha.strftime('%d/%m/%Y')}.")
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _agregar_hs_extra(self):
        emp = self._get_selected_emp()
        if not emp:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Agregar Hs Extra — {emp.nombre} {emp.apellido or ''}")
        dialog.setFixedSize(350, 200)
        dialog.setModal(True)
        dlayout = QVBoxLayout(dialog)
        dlayout.setSpacing(10)

        form = QGridLayout()
        form.addWidget(QLabel("Fecha:"), 0, 0)
        date_edit = QDateEdit()
        date_edit.setMinimumHeight(32)
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        form.addWidget(date_edit, 0, 1)

        form.addWidget(QLabel("Horas extra:"), 1, 0)
        hs_edit = QDoubleSpinBox()
        hs_edit.setMinimumHeight(32)
        hs_edit.setRange(0.5, 24)
        hs_edit.setDecimals(1)
        hs_edit.setValue(1.0)
        hs_edit.setSuffix(" hs")
        form.addWidget(hs_edit, 1, 1)
        dlayout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dialog.reject)
        btns.addWidget(btn_cancel)
        btn_ok = QPushButton("Registrar Extras")
        btn_ok.setStyleSheet("QPushButton { background-color: #f59e0b; color: #0f0f0f; } QPushButton:hover { background-color: #d97706; }")
        btn_ok.clicked.connect(dialog.accept)
        btns.addWidget(btn_ok)
        dlayout.addLayout(btns)

        if dialog.exec() == QDialog.Accepted:
            fecha = date_edit.date().toPython()
            horas = Decimal(str(hs_edit.value()))
            try:
                from services.rrhh.asistencia_service import asistencia_service
                from datetime import time
                # Registrar como asistencia con solo horas extra
                asistencia_service.registrar(
                    emp.id, fecha,
                    time(0, 0), time(0, 0),
                    horas_extra=horas,
                    tipo_dia="normal"
                )
                QMessageBox.information(self, "OK", f"{horas} hs extra registradas para {emp.nombre} el {fecha.strftime('%d/%m/%Y')}.")
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _get_selected_emp(self):
        row = self.tabla.currentRow()
        if row < 0 or not hasattr(self, '_empleados_tabla') or row >= len(self._empleados_tabla):
            QMessageBox.information(self, "Seleccion", "Selecciona un empleado de la tabla.")
            return None
        return self._empleados_tabla[row]

    def _agregar_falta(self):
        emp = self._get_selected_emp()
        if not emp:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Agregar Falta - {emp.nombre} {emp.apellido or ''}")
        dialog.setFixedSize(350, 160)
        dialog.setModal(True)
        dlayout = QVBoxLayout(dialog)
        form = QGridLayout()
        form.addWidget(QLabel("Fecha:"), 0, 0)
        date_edit = QDateEdit()
        date_edit.setMinimumHeight(32)
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        form.addWidget(date_edit, 0, 1)
        dlayout.addLayout(form)
        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dialog.reject)
        btns.addWidget(btn_cancel)
        btn_ok = QPushButton("Registrar Falta")
        btn_ok.clicked.connect(dialog.accept)
        btns.addWidget(btn_ok)
        dlayout.addLayout(btns)
        if dialog.exec() == QDialog.Accepted:
            fecha = date_edit.date().toPython()
            try:
                from services.rrhh.permiso_ausencia_service import permiso_ausencia_service
                permiso_ausencia_service.registrar_ausencia(emp.id, fecha, justificada=False, motivo="")
                QMessageBox.information(self, "OK", f"Falta registrada el {fecha.strftime('%d/%m/%Y')}.")
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _agregar_hs_extra(self):
        emp = self._get_selected_emp()
        if not emp:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Agregar Hs Extra - {emp.nombre} {emp.apellido or ''}")
        dialog.setFixedSize(350, 180)
        dialog.setModal(True)
        dlayout = QVBoxLayout(dialog)
        form = QGridLayout()
        form.addWidget(QLabel("Fecha:"), 0, 0)
        date_edit = QDateEdit()
        date_edit.setMinimumHeight(32)
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        form.addWidget(date_edit, 0, 1)
        form.addWidget(QLabel("Horas extra:"), 1, 0)
        hs_edit = QDoubleSpinBox()
        hs_edit.setMinimumHeight(32)
        hs_edit.setRange(0.5, 24)
        hs_edit.setDecimals(1)
        hs_edit.setValue(1.0)
        hs_edit.setSuffix(" hs")
        form.addWidget(hs_edit, 1, 1)
        dlayout.addLayout(form)
        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dialog.reject)
        btns.addWidget(btn_cancel)
        btn_ok = QPushButton("Registrar")
        btn_ok.clicked.connect(dialog.accept)
        btns.addWidget(btn_ok)
        dlayout.addLayout(btns)
        if dialog.exec() == QDialog.Accepted:
            fecha = date_edit.date().toPython()
            horas = Decimal(str(hs_edit.value()))
            try:
                from services.rrhh.asistencia_service import asistencia_service
                from datetime import time
                asistencia_service.registrar(emp.id, fecha, time(0, 0), time(0, 0), horas_extra=horas)
                QMessageBox.information(self, "OK", f"{horas} hs extra registradas el {fecha.strftime('%d/%m/%Y')}.")
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
