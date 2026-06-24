"""
Reportes e Indicadores Clave (KPIs) del modulo de Compras.
- Rotacion de Stock y Reposicion (alertas bajo minimo)
- Analisis de Gastos (por proveedor, categoria, departamento)
- Cumplimiento de Proveedores (fechas, cantidades)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QTabWidget, QSpinBox, QComboBox, QMessageBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from datetime import date, timedelta


class ReportesComprasView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("Reportes e Indicadores (KPIs)")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_rotacion(), "Rotacion de Stock")
        self._tabs.addTab(self._build_gastos(), "Analisis de Gastos")
        self._tabs.addTab(self._build_cumplimiento(), "Cumplimiento Proveedores")
        layout.addWidget(self._tabs)

    # ============================
    # TAB 1: ROTACION DE STOCK
    # ============================
    def _build_rotacion(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)

        info = QLabel("Productos con stock bajo minimo o sin cobertura suficiente. Genera requerimiento directo.")
        info.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(info)

        # Cards
        cards = QHBoxLayout()
        self._card_bajo_min = self._card("Bajo Minimo", "0", "#ef4444")
        self._card_sin_stock = self._card("Sin Stock", "0", "#dc2626")
        self._card_rotacion_alta = self._card("Alta Rotacion", "0", "#10b981")
        self._card_sin_movimiento = self._card("Sin Movimiento (30d)", "0", "#f59e0b")
        cards.addWidget(self._card_bajo_min)
        cards.addWidget(self._card_sin_stock)
        cards.addWidget(self._card_rotacion_alta)
        cards.addWidget(self._card_sin_movimiento)
        cards.addStretch()
        layout.addLayout(cards)

        btn_row = QHBoxLayout()
        btn_analizar = QPushButton("  Analizar")
        btn_analizar.setIcon(qta.icon("fa5s.sync", color="#0f0f0f"))
        btn_analizar.setFixedHeight(28)
        btn_analizar.clicked.connect(self._analizar_rotacion)
        btn_row.addWidget(btn_analizar)
        btn_row.addStretch()
        btn_req = QPushButton("  Generar Requerimiento")
        btn_req.setIcon(qta.icon("fa5s.hand-paper", color="#0f0f0f"))
        btn_req.setFixedHeight(28)
        btn_req.clicked.connect(self._generar_req_rotacion)
        btn_row.addWidget(btn_req)
        layout.addLayout(btn_row)

        self._tabla_rotacion = QTableWidget()
        self._tabla_rotacion.setColumnCount(7)
        self._tabla_rotacion.setHorizontalHeaderLabels([
            "Codigo", "Producto", "Stock", "Minimo", "Consumo/Dia", "Cobertura", "Estado"
        ])
        self._tabla_rotacion.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla_rotacion.setAlternatingRowColors(True)
        self._tabla_rotacion.verticalHeader().setVisible(False)
        self._tabla_rotacion.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_rotacion.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self._tabla_rotacion, 1)

        self._analizar_rotacion()
        return w

    def _analizar_rotacion(self):
        from core.database import get_db
        from models.inventario import Producto, StockDeposito, MovimientoStock
        from sqlalchemy import func

        fecha_30 = date.today() - timedelta(days=30)
        self._datos_rotacion = []
        bajo_min = 0
        sin_stock = 0
        alta_rot = 0
        sin_mov = 0

        with get_db() as db:
            productos = db.query(Producto).filter(Producto.activo == True).all()
            for p in productos:
                stock = db.query(func.sum(StockDeposito.cantidad)).filter(
                    StockDeposito.producto_id == p.id
                ).scalar() or 0

                salidas = db.query(func.sum(MovimientoStock.cantidad)).filter(
                    MovimientoStock.producto_id == p.id,
                    MovimientoStock.tipo == "salida",
                    MovimientoStock.fecha >= fecha_30,
                ).scalar() or 0

                consumo_dia = salidas / 30.0
                cobertura = stock / consumo_dia if consumo_dia > 0 else (999 if stock > 0 else 0)

                # Estado
                if stock == 0:
                    estado = "SIN STOCK"
                    sin_stock += 1
                elif p.stock_minimo and stock < p.stock_minimo:
                    estado = "BAJO MINIMO"
                    bajo_min += 1
                elif consumo_dia > 2:
                    estado = "Alta rotacion"
                    alta_rot += 1
                elif salidas == 0:
                    estado = "Sin movimiento"
                    sin_mov += 1
                else:
                    estado = "OK"
                    continue  # No mostrar los OK

                self._datos_rotacion.append({
                    "codigo": p.codigo, "nombre": p.nombre,
                    "stock": int(stock), "minimo": p.stock_minimo or 0,
                    "consumo_dia": round(consumo_dia, 2),
                    "cobertura": round(cobertura, 1) if cobertura < 999 else "∞",
                    "estado": estado,
                })

        # Ordenar: sin stock primero, luego bajo minimo
        orden = {"SIN STOCK": 0, "BAJO MINIMO": 1, "Alta rotacion": 2, "Sin movimiento": 3}
        self._datos_rotacion.sort(key=lambda x: orden.get(x["estado"], 9))

        self._tabla_rotacion.setRowCount(len(self._datos_rotacion))
        for i, d in enumerate(self._datos_rotacion):
            self._tabla_rotacion.setItem(i, 0, QTableWidgetItem(d["codigo"]))
            self._tabla_rotacion.setItem(i, 1, QTableWidgetItem(d["nombre"]))
            stock_item = QTableWidgetItem(str(d["stock"]))
            stock_item.setTextAlignment(Qt.AlignCenter)
            self._tabla_rotacion.setItem(i, 2, stock_item)
            self._tabla_rotacion.setItem(i, 3, QTableWidgetItem(str(d["minimo"])))
            self._tabla_rotacion.setItem(i, 4, QTableWidgetItem(f"{d['consumo_dia']:.1f}"))
            cob = str(d["cobertura"]) if d["cobertura"] != "∞" else "∞"
            self._tabla_rotacion.setItem(i, 5, QTableWidgetItem(cob))
            estado_item = QTableWidgetItem(d["estado"])
            if d["estado"] == "SIN STOCK":
                estado_item.setForeground(Qt.red)
            elif d["estado"] == "BAJO MINIMO":
                estado_item.setForeground(Qt.yellow)
            elif d["estado"] == "Alta rotacion":
                estado_item.setForeground(Qt.green)
            self._tabla_rotacion.setItem(i, 6, estado_item)

        self._card_bajo_min._val.setText(str(bajo_min))
        self._card_sin_stock._val.setText(str(sin_stock))
        self._card_rotacion_alta._val.setText(str(alta_rot))
        self._card_sin_movimiento._val.setText(str(sin_mov))

    def _generar_req_rotacion(self):
        criticos = [d for d in self._datos_rotacion if d["estado"] in ("SIN STOCK", "BAJO MINIMO")]
        if not criticos:
            QMessageBox.information(self, "Info", "No hay productos criticos.")
            return
        from services.compras_service import compras_service
        from services.auth_service import auth_service
        solicitante = auth_service.current_user.nombre_completo if auth_service.current_user else ""
        items = [{"descripcion": f"{d['codigo']} - {d['nombre']}", "cantidad": max(d["minimo"] - d["stock"], 1)} for d in criticos]
        compras_service.crear_requisicion(solicitante, items)
        QMessageBox.information(self, "OK", f"Requerimiento creado con {len(items)} productos criticos.")

    # ============================
    # TAB 2: ANALISIS DE GASTOS
    # ============================
    def _build_gastos(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)

        # Filtros
        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Periodo:"))
        self._combo_periodo_gastos = QComboBox()
        self._combo_periodo_gastos.addItems(["Ultimo mes", "Ultimos 3 meses", "Ultimos 6 meses", "Ultimo ano"])
        self._combo_periodo_gastos.setFixedHeight(28)
        filtros.addWidget(self._combo_periodo_gastos)

        filtros.addWidget(QLabel("Agrupar por:"))
        self._combo_agrupacion = QComboBox()
        self._combo_agrupacion.addItems(["Proveedor", "Categoria", "Departamento"])
        self._combo_agrupacion.setFixedHeight(28)
        filtros.addWidget(self._combo_agrupacion)

        btn = QPushButton("  Generar")
        btn.setIcon(qta.icon("fa5s.chart-bar", color="#0f0f0f"))
        btn.setFixedHeight(28)
        btn.clicked.connect(self._analizar_gastos)
        filtros.addWidget(btn)
        filtros.addStretch()
        layout.addLayout(filtros)

        # Cards totales
        cards = QHBoxLayout()
        self._card_total_gastos = self._card("Total Compras", "$ 0", "#D4AF37")
        self._card_promedio = self._card("Promedio x OC", "$ 0", "#3b82f6")
        self._card_oc_count = self._card("Cant. OC", "0", "#10b981")
        cards.addWidget(self._card_total_gastos)
        cards.addWidget(self._card_promedio)
        cards.addWidget(self._card_oc_count)
        cards.addStretch()
        layout.addLayout(cards)

        # Tabla ranking
        self._tabla_gastos = QTableWidget()
        self._tabla_gastos.setColumnCount(5)
        self._tabla_gastos.setHorizontalHeaderLabels(["#", "Concepto", "Total", "% del Total", "Cant. OC"])
        self._tabla_gastos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla_gastos.setAlternatingRowColors(True)
        self._tabla_gastos.verticalHeader().setVisible(False)
        self._tabla_gastos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._tabla_gastos, 1)

        # Barra visual simple
        self._frame_barras = QFrame()
        self._frame_barras.setMaximumHeight(80)
        self._barras_layout = QVBoxLayout(self._frame_barras)
        self._barras_layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self._frame_barras)

        return w

    def _analizar_gastos(self):
        from core.database import get_db
        from models.comercial import OrdenCompra
        from sqlalchemy import func

        # Periodo
        idx = self._combo_periodo_gastos.currentIndex()
        dias = [30, 90, 180, 365][idx]
        fecha_desde = date.today() - timedelta(days=dias)
        agrupacion = self._combo_agrupacion.currentText()

        with get_db() as db:
            ordenes = db.query(OrdenCompra).filter(
                OrdenCompra.fecha >= fecha_desde,
                OrdenCompra.estado.notin_(["cancelada", "rechazada"]),
            ).all()

            total_general = sum(o.total for o in ordenes)
            cant_oc = len(ordenes)
            promedio = total_general / cant_oc if cant_oc else 0

            # Agrupar
            grupos = {}
            if agrupacion == "Proveedor":
                for o in ordenes:
                    key = o.proveedor_nombre or "(Sin proveedor)"
                    grupos[key] = grupos.get(key, 0) + o.total
            elif agrupacion == "Categoria":
                # Agrupar por descripcion de items (primera palabra como proxy de categoria)
                from models.comercial import OrdenCompraDetalle
                for o in ordenes:
                    detalles = db.query(OrdenCompraDetalle).filter(OrdenCompraDetalle.orden_id == o.id).all()
                    for d in detalles:
                        # Intentar extraer categoria del producto
                        cat = self._obtener_categoria_producto(db, d.descripcion)
                        grupos[cat] = grupos.get(cat, 0) + d.subtotal
            elif agrupacion == "Departamento":
                # Buscar departamento desde requisiciones vinculadas o usar "General"
                from models.compras import Requisicion
                for o in ordenes:
                    depto = "General"
                    # Intentar vincular con requisicion por usuario
                    if o.usuario_id:
                        req = db.query(Requisicion).filter(
                            Requisicion.usuario_id == o.usuario_id,
                            Requisicion.fecha >= fecha_desde,
                        ).first()
                        if req and req.departamento:
                            depto = req.departamento
                    grupos[depto] = grupos.get(depto, 0) + o.total

        # Ordenar por monto desc
        ranking = sorted(grupos.items(), key=lambda x: x[1], reverse=True)

        self._card_total_gastos._val.setText(f"$ {total_general:,.0f}")
        self._card_promedio._val.setText(f"$ {promedio:,.0f}")
        self._card_oc_count._val.setText(str(cant_oc))

        self._tabla_gastos.setRowCount(len(ranking))
        for i, (concepto, monto) in enumerate(ranking):
            self._tabla_gastos.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self._tabla_gastos.setItem(i, 1, QTableWidgetItem(concepto))
            monto_item = QTableWidgetItem(f"$ {monto:,.2f}")
            monto_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._tabla_gastos.setItem(i, 2, monto_item)
            pct = (monto / total_general * 100) if total_general > 0 else 0
            pct_item = QTableWidgetItem(f"{pct:.1f}%")
            pct_item.setTextAlignment(Qt.AlignCenter)
            self._tabla_gastos.setItem(i, 3, pct_item)
            # Contar OC de este grupo
            cant = sum(1 for o in ordenes if (
                (agrupacion == "Proveedor" and (o.proveedor_nombre or "(Sin proveedor)") == concepto) or
                agrupacion != "Proveedor"
            )) if agrupacion == "Proveedor" else ""
            self._tabla_gastos.setItem(i, 4, QTableWidgetItem(str(cant) if cant else ""))

        # Barras visuales
        while self._barras_layout.count():
            child = self._barras_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        top5 = ranking[:5]
        max_val = top5[0][1] if top5 else 1
        for concepto, monto in top5:
            row = QHBoxLayout()
            lbl = QLabel(concepto[:20])
            lbl.setFixedWidth(120)
            lbl.setStyleSheet("font-size: 10px; color: #aaa;")
            row.addWidget(lbl)
            pct_width = int((monto / max_val) * 300) if max_val > 0 else 0
            bar = QFrame()
            bar.setFixedHeight(14)
            bar.setFixedWidth(max(pct_width, 5))
            bar.setStyleSheet("background-color: #D4AF37; border-radius: 3px;")
            row.addWidget(bar)
            val = QLabel(f"$ {monto:,.0f}")
            val.setStyleSheet("font-size: 10px; color: #ccc;")
            row.addWidget(val)
            row.addStretch()
            container = QWidget()
            container.setLayout(row)
            self._barras_layout.addWidget(container)

    def _obtener_categoria_producto(self, db, descripcion: str) -> str:
        """Intenta obtener la categoria del producto por su descripcion/codigo."""
        from models.inventario import Producto
        codigo = descripcion.split(" - ")[0].strip() if " - " in descripcion else descripcion.split()[0]
        prod = db.query(Producto).filter(Producto.codigo == codigo).first()
        if prod and prod.categoria_id:
            from models.inventario import CategoriaProducto
            cat = db.get(CategoriaProducto, prod.categoria_id)
            return cat.nombre if cat else "Sin categoria"
        return "Sin categoria"

    # ============================
    # TAB 3: CUMPLIMIENTO PROVEEDORES
    # ============================
    def _build_cumplimiento(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)

        info = QLabel("Evalua el cumplimiento de proveedores: entregas a tiempo y cantidades correctas.")
        info.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(info)

        btn_row = QHBoxLayout()
        btn = QPushButton("  Analizar Cumplimiento")
        btn.setIcon(qta.icon("fa5s.chart-line", color="#0f0f0f"))
        btn.setFixedHeight(28)
        btn.clicked.connect(self._analizar_cumplimiento)
        btn_row.addWidget(btn)

        btn_row.addWidget(QLabel("Periodo:"))
        self._spin_dias_cumpl = QSpinBox()
        self._spin_dias_cumpl.setRange(30, 365)
        self._spin_dias_cumpl.setValue(90)
        self._spin_dias_cumpl.setSuffix(" dias")
        self._spin_dias_cumpl.setFixedHeight(28)
        btn_row.addWidget(self._spin_dias_cumpl)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._tabla_cumplimiento = QTableWidget()
        self._tabla_cumplimiento.setColumnCount(8)
        self._tabla_cumplimiento.setHorizontalHeaderLabels([
            "Proveedor", "OC Enviadas", "Recibidas", "% Cumplimiento",
            "Entregas a Tiempo", "Con Diferencia", "Calificacion", "Tendencia"
        ])
        self._tabla_cumplimiento.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tabla_cumplimiento.setAlternatingRowColors(True)
        self._tabla_cumplimiento.verticalHeader().setVisible(False)
        self._tabla_cumplimiento.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._tabla_cumplimiento, 1)

        return w

    def _analizar_cumplimiento(self):
        from core.database import get_db
        from models.comercial import OrdenCompra
        from models.compras import RecepcionCompra, RecepcionDetalle
        from models.comercial import OrdenCompraDetalle

        dias = self._spin_dias_cumpl.value()
        fecha_desde = date.today() - timedelta(days=dias)

        with get_db() as db:
            # Obtener OC del periodo
            ordenes = db.query(OrdenCompra).filter(
                OrdenCompra.fecha >= fecha_desde,
                OrdenCompra.estado.notin_(["cancelada", "rechazada", "pendiente_aprobacion"]),
            ).all()

            # Agrupar por proveedor
            proveedores = {}
            for oc in ordenes:
                prov = oc.proveedor_nombre or "(Sin nombre)"
                if prov not in proveedores:
                    proveedores[prov] = {
                        "oc_enviadas": 0, "oc_recibidas": 0,
                        "a_tiempo": 0, "con_diferencia": 0,
                    }
                proveedores[prov]["oc_enviadas"] += 1

                if oc.estado == "recibida":
                    proveedores[prov]["oc_recibidas"] += 1

                    # Verificar si recepcion tiene diferencias
                    recepcion = db.query(RecepcionCompra).filter(
                        RecepcionCompra.orden_compra_id == oc.id
                    ).first()
                    if recepcion:
                        # Comparar cantidades
                        detalles_rec = db.query(RecepcionDetalle).filter(
                            RecepcionDetalle.recepcion_id == recepcion.id
                        ).all()
                        tiene_diferencia = any(
                            d.cantidad_recibida != d.cantidad_esperada for d in detalles_rec
                        )
                        if tiene_diferencia:
                            proveedores[prov]["con_diferencia"] += 1
                        else:
                            proveedores[prov]["a_tiempo"] += 1
                    else:
                        proveedores[prov]["a_tiempo"] += 1

        # Mostrar
        ranking = sorted(proveedores.items(), key=lambda x: x[1]["oc_enviadas"], reverse=True)
        self._tabla_cumplimiento.setRowCount(len(ranking))

        for i, (prov, data) in enumerate(ranking):
            self._tabla_cumplimiento.setItem(i, 0, QTableWidgetItem(prov))
            self._tabla_cumplimiento.setItem(i, 1, QTableWidgetItem(str(data["oc_enviadas"])))
            self._tabla_cumplimiento.setItem(i, 2, QTableWidgetItem(str(data["oc_recibidas"])))

            # % cumplimiento
            pct = (data["oc_recibidas"] / data["oc_enviadas"] * 100) if data["oc_enviadas"] > 0 else 0
            pct_item = QTableWidgetItem(f"{pct:.0f}%")
            pct_item.setTextAlignment(Qt.AlignCenter)
            if pct >= 90:
                pct_item.setForeground(Qt.green)
            elif pct >= 70:
                pct_item.setForeground(Qt.yellow)
            else:
                pct_item.setForeground(Qt.red)
            self._tabla_cumplimiento.setItem(i, 3, pct_item)

            self._tabla_cumplimiento.setItem(i, 4, QTableWidgetItem(str(data["a_tiempo"])))
            dif_item = QTableWidgetItem(str(data["con_diferencia"]))
            if data["con_diferencia"] > 0:
                dif_item.setForeground(Qt.red)
            self._tabla_cumplimiento.setItem(i, 5, dif_item)

            # Calificacion
            if pct >= 90 and data["con_diferencia"] == 0:
                calif = "★★★★★"
                color = "#10b981"
            elif pct >= 80:
                calif = "★★★★"
                color = "#84cc16"
            elif pct >= 60:
                calif = "★★★"
                color = "#f59e0b"
            elif pct >= 40:
                calif = "★★"
                color = "#ef4444"
            else:
                calif = "★"
                color = "#dc2626"
            calif_item = QTableWidgetItem(calif)
            calif_item.setForeground(__import__('PySide6.QtGui', fromlist=['QColor']).QColor(color))
            self._tabla_cumplimiento.setItem(i, 6, calif_item)

            # Tendencia (simplificada)
            tendencia = "→"
            if data["oc_recibidas"] == data["oc_enviadas"] and data["con_diferencia"] == 0:
                tendencia = "↑"
            elif data["con_diferencia"] > data["a_tiempo"]:
                tendencia = "↓"
            self._tabla_cumplimiento.setItem(i, 7, QTableWidgetItem(tendencia))

    # ============================
    # UTILIDADES
    # ============================
    def _card(self, label: str, value: str, color: str = "#D4AF37") -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(140)
        card.setMinimumHeight(55)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 10px; color: #888;")
        lay.addWidget(lbl)
        val = QLabel(value)
        val.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
        lay.addWidget(val)
        card._val = val
        return card
