from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QLineEdit, QPushButton, QLabel,
    QMessageBox, QGroupBox, QCheckBox, QScrollArea, QFrame,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, Signal
from decimal import Decimal
from datetime import date
from services.nomina_service import nomina_service
from services.empleado_service import empleado_service
from services.calculo_asistencia_service import calculo_asistencia_service


class LiquidarView(QWidget):
    liquidacion_creada = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._empleados = []
        self._conceptos = []
        self._calculo = None
        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        clayout = QVBoxLayout(content)
        clayout.setSpacing(12)

        title = QLabel("Nueva Liquidaci\u00f3n")
        title.setObjectName("title")
        clayout.addWidget(title)

        # === Encabezado ===
        grp_header = self._grp("Datos")
        header_layout = QGridLayout(grp_header)
        header_layout.setSpacing(8)
        header_layout.setColumnStretch(1, 1)
        header_layout.setColumnStretch(3, 1)

        header_layout.addWidget(QLabel("Periodo:"), 0, 0)
        self.combo_periodo = QComboBox()
        self.combo_periodo.setMinimumHeight(32)
        self.combo_periodo.currentIndexChanged.connect(self._on_periodo_changed)
        header_layout.addWidget(self.combo_periodo, 0, 1)

        header_layout.addWidget(QLabel("Empleado:"), 0, 2)
        self.combo_empleado = QComboBox()
        self.combo_empleado.setMinimumHeight(32)
        self.combo_empleado.currentIndexChanged.connect(self._recalcular)
        header_layout.addWidget(self.combo_empleado, 0, 3)

        # Boton verificar
        btn_verificar = QPushButton("Verificar Periodo")
        btn_verificar.setMinimumHeight(32)
        btn_verificar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_verificar.clicked.connect(self._verificar_periodo)
        header_layout.addWidget(btn_verificar, 1, 3)

        clayout.addWidget(grp_header)

        # === Detalle de Asistencia ===
        grp_asist = self._grp("Horas Trabajadas (desde Asistencia)")
        self.asist_layout = QGridLayout(grp_asist)
        self.asist_layout.setSpacing(6)

        self.lbl_hs_normales = QLabel("—")
        self.lbl_hs_extra = QLabel("—")
        self.lbl_hs_sabado = QLabel("—")
        self.lbl_hs_domingo = QLabel("—")
        self.lbl_hs_feriado = QLabel("—")
        self.lbl_valor_hora = QLabel("—")
        self.lbl_bruto = QLabel("—")
        self.lbl_bruto.setStyleSheet("font-weight: bold; color: #D4AF37; font-size: 14px;")

        self.asist_layout.addWidget(QLabel("Hs Normales:"), 0, 0)
        self.asist_layout.addWidget(self.lbl_hs_normales, 0, 1)
        self.asist_layout.addWidget(QLabel("Hs Extra:"), 0, 2)
        self.asist_layout.addWidget(self.lbl_hs_extra, 0, 3)
        self.asist_layout.addWidget(QLabel("Hs S\u00e1bado:"), 1, 0)
        self.asist_layout.addWidget(self.lbl_hs_sabado, 1, 1)
        self.asist_layout.addWidget(QLabel("Hs Domingo:"), 1, 2)
        self.asist_layout.addWidget(self.lbl_hs_domingo, 1, 3)
        self.asist_layout.addWidget(QLabel("Hs Feriado:"), 2, 0)
        self.asist_layout.addWidget(self.lbl_hs_feriado, 2, 1)
        self.asist_layout.addWidget(QLabel("Valor Hora:"), 2, 2)
        self.asist_layout.addWidget(self.lbl_valor_hora, 2, 3)
        self.asist_layout.addWidget(QLabel("BRUTO por Asistencia:"), 3, 0, 1, 2)
        self.asist_layout.addWidget(self.lbl_bruto, 3, 2, 1, 2)

        clayout.addWidget(grp_asist)

        # === Conceptos ===
        grp_conceptos = self._grp("Conceptos a Aplicar (sobre el bruto)")
        conceptos_layout = QVBoxLayout(grp_conceptos)
        self._conceptos_checks: list[tuple[QCheckBox, int]] = []
        self.conceptos_container = QGridLayout()
        self.conceptos_container.setSpacing(6)
        conceptos_layout.addLayout(self.conceptos_container)
        clayout.addWidget(grp_conceptos)

        # === Detalle Recibo ===
        grp_preview = self._grp("Detalle del Recibo")
        preview_layout = QVBoxLayout(grp_preview)

        self.tabla_detalle = QTableWidget()
        self.tabla_detalle.setColumnCount(3)
        self.tabla_detalle.setHorizontalHeaderLabels(["Concepto", "Tipo", "Monto"])
        self.tabla_detalle.horizontalHeader().setStretchLastSection(True)
        self.tabla_detalle.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_detalle.setAlternatingRowColors(True)
        self.tabla_detalle.verticalHeader().setVisible(False)
        self.tabla_detalle.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_detalle.setMaximumHeight(180)
        preview_layout.addWidget(self.tabla_detalle)

        totales_layout = QHBoxLayout()
        totales_layout.setSpacing(16)
        self.lbl_haberes = QLabel("Haberes: $ 0.00")
        self.lbl_haberes.setStyleSheet("font-weight: bold; color: #10b981;")
        totales_layout.addWidget(self.lbl_haberes)
        self.lbl_deducciones = QLabel("Deducciones: $ 0.00")
        self.lbl_deducciones.setStyleSheet("font-weight: bold; color: #ef4444;")
        totales_layout.addWidget(self.lbl_deducciones)
        totales_layout.addStretch()
        self.lbl_neto = QLabel("NETO: $ 0.00")
        self.lbl_neto.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        totales_layout.addWidget(self.lbl_neto)
        preview_layout.addLayout(totales_layout)

        clayout.addWidget(grp_preview)
        clayout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # === Botones (fijos abajo) ===
        btns = QHBoxLayout()
        btns.addStretch()
        btn_liquidar = QPushButton("Confirmar Liquidaci\u00f3n")
        btn_liquidar.setMinimumHeight(40)
        btn_liquidar.setMinimumWidth(160)
        btn_liquidar.clicked.connect(self._confirmar)
        btns.addWidget(btn_liquidar)
        layout.addLayout(btns)

    def _grp(self, title: str) -> QGroupBox:
        g = QGroupBox(title)
        g.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 4px; }")
        return g

    def _cargar_datos(self):
        from services.liquidacion_pendiente_service import liquidacion_pendiente_service

        # Cargar periodos pendientes
        periodos = liquidacion_pendiente_service.periodos_pendientes()
        self.combo_periodo.clear()
        for p in periodos:
            resumen = liquidacion_pendiente_service.resumen_periodo(p)
            self.combo_periodo.addItem(f"{p} ({resumen['pendientes']} pendientes)", p)

        if not periodos:
            # Mostrar todos los periodos con asistencia
            todos = liquidacion_pendiente_service.periodos_con_asistencia()
            for p in todos:
                self.combo_periodo.addItem(f"{p} (completo)", p)

        # Cargar conceptos
        self._conceptos = nomina_service.listar_conceptos()
        row, col = 0, 0
        for c in self._conceptos:
            tipo_tag = "+" if c.tipo == "haber" else "\u2212"
            label = f"{tipo_tag} {c.nombre}"
            if c.porcentaje:
                label += f" ({c.porcentaje}%)"
            elif c.monto_fijo:
                label += f" (${c.monto_fijo})"
            chk = QCheckBox(label)
            chk.setChecked(False)
            chk.stateChanged.connect(self._recalcular)
            self._conceptos_checks.append((chk, c.id))
            self.conceptos_container.addWidget(chk, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _on_periodo_changed(self):
        """Al cambiar periodo, cargar empleados pendientes de ese periodo."""
        from services.liquidacion_pendiente_service import liquidacion_pendiente_service
        periodo = self.combo_periodo.currentData()
        if not periodo:
            return

        empleados = liquidacion_pendiente_service.empleados_pendientes(periodo)
        self.combo_empleado.clear()
        empleados_sorted = sorted(empleados, key=lambda e: int(e.legajo) if e.legajo and e.legajo.isdigit() else 9999)
        for emp in empleados_sorted:
            self.combo_empleado.addItem(f"{emp.legajo} - {emp.nombre} {emp.apellido or ''}", emp.id)

    def _verificar_periodo(self):
        """Muestra resumen del estado de liquidacion del periodo."""
        from services.liquidacion_pendiente_service import liquidacion_pendiente_service
        periodo = self.combo_periodo.currentData()
        if not periodo:
            QMessageBox.information(self, "Info", "No hay periodo seleccionado.")
            return

        resumen = liquidacion_pendiente_service.resumen_periodo(periodo)
        estado = "COMPLETO" if resumen["completo"] else "PENDIENTE"
        msg = (
            f"Periodo: {resumen['periodo']}\n"
            f"Estado: {estado}\n\n"
            f"Empleados con asistencia: {resumen['total_con_asistencia']}\n"
            f"Ya liquidados: {resumen['liquidados']}\n"
            f"Pendientes: {resumen['pendientes']}\n"
        )
        if resumen["completo"]:
            QMessageBox.information(self, "Periodo Completo", msg)
        else:
            QMessageBox.warning(self, "Periodo Pendiente", msg)

    def _recalcular(self, *args):
        emp_id = self.combo_empleado.currentData()
        periodo = self.combo_periodo.currentData()
        if not emp_id or not periodo or len(periodo) < 7:
            return

        # Calcular desde asistencia
        calc = calculo_asistencia_service.calcular_bruto_periodo(emp_id, periodo)
        self._calculo = calc

        self.lbl_hs_normales.setText(f"{calc['hs_normales']} hs = $ {calc['monto_normales']:,.2f}")
        self.lbl_hs_extra.setText(f"{calc['hs_extra']} hs x{calc['mult_extra']} = $ {calc['monto_extra']:,.2f}")
        self.lbl_hs_sabado.setText(f"{calc['hs_sabado']} hs x{calc['mult_sabado']} = $ {calc['monto_sabado']:,.2f}")
        self.lbl_hs_domingo.setText(f"{calc['hs_domingo']} hs x{calc['mult_domingo']} = $ {calc['monto_domingo']:,.2f}")
        self.lbl_hs_feriado.setText(f"{calc['hs_feriado']} hs x{calc['mult_feriado']} = $ {calc['monto_feriado']:,.2f}")
        self.lbl_valor_hora.setText(f"$ {calc['valor_hora']:,.2f}")
        self.lbl_bruto.setText(f"$ {calc['bruto']:,.2f} ({calc['dias_trabajados']} d\u00edas)")

        # Calcular recibo
        basico = calc["bruto"]
        if basico <= 0:
            self.tabla_detalle.setRowCount(0)
            self.lbl_haberes.setText("Haberes: $ 0.00")
            self.lbl_deducciones.setText("Deducciones: $ 0.00")
            self.lbl_neto.setText("NETO: $ 0.00")
            return

        conceptos_ids = [cid for chk, cid in self._conceptos_checks if chk.isChecked()]
        conceptos = [c for c in self._conceptos if c.id in conceptos_ids]

        total_haberes = basico
        total_deducciones = Decimal("0")
        filas = [("Bruto por Asistencia", "Haber", basico)]

        for c in conceptos:
            if c.calculo == "por_dia" and c.monto_fijo:
                # Monto por dia trabajado
                monto = (c.monto_fijo * calc["dias_trabajados"]).quantize(Decimal("0.01"))
            elif c.porcentaje:
                monto = (basico * c.porcentaje / Decimal("100")).quantize(Decimal("0.01"))
            elif c.monto_fijo:
                monto = c.monto_fijo
            else:
                continue
            if c.tipo == "haber":
                total_haberes += monto
            else:
                total_deducciones += monto
            filas.append((c.nombre, c.tipo.capitalize(), monto))

        # Adelantos
        from services.adelanto_service import adelanto_service
        from models.adelanto import Adelanto
        from core.database import get_db
        with get_db() as db:
            pendientes = db.query(Adelanto).filter_by(empleado_id=emp_id, completado=False).all()
            desc_total = Decimal("0")
            for a in pendientes:
                cuota = a.monto_cuota
                if a.saldo_pendiente <= cuota:
                    cuota = a.saldo_pendiente
                desc_total += cuota
        if desc_total > 0:
            total_deducciones += desc_total
            filas.append(("Adelantos", "Deduccion", desc_total))

        neto = total_haberes - total_deducciones

        self.tabla_detalle.setRowCount(len(filas))
        for i, (nombre, tipo, monto) in enumerate(filas):
            self.tabla_detalle.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla_detalle.setItem(i, 1, QTableWidgetItem(tipo))
            self.tabla_detalle.setItem(i, 2, QTableWidgetItem(f"$ {monto:,.2f}"))

        self.lbl_haberes.setText(f"Haberes: $ {total_haberes:,.2f}")
        self.lbl_deducciones.setText(f"Deducciones: $ {total_deducciones:,.2f}")
        self.lbl_neto.setText(f"NETO: $ {neto:,.2f}")

    def _confirmar(self):
        emp_id = self.combo_empleado.currentData()
        periodo = self.combo_periodo.currentData()

        if not emp_id or not periodo:
            QMessageBox.warning(self, "Error", "Complet\u00e1 empleado y per\u00edodo.")
            return

        if not self._calculo or self._calculo["bruto"] <= 0:
            QMessageBox.warning(self, "Error", "No hay horas registradas para este per\u00edodo.")
            return

        neto_text = self.lbl_neto.text()
        conceptos_ids = [cid for chk, cid in self._conceptos_checks if chk.isChecked()]

        resp = QMessageBox.question(
            self, "Confirmar",
            f"\u00bfLiquidar per\u00edodo {periodo}?\n{neto_text}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        try:
            basico = self._calculo["bruto"]
            nomina_service.liquidar(emp_id, periodo, basico, conceptos_ids)
            QMessageBox.information(self, "\u00c9xito", "Liquidaci\u00f3n registrada correctamente.")
            self.liquidacion_creada.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
