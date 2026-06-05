from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame,
)
from PySide6.QtCore import Qt
from decimal import Decimal
from datetime import date
from services.dashboard_service import dashboard_service
from services.calculo_asistencia_service import calculo_asistencia_service
from services.empleado_service import empleado_service


class DashboardRRHHView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar_metricas()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("Dashboard RRHH")
        title.setObjectName("title")
        layout.addWidget(title)

        self.lbl_periodo = QLabel("")
        self.lbl_periodo.setObjectName("subtitle")
        layout.addWidget(self.lbl_periodo)

        # Cards grid
        self.grid = QGridLayout()
        self.grid.setSpacing(16)

        self.card_empleados = self._create_card("0", "Empleados Activos", "#D4AF37")
        self.grid.addWidget(self.card_empleados, 0, 0)

        self.card_horas = self._create_card("0 hs", "Horas Normales (mes)", "#10b981")
        self.grid.addWidget(self.card_horas, 0, 1)

        self.card_extras = self._create_card("0 hs", "Horas Extra (mes)", "#f59e0b")
        self.grid.addWidget(self.card_extras, 0, 2)

        self.card_liquidadas = self._create_card("0", "Liquidaciones del Mes", "#6366f1")
        self.grid.addWidget(self.card_liquidadas, 1, 0)

        self.card_pendientes = self._create_card("0", "Pendientes de Liquidar", "#ef4444")
        self.grid.addWidget(self.card_pendientes, 1, 1)

        self.card_adelantos = self._create_card("$ 0", "Adelantos Pendientes", "#ec4899")
        self.grid.addWidget(self.card_adelantos, 1, 2)

        self.card_cierre = self._create_card("---", "Asistencia del Mes", "#8b5cf6")
        self.grid.addWidget(self.card_cierre, 2, 0)

        self.card_gasto = self._create_card("$ 0", "Gasto Nomina (periodo)", "#f97316")
        self.grid.addWidget(self.card_gasto, 2, 1)

        layout.addLayout(self.grid)
        layout.addStretch()

    def _create_card(self, valor: str, titulo: str, color: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumSize(200, 100)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)

        lbl_valor = QLabel(valor)
        lbl_valor.setAlignment(Qt.AlignCenter)
        lbl_valor.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {color};")
        lbl_valor.setObjectName("card_valor")
        card_layout.addWidget(lbl_valor)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 11px; color: #888888;")
        card_layout.addWidget(lbl_titulo)

        return card

    def _update_card(self, card: QFrame, valor: str):
        lbl = card.findChild(QLabel, "card_valor")
        if lbl:
            lbl.setText(valor)

    def _cargar_metricas(self):
        m = dashboard_service.obtener_metricas()
        self.lbl_periodo.setText(f"Periodo actual: {m['periodo_actual']}")

        self._update_card(self.card_empleados, str(m["empleados_activos"]))
        self._update_card(self.card_horas, f"{m['horas_normales_mes']} hs")
        self._update_card(self.card_extras, f"{m['horas_extra_mes']} hs")
        self._update_card(self.card_liquidadas, str(m["liquidaciones_mes"]))
        self._update_card(self.card_pendientes, str(m["pendientes_liquidar"]))
        self._update_card(self.card_adelantos, f"$ {m['adelantos_pendientes']:,.2f}")
        estado_cierre = "CERRADA" if m["asistencia_cerrada"] else "ABIERTA"
        self._update_card(self.card_cierre, estado_cierre)

        # Calcular gasto nomina del periodo actual
        periodo = m["periodo_actual"]
        empleados = empleado_service.listar()
        gasto_total = Decimal("0")
        for emp in empleados:
            calc = calculo_asistencia_service.calcular_bruto_periodo(emp.id, periodo)
            gasto_total += calc["bruto"]
        self._update_card(self.card_gasto, f"$ {gasto_total:,.2f}")
