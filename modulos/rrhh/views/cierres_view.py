from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QDateEdit, QComboBox,
    QMessageBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QSpinBox,
)
from PySide6.QtCore import Qt, QDate
from datetime import date
from services.rrhh.cierre_service import cierre_service
from services.rrhh.nomina_service import nomina_service
from services.core.auth_service import auth_service
from services.rrhh.periodo_service import obtener_frecuencia


class CierresAsistenciaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar_cierres()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Cierres de Asistencia")
        title.setObjectName("title")
        layout.addWidget(title)

        freq = obtener_frecuencia()
        desc = {
            "mensual": "Cierra periodos mensuales completos.",
            "quincenal": "Cierra por quincena (Q1: 1-15, Q2: 16-fin). Q1 debe cerrarse antes que Q2.",
            "semanal": "Cierra periodos semanales.",
            "diario": "Cierra periodos diarios.",
        }
        subtitle = QLabel(f"Frecuencia: {freq.upper()} — {desc.get(freq, '')}")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Form cerrar
        grp = QGroupBox("Nuevo Cierre")
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        form = QGridLayout(grp)
        form.setSpacing(10)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        hoy = date.today()

        if freq == "quincenal":
            form.addWidget(QLabel("Mes:"), 0, 0)
            self.spin_mes = QSpinBox()
            self.spin_mes.setMinimumHeight(34)
            self.spin_mes.setRange(1, 12)
            self.spin_mes.setValue(hoy.month)
            form.addWidget(self.spin_mes, 0, 1)

            form.addWidget(QLabel("Anio:"), 0, 2)
            self.spin_anio = QSpinBox()
            self.spin_anio.setMinimumHeight(34)
            self.spin_anio.setRange(2020, 2050)
            self.spin_anio.setValue(hoy.year)
            form.addWidget(self.spin_anio, 0, 3)

            form.addWidget(QLabel("Quincena:"), 1, 0)
            self.combo_quincena = QComboBox()
            self.combo_quincena.setMinimumHeight(34)
            self.combo_quincena.addItem("Q1 (1 al 15)", 1)
            self.combo_quincena.addItem("Q2 (16 al fin de mes)", 2)
            form.addWidget(self.combo_quincena, 1, 1)

            btn_cerrar = QPushButton("Cerrar Quincena")
            btn_cerrar.setMinimumHeight(36)
            btn_cerrar.clicked.connect(self._cerrar_quincenal)
            form.addWidget(btn_cerrar, 1, 3)
        else:
            form.addWidget(QLabel("Desde:"), 0, 0)
            self.input_desde = QDateEdit()
            self.input_desde.setMinimumHeight(34)
            self.input_desde.setCalendarPopup(True)
            self.input_desde.setDate(QDate(hoy.year, hoy.month, 1))
            form.addWidget(self.input_desde, 0, 1)

            form.addWidget(QLabel("Hasta:"), 0, 2)
            self.input_hasta = QDateEdit()
            self.input_hasta.setMinimumHeight(34)
            self.input_hasta.setCalendarPopup(True)
            if freq == "mensual":
                import calendar
                ultimo_dia = calendar.monthrange(hoy.year, hoy.month)[1]
                self.input_hasta.setDate(QDate(hoy.year, hoy.month, ultimo_dia))
            elif freq == "semanal":
                from datetime import timedelta
                lunes = hoy - timedelta(days=hoy.weekday())
                self.input_desde.setDate(QDate(lunes.year, lunes.month, lunes.day))
                domingo = lunes + timedelta(days=6)
                self.input_hasta.setDate(QDate(domingo.year, domingo.month, domingo.day))
            else:
                self.input_hasta.setDate(QDate(hoy.year, hoy.month, hoy.day))
            form.addWidget(self.input_hasta, 0, 3)

            btn_cerrar = QPushButton("Cerrar Periodo")
            btn_cerrar.setMinimumHeight(36)
            btn_cerrar.clicked.connect(self._cerrar_rango)
            form.addWidget(btn_cerrar, 1, 1)

        btn_reabrir = QPushButton("Reabrir Seleccionado")
        btn_reabrir.setMinimumHeight(36)
        btn_reabrir.setStyleSheet("QPushButton { background-color: #f59e0b; color: #0f0f0f; } QPushButton:hover { background-color: #d97706; }")
        btn_reabrir.clicked.connect(self._reabrir)
        form.addWidget(btn_reabrir, 1, 3 if freq != "quincenal" else 2)

        layout.addWidget(grp)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Periodo", "Desde", "Hasta", "Estado", "Fecha Cierre"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.tabla)

        # Botones abajo
        bottom = QHBoxLayout()
        bottom.addStretch()

        btn_borrar = QPushButton("Eliminar Cierre")
        btn_borrar.setMinimumHeight(34)
        btn_borrar.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_borrar.clicked.connect(self._borrar_cierre)
        bottom.addWidget(btn_borrar)

        layout.addLayout(bottom)

    def _cargar_cierres(self):
        cierres = cierre_service.listar_cierres_asistencia()
        self._cierres = cierres
        self.tabla.setRowCount(len(cierres))
        for i, c in enumerate(cierres):
            quincena_txt = f"{c.periodo} Q{c.quincena}"
            self.tabla.setItem(i, 0, QTableWidgetItem(quincena_txt))
            self.tabla.setItem(i, 1, QTableWidgetItem(c.fecha_desde.strftime("%d/%m/%Y") if c.fecha_desde else ""))
            self.tabla.setItem(i, 2, QTableWidgetItem(c.fecha_hasta.strftime("%d/%m/%Y") if c.fecha_hasta else ""))
            estado = "CERRADO" if c.cerrado else "ABIERTO"
            item_estado = QTableWidgetItem(estado)
            self.tabla.setItem(i, 3, item_estado)
            fecha = c.fecha_cierre.strftime("%d/%m/%Y %H:%M") if c.fecha_cierre else ""
            self.tabla.setItem(i, 4, QTableWidgetItem(fecha))

    def _cerrar_quincenal(self):
        mes = self.spin_mes.value()
        anio = self.spin_anio.value()
        quincena = self.combo_quincena.currentData()
        periodo = f"{anio}-{mes:02d}"

        # Validar: no cerrar si ya esta cerrada
        cierres = cierre_service.listar_cierres_asistencia()
        ya_cerrada = any(c for c in cierres if c.periodo == periodo and c.quincena == quincena and c.cerrado)
        if ya_cerrada:
            QMessageBox.warning(self, "Error", f"La quincena Q{quincena} de {periodo} ya esta cerrada.")
            return

        # Calcular rango
        import calendar
        if quincena == 1:
            desde = date(anio, mes, 1)
            hasta = date(anio, mes, 15)
        else:
            desde = date(anio, mes, 16)
            ultimo = calendar.monthrange(anio, mes)[1]
            hasta = date(anio, mes, ultimo)

        self._ejecutar_cierre(desde, hasta)

    def _cerrar_rango(self):
        desde = self.input_desde.date().toPython()
        hasta = self.input_hasta.date().toPython()

        if hasta <= desde:
            QMessageBox.warning(self, "Error", "La fecha 'Hasta' debe ser posterior a 'Desde'.")
            return

        # Verificar solapamiento
        cierres = cierre_service.listar_cierres_asistencia()
        for c in cierres:
            if c.cerrado and c.fecha_desde and c.fecha_hasta:
                if desde <= c.fecha_hasta and hasta >= c.fecha_desde:
                    QMessageBox.warning(self, "Solapamiento",
                        f"El rango se solapa con {c.periodo} Q{c.quincena} ({c.fecha_desde.strftime('%d/%m')} - {c.fecha_hasta.strftime('%d/%m/%Y')}).")
                    return

        self._ejecutar_cierre(desde, hasta)

    def _ejecutar_cierre(self, desde, hasta):
        try:
            user_id = auth_service.current_user.id if auth_service.current_user else None
            cierre_service.cerrar_asistencia_rango(desde, hasta, user_id)
            self._cargar_cierres()
            QMessageBox.information(self, "OK", f"Periodo {desde.strftime('%d/%m')} al {hasta.strftime('%d/%m/%Y')} cerrado.")
        except ValueError as e:
            QMessageBox.warning(self, "No se puede cerrar", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _reabrir(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccion", "Selecciona un cierre de la tabla.")
            return
        if row >= len(self._cierres):
            return
        cierre = self._cierres[row]

        if not cierre.cerrado:
            QMessageBox.information(self, "Info", "Este periodo ya esta abierto.")
            return

        liquidaciones = nomina_service.listar_liquidaciones(periodo=cierre.periodo)
        mensaje = f"Reabrir {cierre.periodo} Q{cierre.quincena}?"
        if liquidaciones:
            mensaje += f"\n\nATENCION: Hay {len(liquidaciones)} liquidacion(es) en este periodo."

        resp = QMessageBox.warning(self, "Confirmar reapertura", mensaje, QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            user_id = auth_service.current_user.id if auth_service.current_user else None
            cierre_service.reabrir_cierre(cierre.id, user_id)
            self._cargar_cierres()
            QMessageBox.information(self, "OK", "Periodo reabierto.")

    def _borrar_cierre(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccion", "Selecciona un cierre de la tabla.")
            return
        if row >= len(self._cierres):
            return
        cierre = self._cierres[row]

        resp = QMessageBox.warning(
            self, "Eliminar Cierre",
            f"Eliminar cierre {cierre.periodo} Q{cierre.quincena}?\nEsto no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            try:
                from core.database import get_db
                from models.cierre import CierreAsistencia
                with get_db() as db:
                    c = db.get(CierreAsistencia, cierre.id)
                    if c:
                        db.delete(c)
                self._cargar_cierres()
                QMessageBox.information(self, "OK", "Cierre eliminado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
