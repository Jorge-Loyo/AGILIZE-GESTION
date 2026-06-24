"""Vista POS / Punto de Venta - Interfaz rapida de mostrador."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox, QDialog, QComboBox, QCheckBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
import qtawesome as qta


class POSView(QWidget):
    def __init__(self, facturador_parent=None):
        super().__init__()
        self._parent = facturador_parent
        self._items = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Header
        top = QHBoxLayout()
        title = QLabel("Punto de Venta")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        top.addWidget(title)
        top.addStretch()
        try:
            from services.core.auth_service import auth_service
            if auth_service.current_user:
                lbl = QLabel(f"Cajero: {auth_service.current_user.nombre_completo}")
                lbl.setStyleSheet("font-size: 11px; color: #888;")
                top.addWidget(lbl)
        except Exception:
            pass
        layout.addLayout(top)

        # Busqueda
        search_frame = QFrame()
        search_frame.setStyleSheet("QFrame { background-color: #1a1a1a; border-radius: 8px; padding: 8px; }")
        search_lay = QHBoxLayout(search_frame)
        search_lay.setContentsMargins(8, 4, 8, 4)
        lbl_scan = QLabel()
        lbl_scan.setPixmap(qta.icon("fa5s.barcode", color="#D4AF37").pixmap(24, 24))
        search_lay.addWidget(lbl_scan)
        self._input_buscar = QLineEdit()
        self._input_buscar.setFixedHeight(36)
        self._input_buscar.setMaxLength(100)
        self._input_buscar.setPlaceholderText("Escanear codigo o buscar producto... (Enter para agregar)")
        self._input_buscar.setStyleSheet("font-size: 14px;")
        self._input_buscar.returnPressed.connect(self._buscar_producto)
        search_lay.addWidget(self._input_buscar)
        layout.addWidget(search_frame)

        # Content
        content = QHBoxLayout()
        content.setSpacing(12)

        # Tabla items
        self._tabla = QTableWidget()
        self._tabla.setColumnCount(6)
        self._tabla.setHorizontalHeaderLabels(["Codigo", "Producto", "Cant", "P.Unit", "Subtotal", ""])
        self._tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self._tabla.setColumnWidth(5, 40)
        self._tabla.setAlternatingRowColors(True)
        self._tabla.verticalHeader().setVisible(False)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        content.addWidget(self._tabla, 3)

        # Panel derecho
        right = QVBoxLayout()
        right.setSpacing(10)

        totales_frame = QFrame()
        totales_frame.setObjectName("card")
        totales_frame.setMinimumWidth(220)
        totales_lay = QVBoxLayout(totales_frame)
        totales_lay.setContentsMargins(12, 12, 12, 12)
        self._lbl_items = QLabel("Items: 0")
        self._lbl_items.setStyleSheet("font-size: 11px; color: #888;")
        totales_lay.addWidget(self._lbl_items)
        self._lbl_subtotal = QLabel("Subtotal: $0.00")
        totales_lay.addWidget(self._lbl_subtotal)
        self._lbl_iva = QLabel("IVA: $0.00")
        totales_lay.addWidget(self._lbl_iva)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #333;")
        totales_lay.addWidget(sep)
        self._lbl_total = QLabel("TOTAL: $0.00")
        self._lbl_total.setStyleSheet("font-size: 20px; font-weight: bold; color: #D4AF37;")
        totales_lay.addWidget(self._lbl_total)
        right.addWidget(totales_frame)

        btn_cobrar = QPushButton("  COBRAR (F12)")
        btn_cobrar.setIcon(qta.icon("fa5s.check-circle", color="#ffffff"))
        btn_cobrar.setFixedHeight(50)
        btn_cobrar.setStyleSheet("QPushButton { background-color: #10b981; font-size: 16px; font-weight: bold; } QPushButton:hover { background-color: #059669; }")
        btn_cobrar.clicked.connect(self._cobrar)
        right.addWidget(btn_cobrar)

        btn_cancelar = QPushButton("  Cancelar Venta")
        btn_cancelar.setIcon(qta.icon("fa5s.times", color="#ffffff"))
        btn_cancelar.setFixedHeight(32)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_cancelar.clicked.connect(self._cancelar)
        right.addWidget(btn_cancelar)

        btn_eliminar = QPushButton("  Eliminar Item (Supr)")
        btn_eliminar.setFixedHeight(30)
        btn_eliminar.clicked.connect(self._eliminar_item)
        right.addWidget(btn_eliminar)

        right.addStretch()
        lbl_atajos = QLabel("Enter=agregar | Supr=eliminar | F12=cobrar")
        lbl_atajos.setStyleSheet("font-size: 9px; color: #555;")
        right.addWidget(lbl_atajos)

        content.addLayout(right, 1)
        layout.addLayout(content)

        QShortcut(QKeySequence("F12"), self, self._cobrar)
        QShortcut(QKeySequence("Delete"), self, self._eliminar_item)
        self._input_buscar.setFocus()

    def _buscar_producto(self):
        texto = self._input_buscar.text().strip()
        if not texto:
            return
        from services.inventario import inventario_service
        productos = inventario_service.buscar_productos(texto)
        if not productos:
            QMessageBox.warning(self, "No encontrado", f"'{texto}' no encontrado.")
            self._input_buscar.selectAll()
            return
        p = productos[0]
        deposito_id = None
        if self._parent and self._parent._depositos_ids:
            from core.database import get_db
            from models.inventario import StockDeposito
            with get_db() as db:
                for dep_id in self._parent._depositos_ids:
                    sd = db.query(StockDeposito).filter(StockDeposito.producto_id == p.id, StockDeposito.deposito_id == dep_id, StockDeposito.cantidad > 0).first()
                    if sd:
                        deposito_id = dep_id
                        break
        self._agregar_item(p.codigo, p.nombre, p.precio_venta or 0, deposito_id)
        self._input_buscar.clear()
        self._input_buscar.setFocus()

    def _agregar_item(self, codigo, nombre, precio, deposito_id):
        for item in self._items:
            if item["codigo"] == codigo:
                item["cantidad"] += 1
                item["subtotal"] = item["cantidad"] * item["precio"]
                self._actualizar_tabla()
                return
        self._items.append({"codigo": codigo, "nombre": nombre, "cantidad": 1, "precio": precio, "subtotal": precio, "deposito_id": deposito_id})
        self._actualizar_tabla()

    def _eliminar_item(self):
        row = self._tabla.currentRow()
        if 0 <= row < len(self._items):
            self._items.pop(row)
            self._actualizar_tabla()

    def _actualizar_tabla(self):
        self._tabla.setRowCount(len(self._items))
        subtotal = 0
        total_cant = 0
        for i, item in enumerate(self._items):
            self._tabla.setItem(i, 0, QTableWidgetItem(item["codigo"]))
            self._tabla.setItem(i, 1, QTableWidgetItem(item["nombre"]))
            c = QTableWidgetItem(str(item["cantidad"]))
            c.setTextAlignment(Qt.AlignCenter)
            self._tabla.setItem(i, 2, c)
            self._tabla.setItem(i, 3, QTableWidgetItem(f"${item['precio']:,.2f}"))
            s = QTableWidgetItem(f"${item['subtotal']:,.2f}")
            s.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._tabla.setItem(i, 4, s)
            self._tabla.setItem(i, 5, QTableWidgetItem("X"))
            subtotal += item["subtotal"]
            total_cant += item["cantidad"]
        try:
            from services.core.empresa_service import empresa_service
            pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
            iva_pct = 16 if pais == "Venezuela" else 21
        except Exception:
            iva_pct = 16
        iva = subtotal * iva_pct / 100
        total = subtotal + iva
        self._lbl_items.setText(f"Items: {total_cant}")
        self._lbl_subtotal.setText(f"Subtotal: ${subtotal:,.2f}")
        self._lbl_iva.setText(f"IVA ({iva_pct}%): ${iva:,.2f}")
        self._lbl_total.setText(f"TOTAL: ${total:,.2f}")

    def _cobrar(self):
        if not self._items:
            return
        try:
            from services.core.empresa_service import empresa_service
            pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
            iva_pct = 16 if pais == "Venezuela" else 21
        except Exception:
            iva_pct = 16
        subtotal = sum(i["subtotal"] for i in self._items)
        total = subtotal + (subtotal * iva_pct / 100)

        # Modal cobro rapido
        dlg = QDialog(self)
        dlg.setWindowTitle("Cobro")
        dlg.setMinimumWidth(380)
        lay = QVBoxLayout(dlg)
        lbl_t = QLabel(f"TOTAL: ${total:,.2f}")
        lbl_t.setStyleSheet("font-size: 22px; font-weight: bold; color: #D4AF37;")
        lbl_t.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_t)

        row_m = QHBoxLayout()
        row_m.addWidget(QLabel("Medio:"))
        combo = QComboBox()
        combo.addItems(["Efectivo", "Tarjeta Debito", "Tarjeta Credito", "Transferencia"])
        combo.setFixedHeight(30)
        row_m.addWidget(combo)
        chk = QCheckBox("Pago partido")
        row_m.addWidget(chk)
        lay.addLayout(row_m)

        frame_p = QFrame()
        frame_p.setVisible(False)
        fp = QHBoxLayout(frame_p)
        fp.setContentsMargins(0, 0, 0, 0)
        fp.addWidget(QLabel("Efectivo $:"))
        inp_ef = QLineEdit()
        inp_ef.setFixedHeight(28)
        inp_ef.setMaxLength(12)
        fp.addWidget(inp_ef)
        fp.addWidget(QLabel("Tarjeta $:"))
        inp_tj = QLineEdit()
        inp_tj.setFixedHeight(28)
        inp_tj.setMaxLength(12)
        fp.addWidget(inp_tj)
        lay.addWidget(frame_p)
        chk.toggled.connect(frame_p.setVisible)

        row_r = QHBoxLayout()
        row_r.addWidget(QLabel("Recibido $:"))
        inp_rec = QLineEdit()
        inp_rec.setFixedHeight(36)
        inp_rec.setStyleSheet("font-size: 18px;")
        inp_rec.setMaxLength(15)
        inp_rec.setPlaceholderText(f"{total:,.2f}")
        row_r.addWidget(inp_rec)
        lay.addLayout(row_r)

        lbl_v = QLabel("Vuelto: $0.00")
        lbl_v.setStyleSheet("font-size: 18px; font-weight: bold; color: #10b981;")
        lbl_v.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_v)

        def upd():
            try:
                r = float(inp_rec.text().replace(",", "").replace("$", "") or "0")
                lbl_v.setText(f"Vuelto: ${max(0, r - total):,.2f}")
            except ValueError:
                pass
        inp_rec.textChanged.connect(upd)

        bot = QHBoxLayout()
        btn_c = QPushButton("Cancelar")
        btn_c.clicked.connect(dlg.reject)
        bot.addWidget(btn_c)
        btn_ok = QPushButton("  Confirmar")
        btn_ok.setIcon(qta.icon("fa5s.check", color="#fff"))
        btn_ok.setFixedHeight(36)
        btn_ok.setStyleSheet("QPushButton{background-color:#10b981;font-weight:bold;}QPushButton:hover{background-color:#059669;}")
        btn_ok.clicked.connect(dlg.accept)
        bot.addWidget(btn_ok)
        lay.addLayout(bot)

        inp_rec.setFocus()
        if dlg.exec() != QDialog.Accepted:
            return

        try:
            recibido = float(inp_rec.text().replace(",", "").replace("$", "") or str(total))
            medio = combo.currentText().lower().replace(" ", "_")
            detalle_medios = None
            if chk.isChecked():
                ef = float(inp_ef.text() or "0")
                tj = float(inp_tj.text() or "0")
                medio = "mixto"
                detalle_medios = {"efectivo": ef, "tarjeta_debito": tj}

            from services.ventas.motor_facturacion import motor_facturacion
            items_f = [{"codigo": i["codigo"], "nombre": i["nombre"], "cantidad": i["cantidad"], "precio": i["precio"], "deposito_id": i["deposito_id"]} for i in self._items]
            punto = self._parent._config.codigo if self._parent and self._parent._config else "0001"
            resultado = motor_facturacion.facturar_pos(items=items_f, medio_pago=medio, monto_recibido=recibido, punto_venta=punto)

            # Registrar en caja
            try:
                from services.ventas.caja_pos_service import caja_pos_service
                turno = caja_pos_service.turno_activo()
                if turno:
                    caja_pos_service.registrar_venta(turno.id, total, medio, referencia=resultado["factura_numero"], detalle_medios=detalle_medios)
            except Exception:
                pass

            vuelto_txt = f"\nVuelto: ${resultado['vuelto']:,.2f}" if resultado['vuelto'] > 0 else ""
            QMessageBox.information(self, "Venta OK", f"Factura: {resultado['factura_numero']}\nTotal: ${resultado['total']:,.2f}{vuelto_txt}")
            self._items.clear()
            self._actualizar_tabla()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        self._input_buscar.setFocus()

    def _cancelar(self):
        if self._items and QMessageBox.question(self, "Cancelar", "Cancelar venta?") == QMessageBox.Yes:
            self._items.clear()
            self._actualizar_tabla()
            self._input_buscar.setFocus()
