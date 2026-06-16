from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QComboBox,
)
from PySide6.QtCore import Qt
from decimal import Decimal
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
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("Dashboard RRHH")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()

        header.addWidget(QLabel("Periodo:"))
        self.combo_periodo = QComboBox()
        self.combo_periodo.setMinimumHeight(34)
        self.combo_periodo.setMinimumWidth(140)
        self.combo_periodo.currentIndexChanged.connect(self._cargar_metricas)
        header.addWidget(self.combo_periodo)

        btn_refresh = QPushButton("  Actualizar")
        btn_refresh.setMinimumHeight(34)
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_refresh.clicked.connect(self._refrescar)
        header.addWidget(btn_refresh)
        layout.addLayout(header)

        # Subtitulo periodo
        self.lbl_periodo = QLabel("")
        self.lbl_periodo.setObjectName("subtitle")
        layout.addWidget(self.lbl_periodo)

        # === CARDS DEL PERIODO ===
        lbl_sec1 = QLabel("Indicadores del Periodo")
        lbl_sec1.setStyleSheet("font-size: 13px; font-weight: bold; color: #D4AF37; margin-top: 4px;")
        layout.addWidget(lbl_sec1)

        self.grid = QGridLayout()
        self.grid.setSpacing(12)

        self.card_empleados = self._create_card("0", "Empleados Activos", "#D4AF37")
        self.grid.addWidget(self.card_empleados, 0, 0)

        self.card_horas = self._create_card("0 hs", "Horas Normales", "#10b981")
        self.grid.addWidget(self.card_horas, 0, 1)

        self.card_extras = self._create_card("0 hs", "Horas Extra", "#f59e0b")
        self.grid.addWidget(self.card_extras, 0, 2)

        self.card_liquidadas = self._create_card("0", "Liquidaciones", "#6366f1")
        self.grid.addWidget(self.card_liquidadas, 0, 3)

        self.card_pendientes = self._create_card("0", "Pendientes Liquidar", "#ef4444")
        self.grid.addWidget(self.card_pendientes, 1, 0)

        self.card_adelantos = self._create_card("$ 0", "Adelantos Pendientes", "#ec4899")
        self.grid.addWidget(self.card_adelantos, 1, 1)

        self.card_cierre = self._create_card("---", "Estado Asistencia", "#8b5cf6")
        self.grid.addWidget(self.card_cierre, 1, 2)

        self.card_gasto = self._create_card("$ 0", "Gasto Nomina", "#f97316")
        self.grid.addWidget(self.card_gasto, 1, 3)

        layout.addLayout(self.grid)

        # === METRICAS GLOBALES ===
        lbl_sec2 = QLabel("Metricas Globales")
        lbl_sec2.setStyleSheet("font-size: 13px; font-weight: bold; color: #D4AF37; margin-top: 8px;")
        layout.addWidget(lbl_sec2)

        self.grid_global = QHBoxLayout()
        self.grid_global.setSpacing(12)

        self.gcard_empleados = self._create_mini_card("0", "Total Empleados")
        self.grid_global.addWidget(self.gcard_empleados)

        self.gcard_inactivos = self._create_mini_card("0", "Inactivos")
        self.grid_global.addWidget(self.gcard_inactivos)

        self.gcard_liquidaciones = self._create_mini_card("0", "Liquidaciones Totales")
        self.grid_global.addWidget(self.gcard_liquidaciones)

        self.gcard_horas = self._create_mini_card("0", "Hs Totales Registradas")
        self.grid_global.addWidget(self.gcard_horas)

        self.gcard_cierres = self._create_mini_card("0", "Periodos Cerrados")
        self.grid_global.addWidget(self.gcard_cierres)

        layout.addLayout(self.grid_global)

        # Notificaciones
        self.notif_layout = QVBoxLayout()
        self.notif_layout.setSpacing(6)
        layout.addLayout(self.notif_layout)

        layout.addStretch()

        # Cargar periodos en combo
        self._cargar_periodos()

    def _create_card(self, valor: str, titulo: str, color: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumSize(160, 85)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setContentsMargins(8, 8, 8, 8)

        lbl_valor = QLabel(valor)
        lbl_valor.setAlignment(Qt.AlignCenter)
        lbl_valor.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
        lbl_valor.setObjectName("card_valor")
        card_layout.addWidget(lbl_valor)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 10px; color: #888888;")
        card_layout.addWidget(lbl_titulo)

        return card

    def _create_mini_card(self, valor: str, titulo: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(60)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setContentsMargins(6, 6, 6, 6)

        lbl_valor = QLabel(valor)
        lbl_valor.setAlignment(Qt.AlignCenter)
        lbl_valor.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8F9FA;")
        lbl_valor.setObjectName("card_valor")
        card_layout.addWidget(lbl_valor)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 9px; color: #888888;")
        card_layout.addWidget(lbl_titulo)

        return card

    def _update_card(self, card: QFrame, valor: str):
        lbl = card.findChild(QLabel, "card_valor")
        if lbl:
            lbl.setText(valor)

    def _cargar_periodos(self):
        self.combo_periodo.blockSignals(True)
        self.combo_periodo.clear()
        periodos = dashboard_service.listar_periodos_disponibles()
        for p in periodos:
            self.combo_periodo.addItem(p, p)
        self.combo_periodo.blockSignals(False)

    def _refrescar(self):
        self._cargar_periodos()
        self._cargar_metricas()

    def _cargar_metricas(self):
        periodo = self.combo_periodo.currentData()
        if not periodo:
            periodo = None

        m = dashboard_service.obtener_metricas(periodo)
        self.lbl_periodo.setText(f"Periodo seleccionado: {m['periodo_actual']}")

        self._update_card(self.card_empleados, str(m["empleados_activos"]))
        self._update_card(self.card_horas, f"{m['horas_normales_mes']} hs")
        self._update_card(self.card_extras, f"{m['horas_extra_mes']} hs")
        self._update_card(self.card_liquidadas, str(m["liquidaciones_mes"]))
        self._update_card(self.card_pendientes, str(m["pendientes_liquidar"]))
        self._update_card(self.card_adelantos, f"$ {m['adelantos_pendientes']:,.2f}")
        estado_cierre = "CERRADA" if m["asistencia_cerrada"] else "ABIERTA"
        self._update_card(self.card_cierre, estado_cierre)

        # Gasto nomina del periodo
        empleados = empleado_service.listar()
        gasto_total = Decimal("0")
        for emp in empleados:
            calc = calculo_asistencia_service.calcular_bruto_periodo(emp.id, m["periodo_actual"])
            gasto_total += calc["bruto"]
        self._update_card(self.card_gasto, f"$ {gasto_total:,.2f}")

        # Metricas globales
        g = dashboard_service.obtener_metricas_globales()
        self._update_card(self.gcard_empleados, str(g["total_empleados"]))
        self._update_card(self.gcard_inactivos, str(g["total_inactivos"]))
        self._update_card(self.gcard_liquidaciones, str(g["total_liquidaciones"]))
        total_hs = float(g["total_horas_normales"]) + float(g["total_horas_extra"])
        self._update_card(self.gcard_horas, f"{total_hs:.0f} hs")
        self._update_card(self.gcard_cierres, str(g["periodos_cerrados"]))

        # Notificaciones
        self._cargar_notificaciones(m)

    def _cargar_notificaciones(self, metricas):
        while self.notif_layout.count():
            item = self.notif_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        alertas = []

        from core.database import get_db
        from models.asistencia import Asistencia
        with get_db() as db:
            incompletos = db.query(Asistencia).filter(Asistencia.incompleto == True).count()
        if incompletos > 0:
            alertas.append(("error", f"{incompletos} registro(s) de asistencia incompleto(s) - completar antes de cerrar"))

        sin_valor = [e for e in empleado_service.listar() if (not e.valor_hora or e.valor_hora == 0) and e.tipo_liquidacion == "por_hora"]
        if sin_valor:
            alertas.append(("warning", f"{len(sin_valor)} empleado(s) por hora sin valor hora configurado"))

        if metricas["pendientes_liquidar"] > 0:
            alertas.append(("info", f"{metricas['pendientes_liquidar']} empleado(s) pendiente(s) de liquidar en {metricas['periodo_actual']}"))

        if not alertas:
            alertas.append(("success", "Todo en orden - sin alertas pendientes"))

        for tipo, msg in alertas:
            lbl = QLabel(f"  {msg}")
            styles = {
                "error": "background-color: #dc2626; color: #ffffff; border-left: 4px solid #991b1b;",
                "warning": "background-color: #d97706; color: #ffffff; border-left: 4px solid #92400e;",
                "info": "background-color: #2563eb; color: #ffffff; border-left: 4px solid #1e40af;",
                "success": "background-color: #16a34a; color: #ffffff; border-left: 4px solid #166534;",
            }
            style = styles.get(tipo, "background-color: #444; color: #fff;")
            lbl.setStyleSheet(f"{style} padding: 10px 14px; border-radius: 4px; font-size: 13px; font-weight: bold;")
            self.notif_layout.addWidget(lbl)

    def showEvent(self, event):
        super().showEvent(event)
        self._cargar_metricas()
