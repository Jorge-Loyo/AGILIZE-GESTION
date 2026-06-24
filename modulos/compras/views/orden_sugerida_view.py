"""
Orden de Compra Sugerida Inteligente.
Analiza:
- Productos bajo stock minimo
- Velocidad de venta (salidas del ultimo mes)
- Dias de cobertura estimado
- Cantidad sugerida para reponer
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QSpinBox, QCheckBox, QGroupBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from datetime import date, timedelta


class OrdenSugeridaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sugerencias = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Orden de Compra Sugerida")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()

        btn_analizar = QPushButton("  Analizar Stock")
        btn_analizar.setIcon(qta.icon("fa5s.magic", color="#0f0f0f"))
        btn_analizar.setFixedHeight(34)
        btn_analizar.setCursor(Qt.PointingHandCursor)
        btn_analizar.clicked.connect(self._analizar)
        header.addWidget(btn_analizar)
        layout.addLayout(header)

        subtitle = QLabel(
            "Analiza el inventario y sugiere productos a reponer basandose en:\n"
            "stock actual vs minimo, velocidad de venta y dias de cobertura."
        )
        subtitle.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(subtitle)

        # Parametros
        params = QGroupBox("Parametros de Analisis")
        params.setStyleSheet("QGroupBox { font-weight: bold; font-size: 11px; padding-top: 12px; }")
        params_lay = QHBoxLayout(params)
        params_lay.setSpacing(12)

        params_lay.addWidget(QLabel("Dias de cobertura deseada:"))
        self._spin_dias = QSpinBox()
        self._spin_dias.setRange(7, 180)
        self._spin_dias.setValue(30)
        self._spin_dias.setFixedHeight(28)
        self._spin_dias.setSuffix(" dias")
        params_lay.addWidget(self._spin_dias)

        params_lay.addWidget(QLabel("Periodo de analisis:"))
        self._spin_periodo = QSpinBox()
        self._spin_periodo.setRange(7, 90)
        self._spin_periodo.setValue(30)
        self._spin_periodo.setFixedHeight(28)
        self._spin_periodo.setSuffix(" dias")
        params_lay.addWidget(self._spin_periodo)

        self._chk_solo_bajo_min = QCheckBox("Solo bajo minimo")
        self._chk_solo_bajo_min.setChecked(False)
        params_lay.addWidget(self._chk_solo_bajo_min)

        params_lay.addStretch()
        layout.addWidget(params)

        # Cards resumen
        cards = QHBoxLayout()
        cards.setSpacing(10)
        self._card_productos = self._card("Productos a Reponer", "0")
        self._card_inversion = self._card("Inversion Estimada", "$ 0")
        self._card_criticos = self._card("Criticos (stock 0)", "0")
        cards.addWidget(self._card_productos)
        cards.addWidget(self._card_inversion)
        cards.addWidget(self._card_criticos)
        cards.addStretch()
        layout.addLayout(cards)

        # Tabla
        self._tabla = QTableWidget()
        self._tabla.setColumnCount(8)
        self._tabla.setHorizontalHeaderLabels([
            "Codigo", "Producto", "Stock Actual", "Stock Min",
            "Venta/Dia", "Dias Cobertura", "Cant. Sugerida", "Costo Est."
        ])
        self._tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla.setAlternatingRowColors(True)
        self._tabla.verticalHeader().setVisible(False)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self._tabla, 1)

        # Boton generar orden
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_generar = QPushButton("  Generar Orden de Compra")
        btn_generar.setIcon(qta.icon("fa5s.file-alt", color="#0f0f0f"))
        btn_generar.setFixedHeight(36)
        btn_generar.setFixedWidth(240)
        btn_generar.setCursor(Qt.PointingHandCursor)
        btn_generar.clicked.connect(self._generar_orden)
        btn_row.addWidget(btn_generar)
        layout.addLayout(btn_row)

    def _card(self, label: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(160)
        card.setMinimumHeight(60)
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

    def _analizar(self):
        from core.database import get_db
        from models.inventario import Producto, StockDeposito, MovimientoStock
        from sqlalchemy import func

        dias_cobertura = self._spin_dias.value()
        periodo_dias = self._spin_periodo.value()
        solo_bajo_min = self._chk_solo_bajo_min.isChecked()
        fecha_inicio = date.today() - timedelta(days=periodo_dias)

        self._sugerencias = []

        with get_db() as db:
            productos = db.query(Producto).filter(Producto.activo == True).all()

            for p in productos:
                # Stock actual total
                stock_actual = db.query(func.sum(StockDeposito.cantidad)).filter(
                    StockDeposito.producto_id == p.id
                ).scalar() or 0

                # Salidas en el periodo (velocidad de venta)
                salidas = db.query(func.sum(MovimientoStock.cantidad)).filter(
                    MovimientoStock.producto_id == p.id,
                    MovimientoStock.tipo == "salida",
                    MovimientoStock.fecha >= fecha_inicio,
                ).scalar() or 0

                venta_diaria = salidas / periodo_dias if periodo_dias > 0 else 0

                # Dias de cobertura con stock actual
                cobertura = stock_actual / venta_diaria if venta_diaria > 0 else 999

                # Cantidad sugerida
                necesidad = (venta_diaria * dias_cobertura) - stock_actual
                cantidad_sugerida = max(0, int(necesidad))

                # Si stock_minimo > stock_actual, asegurar al menos llegar al minimo
                if p.stock_minimo > 0 and stock_actual < p.stock_minimo:
                    min_reponer = p.stock_minimo - stock_actual
                    cantidad_sugerida = max(cantidad_sugerida, min_reponer)

                # Filtrar
                if solo_bajo_min and stock_actual >= p.stock_minimo:
                    continue
                if cantidad_sugerida <= 0:
                    continue

                self._sugerencias.append({
                    "codigo": p.codigo,
                    "nombre": p.nombre,
                    "stock_actual": int(stock_actual),
                    "stock_minimo": p.stock_minimo,
                    "venta_diaria": round(venta_diaria, 2),
                    "cobertura": round(cobertura, 1) if cobertura < 999 else "∞",
                    "cantidad_sugerida": cantidad_sugerida,
                    "costo_unitario": p.precio_costo,
                    "costo_total": round(cantidad_sugerida * p.precio_costo, 2),
                })

        # Ordenar por cobertura (los mas urgentes primero)
        self._sugerencias.sort(key=lambda x: x["cobertura"] if isinstance(x["cobertura"], float) else 9999)
        self._actualizar_tabla()

    def _actualizar_tabla(self):
        self._tabla.setRowCount(len(self._sugerencias))
        inversion_total = 0
        criticos = 0

        for i, s in enumerate(self._sugerencias):
            self._tabla.setItem(i, 0, QTableWidgetItem(s["codigo"]))
            self._tabla.setItem(i, 1, QTableWidgetItem(s["nombre"]))

            stock_item = QTableWidgetItem(str(s["stock_actual"]))
            stock_item.setTextAlignment(Qt.AlignCenter)
            if s["stock_actual"] == 0:
                stock_item.setForeground(Qt.red)
                criticos += 1
            elif s["stock_actual"] < s["stock_minimo"]:
                stock_item.setForeground(Qt.yellow)
            self._tabla.setItem(i, 2, stock_item)

            self._tabla.setItem(i, 3, QTableWidgetItem(str(s["stock_minimo"])))

            venta_item = QTableWidgetItem(f"{s['venta_diaria']:.1f}")
            venta_item.setTextAlignment(Qt.AlignCenter)
            self._tabla.setItem(i, 4, venta_item)

            cob_item = QTableWidgetItem(str(s["cobertura"]) if s["cobertura"] != "∞" else "∞")
            cob_item.setTextAlignment(Qt.AlignCenter)
            self._tabla.setItem(i, 5, cob_item)

            cant_item = QTableWidgetItem(str(s["cantidad_sugerida"]))
            cant_item.setTextAlignment(Qt.AlignCenter)
            cant_item.setForeground(Qt.cyan)
            self._tabla.setItem(i, 6, cant_item)

            costo_item = QTableWidgetItem(f"$ {s['costo_total']:,.2f}")
            costo_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._tabla.setItem(i, 7, costo_item)

            inversion_total += s["costo_total"]

        self._card_productos._val.setText(str(len(self._sugerencias)))
        self._card_inversion._val.setText(f"$ {inversion_total:,.0f}")
        self._card_criticos._val.setText(str(criticos))
        if criticos > 0:
            self._card_criticos._val.setStyleSheet("font-size: 15px; font-weight: bold; color: #ef4444;")

    def _generar_orden(self):
        if not self._sugerencias:
            QMessageBox.information(self, "Info", "Ejecuta el analisis primero.")
            return

        resp = QMessageBox.question(
            self, "Generar Orden",
            f"Se creara una orden de compra con {len(self._sugerencias)} productos.\nContinuar?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        try:
            from services.compras_service import compras_service
            items = [
                {
                    "descripcion": f"{s['codigo']} - {s['nombre']}",
                    "cantidad": s["cantidad_sugerida"],
                    "precio_unitario": s["costo_unitario"],
                }
                for s in self._sugerencias
            ]
            compras_service.crear_orden("Orden Sugerida Automatica", items)
            QMessageBox.information(
                self, "Orden Creada",
                f"Orden de compra generada con {len(items)} productos.\n"
                f"Revise en 'Ordenes de Compra'."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
