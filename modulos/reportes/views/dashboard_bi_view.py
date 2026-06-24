from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox,
)
from PySide6.QtCore import Qt
from services.reportes_service import reportes_service


class DashboardBIView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Business Intelligence")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Indicadores clave del negocio en tiempo real")
        subtitle.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(subtitle)

        # KPI Cards - Fila 1
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self._kpi_ventas = self._card("Ventas del Mes", "$ 0")
        self._kpi_compras = self._card("Compras del Mes", "$ 0")
        self._kpi_margen = self._card("Margen", "$ 0")
        self._kpi_bancos = self._card("Saldo Bancos", "$ 0")
        row1.addWidget(self._kpi_ventas)
        row1.addWidget(self._kpi_compras)
        row1.addWidget(self._kpi_margen)
        row1.addWidget(self._kpi_bancos)
        layout.addLayout(row1)

        # KPI Cards - Fila 2
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self._kpi_cobrar = self._card("Por Cobrar", "$ 0")
        self._kpi_pagar = self._card("Por Pagar", "$ 0")
        self._kpi_inventario = self._card("Inventario", "$ 0")
        self._kpi_productos = self._card("Productos", "0")
        row2.addWidget(self._kpi_cobrar)
        row2.addWidget(self._kpi_pagar)
        row2.addWidget(self._kpi_inventario)
        row2.addWidget(self._kpi_productos)
        layout.addLayout(row2)

        # KPI Cards - Fila 3
        row3 = QHBoxLayout()
        row3.setSpacing(10)
        self._kpi_clientes = self._card("Clientes", "0")
        self._kpi_proveedores = self._card("Proveedores", "0")
        self._kpi_presupuestos = self._card("Presup. Pendientes", "0")
        self._kpi_pedidos = self._card("Pedidos Pendientes", "0")
        row3.addWidget(self._kpi_clientes)
        row3.addWidget(self._kpi_proveedores)
        row3.addWidget(self._kpi_presupuestos)
        row3.addWidget(self._kpi_pedidos)
        layout.addLayout(row3)

        # Tablas resumen
        tables_row = QHBoxLayout()
        tables_row.setSpacing(14)

        # Top clientes
        grp_cli = QGroupBox("Top Clientes")
        grp_cli.setStyleSheet("QGroupBox { font-weight: bold; font-size: 11px; padding-top: 12px; }")
        cli_lay = QVBoxLayout(grp_cli)
        self._tabla_top_cli = QTableWidget()
        self._tabla_top_cli.setColumnCount(2)
        self._tabla_top_cli.setHorizontalHeaderLabels(["Cliente", "Total"])
        self._tabla_top_cli.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tabla_top_cli.verticalHeader().setVisible(False)
        self._tabla_top_cli.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_top_cli.setMaximumHeight(150)
        cli_lay.addWidget(self._tabla_top_cli)
        tables_row.addWidget(grp_cli)

        # Ventas por mes
        grp_ventas = QGroupBox("Ventas por Mes")
        grp_ventas.setStyleSheet("QGroupBox { font-weight: bold; font-size: 11px; padding-top: 12px; }")
        ventas_lay = QVBoxLayout(grp_ventas)
        self._tabla_ventas_mes = QTableWidget()
        self._tabla_ventas_mes.setColumnCount(2)
        self._tabla_ventas_mes.setHorizontalHeaderLabels(["Mes", "Total"])
        self._tabla_ventas_mes.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tabla_ventas_mes.verticalHeader().setVisible(False)
        self._tabla_ventas_mes.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_ventas_mes.setMaximumHeight(150)
        ventas_lay.addWidget(self._tabla_ventas_mes)
        tables_row.addWidget(grp_ventas)

        layout.addLayout(tables_row)
        layout.addStretch()

    def _card(self, label: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(65)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 10px; color: #888;")
        lay.addWidget(lbl)
        val = QLabel(value)
        val.setStyleSheet("font-size: 15px; font-weight: bold; color: #D4AF37;")
        lay.addWidget(val)
        card._val = val
        return card

    def _cargar(self):
        try:
            kpis = reportes_service.kpis_generales()
            self._kpi_ventas._val.setText(f"$ {kpis['ventas_mes']:,.0f}")
            self._kpi_compras._val.setText(f"$ {kpis['compras_mes']:,.0f}")
            self._kpi_margen._val.setText(f"$ {kpis['margen_mes']:,.0f}")
            margen_color = "#10b981" if kpis['margen_mes'] >= 0 else "#ef4444"
            self._kpi_margen._val.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {margen_color};")
            self._kpi_bancos._val.setText(f"$ {kpis['saldo_bancos']:,.0f}")
            self._kpi_cobrar._val.setText(f"$ {kpis['por_cobrar']:,.0f}")
            self._kpi_pagar._val.setText(f"$ {kpis['por_pagar']:,.0f}")
            self._kpi_inventario._val.setText(f"$ {kpis['valor_inventario']:,.0f}")
            self._kpi_productos._val.setText(str(kpis['total_productos']))
            self._kpi_clientes._val.setText(str(kpis['total_clientes']))
            self._kpi_proveedores._val.setText(str(kpis['total_proveedores']))
            self._kpi_presupuestos._val.setText(str(kpis['presupuestos_pendientes']))
            self._kpi_pedidos._val.setText(str(kpis['pedidos_pendientes']))

            # Top clientes
            top = reportes_service.top_clientes()
            self._tabla_top_cli.setRowCount(len(top))
            for i, t in enumerate(top):
                self._tabla_top_cli.setItem(i, 0, QTableWidgetItem(t["nombre"]))
                val = QTableWidgetItem(f"$ {t['total']:,.0f}")
                val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._tabla_top_cli.setItem(i, 1, val)

            # Ventas por mes
            ventas_mes = reportes_service.ventas_por_mes()
            self._tabla_ventas_mes.setRowCount(len(ventas_mes))
            for i, v in enumerate(ventas_mes):
                self._tabla_ventas_mes.setItem(i, 0, QTableWidgetItem(v["mes"]))
                val = QTableWidgetItem(f"$ {v['total']:,.0f}")
                val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._tabla_ventas_mes.setItem(i, 1, val)

        except Exception:
            pass
