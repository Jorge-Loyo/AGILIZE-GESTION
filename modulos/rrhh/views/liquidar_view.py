from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QLineEdit, QPushButton, QLabel,
    QMessageBox, QGroupBox, QCheckBox, QScrollArea, QFrame,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, Signal
from decimal import Decimal
from datetime import date
from services.rrhh.nomina_service import nomina_service
from services.rrhh.empleado_service import empleado_service
from services.rrhh.calculo_asistencia_service import calculo_asistencia_service
from services.core.pais_config_service import moneda


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
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # === Header: Periodo + Empleado (siempre visible arriba) ===
        header = QHBoxLayout()
        header.setSpacing(8)
        header.addWidget(QLabel("Periodo:"))
        self.combo_periodo = QComboBox()
        self.combo_periodo.setMinimumHeight(32)
        self.combo_periodo.currentIndexChanged.connect(self._on_periodo_changed)
        header.addWidget(self.combo_periodo)
        header.addWidget(QLabel("Empleado:"))
        self.combo_empleado = QComboBox()
        self.combo_empleado.setMinimumHeight(32)
        self.combo_empleado.setMinimumWidth(280)
        self.combo_empleado.currentIndexChanged.connect(self._recalcular)
        header.addWidget(self.combo_empleado)
        btn_verificar = QPushButton("Verificar")
        btn_verificar.setMinimumHeight(32)
        btn_verificar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_verificar.clicked.connect(self._verificar_periodo)
        header.addWidget(btn_verificar)
        layout.addLayout(header)

        # === Scroll para todo el contenido ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        clayout = QVBoxLayout(content)
        clayout.setSpacing(8)
        clayout.setContentsMargins(0, 0, 0, 0)

        # === Horas Trabajadas (grid compacto) ===
        grp_asist = self._grp("Detalle de Horas")
        self.asist_layout = QGridLayout(grp_asist)
        self.asist_layout.setSpacing(4)
        self.asist_layout.setColumnStretch(1, 1)
        self.asist_layout.setColumnStretch(3, 1)

        self.lbl_hs_normales = QLabel("—")
        self.lbl_hs_extra = QLabel("—")
        self.lbl_hs_sabado = QLabel("—")
        self.lbl_hs_domingo = QLabel("—")
        self.lbl_hs_feriado = QLabel("—")
        self.lbl_valor_hora = QLabel("—")
        self.lbl_bruto = QLabel("—")
        self.lbl_bruto.setStyleSheet("font-weight: bold; color: #D4AF37; font-size: 15px;")

        for lbl in [self.lbl_hs_normales, self.lbl_hs_extra, self.lbl_hs_sabado,
                    self.lbl_hs_domingo, self.lbl_hs_feriado, self.lbl_valor_hora]:
            lbl.setStyleSheet("font-size: 12px;")

        self.asist_layout.addWidget(self.lbl_hs_normales, 0, 0, 1, 2)
        self.asist_layout.addWidget(self.lbl_hs_extra, 0, 2, 1, 2)
        self.asist_layout.addWidget(self.lbl_hs_sabado, 1, 0, 1, 2)
        self.asist_layout.addWidget(self.lbl_hs_domingo, 1, 2, 1, 2)
        self.asist_layout.addWidget(self.lbl_hs_feriado, 2, 0, 1, 2)
        self.asist_layout.addWidget(self.lbl_valor_hora, 2, 2, 1, 2)
        self.asist_layout.addWidget(self.lbl_bruto, 3, 0, 1, 4)

        clayout.addWidget(grp_asist)

        # === Checkbox feriados ===
        self.chk_feriados = QCheckBox("Incluir feriados no trabajados")
        self.chk_feriados.setStyleSheet("font-size: 13px; font-weight: bold; padding: 6px 12px; background-color: #1e1e1e; border-radius: 4px;")
        self.chk_feriados.setVisible(False)
        self.chk_feriados.stateChanged.connect(self._recalcular)
        clayout.addWidget(self.chk_feriados)

        # === Conceptos (compacto) ===
        grp_conceptos = self._grp("Conceptos")
        conceptos_layout = QVBoxLayout(grp_conceptos)
        conceptos_layout.setContentsMargins(8, 4, 8, 4)
        self._conceptos_checks: list[tuple[QCheckBox, int]] = []
        self.conceptos_container = QGridLayout()
        self.conceptos_container.setSpacing(4)
        conceptos_layout.addLayout(self.conceptos_container)
        clayout.addWidget(grp_conceptos)

        # === Detalle Recibo (sin limite de altura) ===
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
        self.tabla_detalle.setMinimumHeight(120)
        preview_layout.addWidget(self.tabla_detalle)

        totales_layout = QHBoxLayout()
        totales_layout.setSpacing(16)
        self.lbl_haberes = QLabel("Haberes: $ 0.00")
        self.lbl_haberes.setStyleSheet("font-weight: bold; color: #10b981; font-size: 13px;")
        totales_layout.addWidget(self.lbl_haberes)
        self.lbl_deducciones = QLabel("Deducciones: $ 0.00")
        self.lbl_deducciones.setStyleSheet("font-weight: bold; color: #ef4444; font-size: 13px;")
        totales_layout.addWidget(self.lbl_deducciones)
        totales_layout.addStretch()
        self.lbl_neto = QLabel("NETO: $ 0.00")
        self.lbl_neto.setStyleSheet("font-size: 18px; font-weight: bold; color: #D4AF37;")
        totales_layout.addWidget(self.lbl_neto)
        preview_layout.addLayout(totales_layout)

        clayout.addWidget(grp_preview)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # === Boton Confirmar (fijo abajo) ===
        btn_liquidar = QPushButton("Confirmar Liquidacion")
        btn_liquidar.setMinimumHeight(42)
        btn_liquidar.setStyleSheet("QPushButton { font-size: 14px; font-weight: bold; }")
        btn_liquidar.clicked.connect(self._confirmar)
        layout.addWidget(btn_liquidar)

    def _grp(self, title: str) -> QGroupBox:
        g = QGroupBox(title)
        g.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 4px; }")
        return g

    def _cargar_datos(self):
        from services.rrhh.liquidacion_pendiente_service import liquidacion_pendiente_service

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
                label += f" ({moneda()}{c.monto_fijo})"
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
        from services.rrhh.liquidacion_pendiente_service import liquidacion_pendiente_service
        periodo = self.combo_periodo.currentData()
        if not periodo:
            return

        empleados = liquidacion_pendiente_service.empleados_pendientes(periodo)
        self.combo_empleado.clear()
        empleados_sorted = sorted(empleados, key=lambda e: int(e.legajo) if e.legajo and e.legajo.isdigit() else 9999)
        for emp in empleados_sorted:
            info = liquidacion_pendiente_service.info_pendiente(emp.id, periodo)
            tipo_tag = "[M]" if emp.tipo_liquidacion == "mensual" else "[H]"
            if not info["puede_liquidar"]:
                label = f"{emp.legajo} - {emp.nombre} {emp.apellido or ''} {tipo_tag} ** {info['motivo']}"
            else:
                label = f"{emp.legajo} - {emp.nombre} {emp.apellido or ''} {tipo_tag}"
            self.combo_empleado.addItem(label, emp.id)

    def _verificar_periodo(self):
        """Muestra resumen del estado de liquidacion del periodo."""
        from services.rrhh.liquidacion_pendiente_service import liquidacion_pendiente_service
        periodo = self.combo_periodo.currentData()
        if not periodo:
            QMessageBox.information(self, "Info", "No hay periodo seleccionado.")
            return

        resumen = liquidacion_pendiente_service.resumen_periodo(periodo)
        estado = "COMPLETO" if resumen["completo"] else "PENDIENTE"
        msg = (
            f"Periodo: {resumen['periodo']}\n"
            f"Estado: {estado}\n\n"
            f"Empleados activos: {resumen['total_activos']}\n"
            f"A liquidar (hora + mensual): {resumen['total_a_liquidar']}\n"
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

        calc = calculo_asistencia_service.calcular_bruto_periodo(emp_id, periodo)
        self._calculo = calc

        if calc.get('tipo_liquidacion') == 'mensual':
            self.lbl_hs_normales.setText(f"Sueldo: $ {calc['sueldo_mensual']:,.2f} | Faltas: {calc['faltas']}")
            self.lbl_hs_extra.setText(f"Desc faltas: $ {calc['descuento_faltas']:,.2f}")
            self.lbl_hs_sabado.setText(f"Hs Extra: {calc['hs_extra']} x{calc['mult_extra']} = $ {calc['monto_extra']:,.2f}" if calc['hs_extra'] > 0 else "")
            self.lbl_hs_domingo.setText(f"Fer.trab: {calc['hs_feriado']} hs x{calc['mult_feriado']} = $ {calc['monto_feriado']:,.2f}" if calc['hs_feriado'] > 0 else "")
            self.lbl_hs_feriado.setText(f"Dias: {calc['dias_trabajados']}")
            self.lbl_valor_hora.setText("MENSUAL")
        else:
            self.lbl_hs_normales.setText(f"Normal: {calc['hs_normales']} hs = $ {calc['monto_normales']:,.2f}")
            self.lbl_hs_extra.setText(f"Extra: {calc['hs_extra']} hs x{calc['mult_extra']} = $ {calc['monto_extra']:,.2f}")
            self.lbl_hs_sabado.setText(f"Sab: {calc['hs_sabado']} hs x{calc['mult_sabado']} = $ {calc['monto_sabado']:,.2f}")
            self.lbl_hs_domingo.setText(f"Dom: {calc['hs_domingo']} hs x{calc['mult_domingo']} = $ {calc['monto_domingo']:,.2f}")
            self.lbl_hs_feriado.setText(f"Fer.trab: {calc['hs_feriado']} hs x{calc['mult_feriado']} = $ {calc['monto_feriado']:,.2f}")
            self.lbl_valor_hora.setText(f"$/h: {calc['valor_hora']:,.0f}")

        # Feriados no trabajados - AMBOS tipos de empleado
        from models.asistencia import Feriado as _Fer
        from services.rrhh.periodo_service import rango_de_periodo as _rng
        from services.rrhh.config_nomina_service import config_nomina_service as _cns
        from core.database import get_db as _gdb
        _desde, _hasta = _rng(periodo)
        with _gdb() as _db:
            _total_fer = _db.query(_Fer).filter(_Fer.fecha >= _desde, _Fer.fecha <= _hasta).count()
        _fer_trab = int(calc.get('feriados_trabajados', 0)) if calc.get('tipo_liquidacion') == 'mensual' else (1 if calc.get('hs_feriado', Decimal('0')) > 0 else 0)
        _fer_no_trab = max(0, _total_fer - _fer_trab)
        _emp = empleado_service.obtener(emp_id)
        _jornada = Decimal(str(_emp.horas_jornada)) if _emp and _emp.horas_jornada else Decimal('8')
        _hs_fer = Decimal(str(_fer_no_trab)) * _jornada
        _mult_nt = _cns.obtener('mult_feriado_no_trabajado')

        if _fer_no_trab > 0:
            self.chk_feriados.setVisible(True)
            self.chk_feriados.setText(f"Incluir {_fer_no_trab} feriado(s) no trabajado(s): {_hs_fer} hs x{_mult_nt}")
        else:
            self.chk_feriados.setVisible(False)

        bruto = calc['bruto']
        bruto_sin_feriados = bruto  # guardar antes de sumar feriados
        if self.chk_feriados.isChecked() and _fer_no_trab > 0:
            _vh = _emp.valor_hora if _emp and _emp.valor_hora else Decimal('0')
            if not _vh and calc.get('tipo_liquidacion') == 'mensual':
                _dt = calc['dias_trabajados'] + calc['faltas']
                _sd = (calc['sueldo_mensual'] / Decimal(str(_dt))).quantize(Decimal('0.01')) if _dt > 0 else Decimal('0')
                _vh = (_sd / _jornada).quantize(Decimal('0.01'))
            bruto += (_hs_fer * _vh * _mult_nt).quantize(Decimal('0.01'))

        self.lbl_bruto.setText(f"BRUTO: $ {bruto:,.2f} ({calc['dias_trabajados']} dias)")
        self._calculo['bruto'] = bruto

        # Calcular recibo
        basico_original = bruto_sin_feriados
        # Calcular monto de feriados no trabajados
        monto_feriados_nt = Decimal("0")
        if self.chk_feriados.isChecked() and _fer_no_trab > 0:
            _vh2 = _emp.valor_hora if _emp and _emp.valor_hora else Decimal('0')
            if not _vh2 and calc.get('tipo_liquidacion') == 'mensual':
                _dt2 = calc['dias_trabajados'] + calc['faltas']
                _sd2 = (calc['sueldo_mensual'] / Decimal(str(_dt2))).quantize(Decimal('0.01')) if _dt2 > 0 else Decimal('0')
                _vh2 = (_sd2 / _jornada).quantize(Decimal('0.01'))
            monto_feriados_nt = (_hs_fer * _vh2 * _mult_nt).quantize(Decimal('0.01'))

        basico = basico_original
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

        # Feriados no trabajados como concepto separado
        if monto_feriados_nt > 0:
            total_haberes += monto_feriados_nt
            filas.append((f"Feriados no trabajados ({_hs_fer} hs x{_mult_nt})", "Haber", monto_feriados_nt))

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
        from services.rrhh.adelanto_service import adelanto_service
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
            if self._calculo and self._calculo.get("tipo_liquidacion") == "mensual":
                QMessageBox.warning(self, "Error", "El sueldo mensual no esta configurado.")
            else:
                QMessageBox.warning(self, "Error", "No hay horas registradas para este periodo.")
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
