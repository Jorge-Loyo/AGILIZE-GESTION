from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox, QDialog, QFormLayout, QComboBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
import qtawesome as qta


class FacturadorView(QWidget):
    volver_dashboard = Signal()
    logout_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._config = None
        self._depositos_ids = []
        self._build_login_ui()

    def _build_login_ui(self):
        """Pantalla inicial: pedir codigo de facturador."""
        self._login_widget = QWidget()
        layout = QVBoxLayout(self._login_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        lbl_title = QLabel("Facturador")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #D4AF37;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Ingrese el codigo del facturador para iniciar")
        lbl_sub.setStyleSheet("font-size: 12px; color: #888;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_sub)

        self._input_codigo = QLineEdit()
        self._input_codigo.setFixedHeight(40)
        self._input_codigo.setFixedWidth(200)
        self._input_codigo.setPlaceholderText("Ej: F01")
        self._input_codigo.setStyleSheet("font-size: 16px; text-align: center;")
        self._input_codigo.setAlignment(Qt.AlignCenter)
        self._input_codigo.returnPressed.connect(self._validar_codigo)
        layout.addWidget(self._input_codigo, alignment=Qt.AlignCenter)

        btn_ingresar = QPushButton("  Ingresar")
        btn_ingresar.setIcon(qta.icon("fa5s.sign-in-alt", color="#0f0f0f"))
        btn_ingresar.setFixedHeight(36)
        btn_ingresar.setFixedWidth(160)
        btn_ingresar.setCursor(Qt.PointingHandCursor)
        btn_ingresar.clicked.connect(self._validar_codigo)
        layout.addWidget(btn_ingresar, alignment=Qt.AlignCenter)

        self._lbl_error = QLabel("")
        self._lbl_error.setStyleSheet("font-size: 11px; color: #ef4444;")
        self._lbl_error.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._lbl_error)

        # Boton volver
        btn_volver = QPushButton("  Volver al Menu")
        btn_volver.setIcon(qta.icon("fa5s.arrow-left", color="#8a8a8a"))
        btn_volver.setStyleSheet("QPushButton { background-color: transparent; color: #8a8a8a; border: none; } QPushButton:hover { color: #F8F9FA; }")
        btn_volver.clicked.connect(self.volver_dashboard.emit)
        layout.addWidget(btn_volver, alignment=Qt.AlignCenter)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._login_widget)

    def _validar_codigo(self):
        codigo = self._input_codigo.text().strip().upper()
        if not codigo:
            self._lbl_error.setText("Ingrese un codigo")
            return

        from services.datos.facturador_config_service import facturador_config_service
        config = facturador_config_service.obtener_por_codigo(codigo)
        if not config:
            self._lbl_error.setText(f"Facturador '{codigo}' no encontrado. Configurelo en Ventas.")
            return

        self._config = config
        self._depositos_ids = facturador_config_service.get_depositos_ids(config)

        # Quitar login y mostrar POS
        self._login_widget.hide()
        self.layout().removeWidget(self._login_widget)
        self._build_pos_ui()

    def _build_pos_ui(self):
        layout = self.layout()

        pos_widget = QWidget()
        pos_layout = QVBoxLayout(pos_widget)
        pos_layout.setContentsMargins(16, 12, 16, 12)
        pos_layout.setSpacing(10)

        # Top bar
        top = QHBoxLayout()
        btn_volver = QPushButton("  Menu")
        btn_volver.setIcon(qta.icon("fa5s.arrow-left", color="#8a8a8a"))
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.setStyleSheet("QPushButton { background-color: transparent; color: #8a8a8a; border: none; padding: 8px 12px; } QPushButton:hover { color: #F8F9FA; }")
        btn_volver.clicked.connect(self.volver_dashboard.emit)
        top.addWidget(btn_volver)

        title = QLabel(f"  {self._config.nombre or self._config.codigo}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        top.addWidget(title)

        # Info depositos
        dep_info = QLabel(f"Depositos: {self._config.depositos_ids}")
        dep_info.setStyleSheet("font-size: 10px; color: #888;")
        top.addWidget(dep_info)

        top.addStretch()

        try:
            from services.core.auth_service import auth_service
            if auth_service.current_user:
                lbl_cajero = QLabel(f"Cajero: {auth_service.current_user.nombre_completo}")
                lbl_cajero.setStyleSheet("font-size: 11px; color: #888;")
                top.addWidget(lbl_cajero)
        except Exception:
            pass

        btn_logout = QPushButton("  Salir")
        btn_logout.setIcon(qta.icon("fa5s.sign-out-alt", color="#ffffff"))
        btn_logout.setStyleSheet("QPushButton { background-color: #ef4444; padding: 6px 12px; } QPushButton:hover { background-color: #dc2626; }")
        btn_logout.clicked.connect(self.logout_signal.emit)
        top.addWidget(btn_logout)
        pos_layout.addLayout(top)

        # Content
        content = QHBoxLayout()
        content.setSpacing(12)

        # Izquierda
        left = QVBoxLayout()
        left.setSpacing(8)

        search_frame = QFrame()
        search_frame.setStyleSheet("QFrame { background-color: #1a1a1a; border-radius: 8px; padding: 8px; }")
        search_lay = QHBoxLayout(search_frame)
        search_lay.setContentsMargins(8, 4, 8, 4)
        lbl_scan = QLabel()
        lbl_scan.setPixmap(qta.icon("fa5s.barcode", color="#D4AF37").pixmap(24, 24))
        search_lay.addWidget(lbl_scan)
        self._input_buscar = QLineEdit()
        self._input_buscar.setFixedHeight(36)
        self._input_buscar.setPlaceholderText("Escanear codigo o buscar producto...")
        self._input_buscar.setStyleSheet("font-size: 14px;")
        self._input_buscar.returnPressed.connect(self._buscar_producto)
        search_lay.addWidget(self._input_buscar)
        left.addWidget(search_frame)

        self._tabla = QTableWidget()
        self._tabla.setColumnCount(7)
        self._tabla.setHorizontalHeaderLabels(["Codigo", "Producto", "Deposito", "Cant", "P. Unit", "Subtotal", ""])
        self._tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self._tabla.setColumnWidth(6, 40)
        self._tabla.setAlternatingRowColors(True)
        self._tabla.verticalHeader().setVisible(False)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla.setSelectionBehavior(QTableWidget.SelectRows)
        left.addWidget(self._tabla, 1)

        content.addLayout(left, 3)

        # Derecha
        right = QVBoxLayout()
        right.setSpacing(10)

        totales_frame = QFrame()
        totales_frame.setObjectName("card")
        totales_frame.setMinimumWidth(250)
        totales_lay = QVBoxLayout(totales_frame)
        totales_lay.setContentsMargins(16, 16, 16, 16)
        totales_lay.setSpacing(8)
        self._lbl_items = QLabel("Items: 0")
        self._lbl_items.setStyleSheet("font-size: 12px; color: #888;")
        totales_lay.addWidget(self._lbl_items)
        self._lbl_subtotal = QLabel("Subtotal: $ 0.00")
        totales_lay.addWidget(self._lbl_subtotal)
        self._lbl_iva = QLabel("IVA: $ 0.00")
        totales_lay.addWidget(self._lbl_iva)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #333;")
        totales_lay.addWidget(sep)
        self._lbl_total = QLabel("TOTAL: $ 0.00")
        self._lbl_total.setStyleSheet("font-size: 22px; font-weight: bold; color: #D4AF37;")
        totales_lay.addWidget(self._lbl_total)
        right.addWidget(totales_frame)

        btn_cobrar = QPushButton("  COBRAR (F12)")
        btn_cobrar.setIcon(qta.icon("fa5s.check-circle", color="#ffffff"))
        btn_cobrar.setFixedHeight(50)
        btn_cobrar.setCursor(Qt.PointingHandCursor)
        btn_cobrar.setStyleSheet("QPushButton { background-color: #10b981; font-size: 16px; font-weight: bold; } QPushButton:hover { background-color: #059669; }")
        btn_cobrar.clicked.connect(self._cobrar)
        right.addWidget(btn_cobrar)

        btn_cancelar = QPushButton("  Cancelar Venta")
        btn_cancelar.setIcon(qta.icon("fa5s.times", color="#ffffff"))
        btn_cancelar.setFixedHeight(36)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_cancelar.clicked.connect(self._cancelar)
        right.addWidget(btn_cancelar)

        btn_eliminar = QPushButton("  Eliminar Item (Supr)")
        btn_eliminar.setFixedHeight(32)
        btn_eliminar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; }")
        btn_eliminar.clicked.connect(self._eliminar_item)
        right.addWidget(btn_eliminar)

        right.addStretch()
        lbl_atajos = QLabel("Enter=agregar | Supr=eliminar | F12=cobrar")
        lbl_atajos.setStyleSheet("font-size: 10px; color: #666;")
        right.addWidget(lbl_atajos)

        content.addLayout(right, 1)
        pos_layout.addLayout(content)

        layout.addWidget(pos_widget)

        QShortcut(QKeySequence("F12"), self, self._cobrar)
        QShortcut(QKeySequence("Delete"), self, self._eliminar_item)
        self._input_buscar.setFocus()

    def _buscar_producto(self):
        texto = self._input_buscar.text().strip()
        if not texto:
            return

        from services.inventario_service import inventario_service
        from core.database import get_db
        from models.inventario import StockDeposito, Deposito

        productos = inventario_service.buscar_productos(texto)
        if not productos:
            QMessageBox.warning(self, "No encontrado", f"Producto '{texto}' no encontrado.")
            self._input_buscar.selectAll()
            return

        p = productos[0]

        # Verificar stock en depositos asignados
        with get_db() as db:
            stocks_disponibles = []
            for dep_id in self._depositos_ids:
                sd = db.query(StockDeposito).filter(
                    StockDeposito.producto_id == p.id,
                    StockDeposito.deposito_id == dep_id,
                    StockDeposito.cantidad > 0,
                ).first()
                if sd:
                    deposito = db.get(Deposito, dep_id)
                    stocks_disponibles.append({
                        "deposito_id": dep_id,
                        "deposito_nombre": deposito.nombre if deposito else f"Dep {dep_id}",
                        "cantidad": sd.cantidad,
                    })

            if not stocks_disponibles:
                # No hay stock en ningun deposito asignado
                QMessageBox.warning(self, "Sin Stock",
                    f"'{p.nombre}' no tiene stock en los depositos asignados a este facturador.")
                self._input_buscar.selectAll()
                return

            # Si hay stock en un solo deposito, usar ese
            if len(stocks_disponibles) == 1:
                deposito_elegido = stocks_disponibles[0]
            else:
                # Pedir al cajero que elija
                deposito_elegido = self._pedir_deposito(p.nombre, stocks_disponibles)
                if not deposito_elegido:
                    self._input_buscar.selectAll()
                    return

        self._agregar_item(p.codigo, p.nombre, p.precio_venta, deposito_elegido["deposito_id"], deposito_elegido["deposito_nombre"])
        self._input_buscar.clear()
        self._input_buscar.setFocus()

    def _pedir_deposito(self, producto_nombre: str, stocks: list) -> dict | None:
        """Muestra dialog para elegir deposito cuando hay stock en multiples."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Seleccionar Deposito")
        dlg.setMinimumWidth(350)
        lay = QVBoxLayout(dlg)
        lay.setSpacing(10)

        lay.addWidget(QLabel(f"Producto: {producto_nombre}"))
        lay.addWidget(QLabel("Disponible en multiples depositos:"))

        combo = QComboBox()
        combo.setFixedHeight(30)
        for s in stocks:
            combo.addItem(f"{s['deposito_nombre']} (Stock: {s['cantidad']})", s)
        lay.addWidget(combo)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(30)
        btn_cancelar.clicked.connect(dlg.reject)
        btns.addWidget(btn_cancelar)
        btn_ok = QPushButton("Seleccionar")
        btn_ok.setFixedHeight(30)
        btn_ok.clicked.connect(dlg.accept)
        btns.addWidget(btn_ok)
        lay.addLayout(btns)

        if dlg.exec() == QDialog.Accepted:
            return combo.currentData()
        return None

    def _agregar_item(self, codigo: str, nombre: str, precio: float, deposito_id: int, deposito_nombre: str):
        # Si ya existe mismo codigo + deposito, incrementar
        for item in self._items:
            if item["codigo"] == codigo and item["deposito_id"] == deposito_id:
                item["cantidad"] += 1
                item["subtotal"] = item["cantidad"] * item["precio"]
                self._actualizar_tabla()
                return

        self._items.append({
            "codigo": codigo,
            "nombre": nombre,
            "cantidad": 1,
            "precio": precio,
            "subtotal": precio,
            "deposito_id": deposito_id,
            "deposito_nombre": deposito_nombre,
        })
        self._actualizar_tabla()

    def _eliminar_item(self):
        row = self._tabla.currentRow()
        if row >= 0 and row < len(self._items):
            self._items.pop(row)
            self._actualizar_tabla()

    def _actualizar_tabla(self):
        self._tabla.setRowCount(len(self._items))
        subtotal = 0
        total_items = 0

        for i, item in enumerate(self._items):
            self._tabla.setItem(i, 0, QTableWidgetItem(item["codigo"]))
            self._tabla.setItem(i, 1, QTableWidgetItem(item["nombre"]))
            self._tabla.setItem(i, 2, QTableWidgetItem(item["deposito_nombre"]))
            cant_item = QTableWidgetItem(str(item["cantidad"]))
            cant_item.setTextAlignment(Qt.AlignCenter)
            self._tabla.setItem(i, 3, cant_item)
            precio_item = QTableWidgetItem(f"$ {item['precio']:,.2f}")
            precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._tabla.setItem(i, 4, precio_item)
            sub_item = QTableWidgetItem(f"$ {item['subtotal']:,.2f}")
            sub_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._tabla.setItem(i, 5, sub_item)
            self._tabla.setItem(i, 6, QTableWidgetItem("X"))
            subtotal += item["subtotal"]
            total_items += item["cantidad"]

        try:
            from services.core.empresa_service import empresa_service
            pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
            iva_pct = 16 if pais == "Venezuela" else 21
        except Exception:
            iva_pct = 16

        iva = subtotal * iva_pct / 100
        total = subtotal + iva

        self._lbl_items.setText(f"Items: {total_items}")
        self._lbl_subtotal.setText(f"Subtotal: $ {subtotal:,.2f}")
        self._lbl_iva.setText(f"IVA ({iva_pct}%): $ {iva:,.2f}")
        self._lbl_total.setText(f"TOTAL: $ {total:,.2f}")

    def _cobrar(self):
        if not self._items:
            QMessageBox.information(self, "Vacio", "No hay items para cobrar.")
            return

        try:
            from services.core.empresa_service import empresa_service
            pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
            iva_pct = 16 if pais == "Venezuela" else 21
        except Exception:
            iva_pct = 16

        subtotal = sum(i["subtotal"] for i in self._items)
        total = subtotal + (subtotal * iva_pct / 100)

        resp = QMessageBox.question(self, "Confirmar Cobro", f"Total: $ {total:,.2f}\nConfirmar?", QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return

        try:
            from services.finanzas.finanzas_service import finanzas_service
            from services.inventario_service import inventario_service

            items_factura = [{"descripcion": i["nombre"], "cantidad": i["cantidad"], "precio_unitario": i["precio"]} for i in self._items]
            datos = {
                "tipo_comprobante": "factura",
                "letra": "B" if pais == "Argentina" else "",
                "tipo_entidad": "cliente",
                "entidad_nombre": "Consumidor Final",
                "impuesto_porcentaje": iva_pct,
            }
            finanzas_service.crear_factura(datos, items_factura)

            # Descontar stock de los depositos correspondientes
            for item in self._items:
                try:
                    from services.inventario_service import inventario_service
                    productos = inventario_service.buscar_productos(item["codigo"])
                    if productos:
                        inventario_service.registrar_salida(
                            productos[0].id, item["deposito_id"], item["cantidad"],
                            motivo="Venta facturador", referencia=self._config.codigo
                        )
                except Exception:
                    pass

            QMessageBox.information(self, "Venta", f"Factura emitida por $ {total:,.2f}")
            self._items.clear()
            self._actualizar_tabla()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        self._input_buscar.setFocus()

    def _cancelar(self):
        if not self._items:
            return
        resp = QMessageBox.question(self, "Cancelar", "Cancelar la venta?", QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            self._items.clear()
            self._actualizar_tabla()
            self._input_buscar.setFocus()
