from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
)
from PySide6.QtCore import Qt
from datetime import date
from decimal import Decimal
from services.cierre_service import cierre_service
from services.calculo_asistencia_service import calculo_asistencia_service
from services.empleado_service import empleado_service
from services.nomina_service import nomina_service


class ResumenMensualView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Resumen Mensual")
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

        # Tabla resumen por empleado
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Legajo", "Empleado", "Dias Trab.", "Hs Normales", "Hs Extra", "Bruto", "Liquidado", "Estado"
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)

        # Totales
        self.lbl_totales = QLabel("")
        self.lbl_totales.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(self.lbl_totales)

    def _cargar(self):
        mes = self.spin_mes.value()
        anio = self.spin_anio.value()
        periodo = f"{anio}-{mes:02d}"

        # Estado de cierres del mes
        cierres = cierre_service.listar_cierres_asistencia()
        cierres_mes = [c for c in cierres if c.periodo == periodo and c.cerrado]
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

        # Calcular por empleado
        empleados = empleado_service.listar()
        empleados.sort(key=lambda e: int(e.legajo) if e.legajo and e.legajo.isdigit() else 9999)

        liquidaciones = nomina_service.listar_liquidaciones(periodo=periodo)
        liq_map = {l.empleado_id: l for l in liquidaciones}

        total_bruto = Decimal("0")
        total_liquidado = Decimal("0")
        filas = []

        for emp in empleados:
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
                f"$ {calc['bruto']:,.2f}",
                f"$ {liquidado:,.2f}" if liq else "-",
                estado,
            ))

        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, val in enumerate(fila):
                item = QTableWidgetItem(val)
                if fila[7] == "Pendiente":
                    item.setForeground(Qt.red) if j == 7 else None
                self.tabla.setItem(i, j, item)

        self.lbl_totales.setText(
            f"Total Bruto: $ {total_bruto:,.2f}  |  Total Liquidado: $ {total_liquidado:,.2f}  |  "
            f"Empleados: {len(filas)}"
        )
