"""Interfaz de Facturacion Central (Administrativa / B2B).
Diseñada para control detallado: cliente, condiciones, documentos previos.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox, QDialog, QFormLayout, QComboBox,
    QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit, QGroupBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
import qtawesome as qta


class FacturacionCentralView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._cliente_id = None
        self._cliente_nombre = ""
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title = QLabel("Facturacion Central")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # === CLIENTE ===
        grp_cliente = QGroupBox("Cliente")
        grp_cliente.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 12px; }")
        cli_lay = QHBoxLayout(grp_cliente)

        cli_lay.addWidget(QLabel("Buscar:"))
        self._input_cliente = QLineEdit()
        self._input_cliente.setFixedHeight(28)
        self._input_cliente.setMaxLength(100)
        self._input_cliente.setPlaceholderText("CUIT/RIF, razon social...")
        self._input_cliente.returnPressed.connect(self._buscar_cliente)
        cli_lay.addWidget(self._input_cliente)

        btn_buscar_cli = QPushButton("Buscar")
        btn_buscar_cli.setFixedHeight(28)
        btn_buscar_cli.clicked.connect(self._buscar_cliente)
        cli_lay.addWidget(btn_buscar_cli)

        self._lbl_cliente = QLabel("Sin cliente seleccionado")
        self._lbl_cliente.setStyleSheet("font-size: 11px; color: #888;")
        cli_lay.addWidget(self._lbl_cliente)
        layout.addWidget(grp_cliente)

        # === CONDICIONES ===
        cond_row = QHBoxLayout()
        cond_row.addWidget(QLabel("Tipo:"))
        self._combo_tipo = QComboBox()
        self._combo_tipo.addItems(["A", "B", "C", "E"])
        self._combo_tipo.setFixedHeight(28)
        self._combo_tipo.setFixedWidth(60)
        cond_row.addWidget(self._combo_tipo)

        cond_row.addWidget(QLabel("Condicion:"))
        self._combo_condicion = QComboBox()
        self._combo_condicion.addItems(["Contado", "15 dias", "30 dias", "60 dias", "90 dias"])
        self._combo_condicion.setFixedHeight(28)
        cond_row.addWidget(self._combo_condicion)

        cond_row.addWidget(QLabel("Descuento %:"))
        self._spin_descuento = QDoubleSpinBox()
        self._spin_descuento.setRange(0, 100)
        self._spin_descuento.setDecimals(1)
        self._spin_descuento.setFixedHeight(28)
        self._spin_descuento.setFixedWidth(70)
        cond_row.addWidget(self._spin_descuento)

        cond_row.addStretch()

        # Importar documentos
        btn_importar_pedido = QPushButton("  Importar Pedido")
        btn_importar_pedido.setIcon(qta.icon("fa5s.file-import", color="#3b82f6"))
        btn_importar_pedido.setFixedHeight(28)
        btn_importar_pedido.clicked.connect(self._importar_pedido)
        cond_row.addWidget(btn_importar_pedido)

        btn_importar_remito = QPushButton("  Importar Remito")
        btn_importar_remito.setIcon(qta.icon("fa5s.dolly", color="#3b82f6"))
        btn_importar_remito.setFixedHeight(28)
        btn_importar_remito.clicked.connect(self._importar_remito)
        cond_row.addWidget(btn_importar_remito)
        layout.addLayout(cond_row)

        # === ITEMS ===
        items_row = QHBoxLayout()
        self._input_producto = QLineEdit()
        self._input_producto.setFixedHeight(30)
        self._input_producto.setMaxLength(100)
        self._input_producto.setPlaceholderText("Codigo o nombre de producto...")
        self._input_producto.returnPressed.connect(self._agregar_producto)
        items_row.addWidget(self._input_producto)

        items_row.addWidget(QLabel("Cant:"))
        self._spin_cant = QSpinBox()
        self._spin_cant.setRange(1, 99999)
        self._spin_cant.setValue(1)
        self._spin_cant.setFixedHeight(30)
        self._spin_cant.setFixedWidth(70)
        items_row.addWidget(self._spin_cant)

        btn_add = QPushButton("  Agregar")
        btn_add.setIcon(qta.icon("fa5s.plus", color="#10b981"))
        btn_add.setFixedHeight(30)
        btn_add.clicked.connect(self._agregar_producto)
        items_row.addWidget(btn_add)
        layout.addLayout(items_row)

        # Tabla
        self._tabla = QTableWidget()
        self._tabla.setColumnCount(6)
        self._tabla.setHorizontalHeaderLabels(["Codigo", "Descripcion", "Cant", "P.Unit", "Subtotal", ""])
        self._tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self._tabla.setColumnWidth(5, 40)
        self._tabla.setAlternatingRowColors(True)
        self._tabla.verticalHeader().setVisible(False)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._tabla, 1)

        # === TOTALES Y FACTURAR ===
        bot = QHBoxLayout()
        self._lbl_subtotal = QLabel("Subtotal: $0")
        self._lbl_subtotal.setStyleSheet("font-size: 12px; color: #888;")
        bot.addWidget(self._lbl_subtotal)
        self._lbl_descuento = QLabel("Desc: $0")
        self._lbl_descuento.setStyleSheet("font-size: 12px; color: #888;")
        bot.addWidget(self._lbl_descuento)
        self._lbl_total = QLabel("TOTAL: $0")
        self._lbl_total.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        bot.addWidget(self._lbl_total)
        bot.addStretch()

        btn_facturar = QPushButton("  Emitir Factura")
        btn_facturar.setIcon(qta.icon("fa5s.file-invoice", color="#ffffff"))
        btn_facturar.setFixedHeight(40)
        btn_facturar.setFixedWidth(200)
        btn_facturar.setStyleSheet("QPushButton { background-color: #10b981; font-size: 14px; font-weight: bold; } QPushButton:hover { background-color: #059669; }")
        btn_facturar.clicked.connect(self._facturar)
        bot.addWidget(btn_facturar)
        layout.addLayout(bot)

    def _buscar_cliente(self):
        texto = self._input_cliente.text().strip()
        if not texto:
            return
        from services.clientes import cliente_service
        clientes = cliente_service.buscar_clientes(texto)
        if not clientes:
            QMessageBox.warning(self, "No encontrado", f"Cliente '{texto}' no encontrado.")
            return
        if len(clientes) == 1:
            cli = clientes[0]
        else:
            # Mostrar selector
            dlg = QDialog(self)
            dlg.setWindowTitle("Seleccionar Cliente")
            dlg.setMinimumWidth(400)
            lay = QVBoxLayout(dlg)
            combo = QComboBox()
            for c in clientes:
                combo.addItem(f"{c.razon_social} ({c.cuit_rif})", c.id)
            lay.addWidget(combo)
            btn = QPushButton("Seleccionar")
            btn.clicked.connect(dlg.accept)
            lay.addWidget(btn)
            if dlg.exec() != QDialog.Accepted:
                return
            cli = next((c for c in clientes if c.id == combo.currentData()), clientes[0])

        self._cliente_id = cli.id
        self._cliente_nombre = cli.razon_social
        credito_info = ""
        if cli.credito_bloqueado:
            credito_info = " | ⚠️ CREDITO BLOQUEADO"
        elif cli.limite_credito > 0:
            disponible = max(0, cli.limite_credito - (cli.saldo or 0))
            credito_info = f" | Credito disp: ${disponible:,.0f}"
        self._lbl_cliente.setText(f"✓ {cli.razon_social} | {cli.cuit_rif}{credito_info}")
        self._lbl_cliente.setStyleSheet("font-size: 11px; color: #10b981;")
        # Auto-llenar condicion
        if cli.condicion_pago:
            idx = self._combo_condicion.findText(cli.condicion_pago, Qt.MatchContains)
            if idx >= 0:
                self._combo_condicion.setCurrentIndex(idx)
        if cli.descuento_default:
            self._spin_descuento.setValue(cli.descuento_default)

    def _agregar_producto(self):
        texto = self._input_producto.text().strip()
        if not texto:
            return
        from services.inventario import inventario_service
        productos = inventario_service.buscar_productos(texto)
        if not productos:
            QMessageBox.warning(self, "No encontrado", f"Producto '{texto}' no encontrado.")
            return
        p = productos[0]
        cant = self._spin_cant.value()

        # Verificar si ya existe
        for item in self._items:
            if item["codigo"] == p.codigo:
                item["cantidad"] += cant
                item["subtotal"] = item["cantidad"] * item["precio"]
                self._actualizar_tabla()
                self._input_producto.clear()
                return

        self._items.append({
            "codigo": p.codigo,
            "descripcion": f"{p.codigo} - {p.nombre}",
            "nombre": p.nombre,
            "cantidad": cant,
            "precio": p.precio_venta or 0,
            "subtotal": cant * (p.precio_venta or 0),
        })
        self._actualizar_tabla()
        self._input_producto.clear()
        self._spin_cant.setValue(1)

    def _importar_pedido(self):
        if not self._cliente_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente primero.")
            return
        from services.ventas.motor_facturacion import motor_facturacion
        pedidos = motor_facturacion.pedidos_pendientes_cliente(self._cliente_id)
        if not pedidos:
            QMessageBox.information(self, "Info", "No hay pedidos pendientes para este cliente.")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Importar Pedido")
        dlg.setMinimumWidth(400)
        lay = QVBoxLayout(dlg)
        combo = QComboBox()
        for p in pedidos:
            combo.addItem(f"Pedido #{p.numero} - {p.fecha.strftime('%d/%m/%Y')} - ${p.total:,.2f}", p.id)
        lay.addWidget(combo)
        btn = QPushButton("Importar")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)
        if dlg.exec() == QDialog.Accepted:
            items = motor_facturacion.items_desde_pedido(combo.currentData())
            for i in items:
                self._items.append({"codigo": "", "descripcion": i["descripcion"], "nombre": i["descripcion"], "cantidad": i["cantidad"], "precio": i["precio"], "subtotal": i["cantidad"] * i["precio"]})
            self._actualizar_tabla()

    def _importar_remito(self):
        if not self._cliente_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente primero.")
            return
        from services.ventas.motor_facturacion import motor_facturacion
        remitos = motor_facturacion.remitos_pendientes_cliente(self._cliente_id)
        if not remitos:
            QMessageBox.information(self, "Info", "No hay remitos pendientes para este cliente.")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Importar Remito")
        dlg.setMinimumWidth(400)
        lay = QVBoxLayout(dlg)
        combo = QComboBox()
        for r in remitos:
            combo.addItem(f"Remito #{r.numero} - {r.fecha.strftime('%d/%m/%Y')}", r.id)
        lay.addWidget(combo)
        btn = QPushButton("Importar")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)
        if dlg.exec() == QDialog.Accepted:
            items = motor_facturacion.items_desde_remito(combo.currentData())
            for i in items:
                self._items.append({"codigo": "", "descripcion": i["descripcion"], "nombre": i["descripcion"], "cantidad": i["cantidad"], "precio": i["precio"], "subtotal": i["cantidad"] * i["precio"]})
            self._actualizar_tabla()

    def _actualizar_tabla(self):
        self._tabla.setRowCount(len(self._items))
        subtotal = 0
        for i, item in enumerate(self._items):
            self._tabla.setItem(i, 0, QTableWidgetItem(item["codigo"]))
            self._tabla.setItem(i, 1, QTableWidgetItem(item["descripcion"]))
            cant_item = QTableWidgetItem(str(item["cantidad"]))
            cant_item.setTextAlignment(Qt.AlignCenter)
            self._tabla.setItem(i, 2, cant_item)
            self._tabla.setItem(i, 3, QTableWidgetItem(f"${item['precio']:,.2f}"))
            self._tabla.setItem(i, 4, QTableWidgetItem(f"${item['subtotal']:,.2f}"))
            self._tabla.setItem(i, 5, QTableWidgetItem("X"))
            subtotal += item["subtotal"]

        desc_pct = self._spin_descuento.value()
        descuento = round(subtotal * desc_pct / 100, 2)
        try:
            from services.core.empresa_service import empresa_service
            pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
            iva_pct = 16 if pais == "Venezuela" else 21
        except Exception:
            iva_pct = 21
        neto = subtotal - descuento
        iva = round(neto * iva_pct / 100, 2)
        total = neto + iva

        self._lbl_subtotal.setText(f"Subtotal: ${subtotal:,.2f}")
        self._lbl_descuento.setText(f"Desc ({desc_pct}%): -${descuento:,.2f}")
        self._lbl_total.setText(f"TOTAL: ${total:,.2f}")

    def _facturar(self):
        if not self._items:
            QMessageBox.warning(self, "Vacio", "Agregue items.")
            return
        if not self._cliente_id:
            QMessageBox.warning(self, "Sin cliente", "Seleccione un cliente.")
            return

        condicion = self._combo_condicion.currentText().lower()
        dias_map = {"contado": 0, "15 dias": 15, "30 dias": 30, "60 dias": 60, "90 dias": 90}
        dias = dias_map.get(condicion, 0)

        try:
            from services.ventas.motor_facturacion import motor_facturacion
            resultado = motor_facturacion.facturar_central(
                cliente_id=self._cliente_id,
                items=[{"descripcion": i["descripcion"], "cantidad": i["cantidad"], "precio": i["precio"]} for i in self._items],
                tipo_comprobante=self._combo_tipo.currentText(),
                condicion_pago=self._combo_condicion.currentText(),
                dias_pago=dias,
                descuento_pct=self._spin_descuento.value(),
            )
            QMessageBox.information(self, "Factura Emitida",
                f"Nro: {resultado['factura_numero']}\n"
                f"Total: ${resultado['total']:,.2f}\n"
                f"Condicion: {resultado['condicion_pago']}\n"
                f"Vencimiento: {resultado['vencimiento']}")
            self._items.clear()
            self._actualizar_tabla()
            self._cliente_id = None
            self._lbl_cliente.setText("Sin cliente seleccionado")
            self._lbl_cliente.setStyleSheet("font-size: 11px; color: #888;")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
