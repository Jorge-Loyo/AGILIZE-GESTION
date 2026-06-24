from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt
from services.inventario import inventario_service


class DashboardInventarioView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Dashboard de Inventario")
        title.setObjectName("title")
        layout.addWidget(title)

        # Cards
        cards = QHBoxLayout()
        cards.setSpacing(12)
        self._card_productos = self._card("Productos", "0")
        self._card_depositos = self._card("Depositos", "0")
        self._card_stock = self._card("Stock Total", "0")
        self._card_valor = self._card("Valor Inventario", "$ 0")
        self._card_mov_hoy = self._card("Mov. Hoy", "0")
        cards.addWidget(self._card_productos)
        cards.addWidget(self._card_depositos)
        cards.addWidget(self._card_stock)
        cards.addWidget(self._card_valor)
        cards.addWidget(self._card_mov_hoy)
        layout.addLayout(cards)

        # Productos bajo minimo
        lbl_alertas = QLabel("Productos bajo stock minimo")
        lbl_alertas.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(lbl_alertas)

        self.tabla_alertas = QTableWidget()
        self.tabla_alertas.setColumnCount(4)
        self.tabla_alertas.setHorizontalHeaderLabels(["Codigo", "Producto", "Stock Actual", "Stock Minimo"])
        self.tabla_alertas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_alertas.setAlternatingRowColors(True)
        self.tabla_alertas.verticalHeader().setVisible(False)
        self.tabla_alertas.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_alertas.setMaximumHeight(200)
        layout.addWidget(self.tabla_alertas)

        layout.addStretch()

    def _card(self, label: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(130)
        card.setMinimumHeight(70)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px; color: #888;")
        lay.addWidget(lbl)
        val = QLabel(value)
        val.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        lay.addWidget(val)
        card._val = val
        return card

    def _cargar(self):
        try:
            r = inventario_service.resumen()
            self._card_productos._val.setText(str(r["total_productos"]))
            self._card_depositos._val.setText(str(r["total_depositos"]))
            self._card_stock._val.setText(f"{r['total_stock']:,}")
            self._card_valor._val.setText(f"$ {r['valor_inventario']:,.0f}")
            self._card_mov_hoy._val.setText(str(r["movimientos_hoy"]))

            # Alertas
            alertas = inventario_service.productos_bajo_minimo()
            self.tabla_alertas.setRowCount(len(alertas))
            for i, a in enumerate(alertas):
                self.tabla_alertas.setItem(i, 0, QTableWidgetItem(a["producto"].codigo))
                self.tabla_alertas.setItem(i, 1, QTableWidgetItem(a["producto"].nombre))
                self.tabla_alertas.setItem(i, 2, QTableWidgetItem(str(a["stock_actual"])))
                self.tabla_alertas.setItem(i, 3, QTableWidgetItem(str(a["stock_minimo"])))
        except Exception:
            pass
