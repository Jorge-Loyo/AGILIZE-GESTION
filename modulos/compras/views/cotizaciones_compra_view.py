"""Vista de Cotizaciones de Compra (Sourcing) - Comparacion de proveedores."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox, QDialog, QLineEdit, QDoubleSpinBox, QSpinBox,
    QFrame, QGridLayout,
)
from PySide6.QtCore import Qt
import qtawesome as qta


class CotizacionesCompraView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Cotizaciones / Sourcing")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        header.addWidget(title)
        header.addStretch()

        btn_nueva = QPushButton("  Nueva Cotizacion")
        btn_nueva.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nueva.setFixedHeight(30)
        btn_nueva.clicked.connect(self._nueva_cotizacion)
        header.addWidget(btn_nueva)
        layout.addLayout(header)

        # Tabla cotizaciones
        self._tabla = QTableWidget()
        self._tabla.setColumnCount(6)
        self._tabla.setHorizontalHeaderLabels(["ID", "Nro", "Fecha", "Descripcion", "Estado", "Adjudicado a"])
        self._tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._tabla.setAlternatingRowColors(True)
        self._tabla.verticalHeader().setVisible(False)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla.setColumnHidden(0, True)
        self._tabla.doubleClicked.connect(self._ver_comparacion)
        layout.addWidget(self._tabla)

        bot = QHBoxLayout()
        btn_comp = QPushButton("  Comparar")
        btn_comp.setIcon(qta.icon("fa5s.balance-scale", color="#0f0f0f"))
        btn_comp.setFixedHeight(30)
        btn_comp.clicked.connect(self._ver_comparacion)
        bot.addWidget(btn_comp)

        btn_adjudicar = QPushButton("  Adjudicar")
        btn_adjudicar.setIcon(qta.icon("fa5s.trophy", color="#0f0f0f"))
        btn_adjudicar.setFixedHeight(30)
        btn_adjudicar.clicked.connect(self._adjudicar)
        bot.addWidget(btn_adjudicar)

        btn_generar_oc = QPushButton("  Generar OC")
        btn_generar_oc.setIcon(qta.icon("fa5s.clipboard-check", color="#0f0f0f"))
        btn_generar_oc.setFixedHeight(30)
        btn_generar_oc.clicked.connect(self._generar_oc)
        bot.addWidget(btn_generar_oc)
        bot.addStretch()
        layout.addLayout(bot)

    def _cargar(self):
        from services.compras.compras_service import compras_service
        cotizaciones = compras_service.listar_cotizaciones()
        self._cotizaciones = cotizaciones
        self._tabla.setRowCount(len(cotizaciones))
        for i, c in enumerate(cotizaciones):
            self._tabla.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self._tabla.setItem(i, 1, QTableWidgetItem(str(c.numero)))
            self._tabla.setItem(i, 2, QTableWidgetItem(c.fecha.strftime("%d/%m/%Y") if c.fecha else ""))
            self._tabla.setItem(i, 3, QTableWidgetItem(c.descripcion))
            estado_item = QTableWidgetItem(c.estado.capitalize())
            if c.estado == "adjudicada":
                estado_item.setForeground(Qt.green)
            self._tabla.setItem(i, 4, estado_item)
            # Proveedor adjudicado
            adj = ""
            if c.proveedor_adjudicado_id:
                try:
                    from core.database import get_db
                    from models.datos import Proveedor
                    with get_db() as db:
                        prov = db.get(Proveedor, c.proveedor_adjudicado_id)
                        if prov:
                            adj = prov.razon_social
                except Exception:
                    pass
            self._tabla.setItem(i, 5, QTableWidgetItem(adj))

    def _nueva_cotizacion(self):
        dlg = _NuevaCotizacionDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.datos()
            from services.compras.compras_service import compras_service
            compras_service.crear_cotizacion(
                descripcion=data["descripcion"],
                items=data["items"],
            )
            self._cargar()

    def _ver_comparacion(self):
        row = self._tabla.currentRow()
        if row < 0:
            return
        cot_id = int(self._tabla.item(row, 0).text())
        desc = self._tabla.item(row, 3).text()
        dlg = _ComparacionDialog(cot_id, desc, self)
        dlg.exec()

    def _adjudicar(self):
        row = self._tabla.currentRow()
        if row < 0:
            return
        cot_id = int(self._tabla.item(row, 0).text())

        # Mostrar proveedores que cotizaron
        from services.compras.compras_service import compras_service
        detalles = compras_service.obtener_cotizacion_detalles(cot_id)
        if not detalles:
            QMessageBox.warning(self, "Aviso", "No hay cotizaciones cargadas.")
            return

        # Proveedores unicos
        proveedores = {}
        for d in detalles:
            if d["proveedor_id"] not in proveedores:
                proveedores[d["proveedor_id"]] = d["proveedor"]

        dlg = QDialog(self)
        dlg.setWindowTitle("Adjudicar a Proveedor")
        dlg.setMinimumWidth(300)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Seleccionar proveedor ganador:"))
        combo = QComboBox()
        for pid, pnombre in proveedores.items():
            combo.addItem(pnombre, pid)
        lay.addWidget(combo)
        btn = QPushButton("Adjudicar")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)

        if dlg.exec() == QDialog.Accepted:
            prov_id = combo.currentData()
            compras_service.adjudicar_cotizacion(cot_id, prov_id)
            QMessageBox.information(self, "Exito", f"Cotizacion adjudicada a {combo.currentText()}")
            self._cargar()

    def _generar_oc(self):
        row = self._tabla.currentRow()
        if row < 0:
            return
        cot_id = int(self._tabla.item(row, 0).text())
        estado = self._tabla.item(row, 4).text().lower()
        if estado != "adjudicada":
            QMessageBox.warning(self, "Aviso", "Primero debes adjudicar la cotizacion.")
            return
        try:
            from services.compras.compras_service import compras_service
            compras_service.generar_oc_desde_cotizacion(cot_id)
            QMessageBox.information(self, "Exito", "Orden de Compra generada desde la cotizacion.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class _NuevaCotizacionDialog(QDialog):
    """Dialog para crear cotizacion con items de multiples proveedores."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Cotizacion (Sourcing)")
        self.setMinimumSize(800, 500)
        self._items = []
        self._proveedores = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Descripcion
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Descripcion:"))
        self._input_desc = QLineEdit()
        self._input_desc.setMaxLength(250)
        self._input_desc.setPlaceholderText("Ej: Compra materiales oficina Q1 2025")
        row1.addWidget(self._input_desc)
        layout.addLayout(row1)

        # Cargar proveedores
        try:
            from core.database import get_db
            from models.datos import Proveedor
            with get_db() as db:
                self._proveedores = [(p.id, p.razon_social) for p in
                    db.query(Proveedor).filter(Proveedor.activo == True).order_by(Proveedor.razon_social).all()]
        except Exception:
            pass

        # Agregar linea
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: #1a1a1a; border-radius: 8px; padding: 8px; }")
        flay = QVBoxLayout(frame)
        flay.addWidget(QLabel("Agregar linea de cotizacion:"))

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Proveedor:"))
        self._combo_prov = QComboBox()
        self._combo_prov.setMinimumWidth(150)
        for pid, pnombre in self._proveedores:
            self._combo_prov.addItem(pnombre, pid)
        row2.addWidget(self._combo_prov)

        row2.addWidget(QLabel("Descripcion:"))
        self._input_item = QLineEdit()
        self._input_item.setMaxLength(250)
        self._input_item.setMinimumWidth(150)
        row2.addWidget(self._input_item)

        row2.addWidget(QLabel("Cant:"))
        self._spin_cant = QSpinBox()
        self._spin_cant.setRange(1, 99999)
        self._spin_cant.setValue(1)
        self._spin_cant.setFixedWidth(60)
        row2.addWidget(self._spin_cant)

        row2.addWidget(QLabel("Precio:"))
        self._spin_precio = QDoubleSpinBox()
        self._spin_precio.setRange(0, 9999999)
        self._spin_precio.setDecimals(2)
        self._spin_precio.setFixedWidth(100)
        row2.addWidget(self._spin_precio)
        flay.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Plazo:"))
        self._input_plazo = QLineEdit()
        self._input_plazo.setMaxLength(50)
        self._input_plazo.setPlaceholderText("Ej: 5 dias")
        self._input_plazo.setFixedWidth(100)
        row3.addWidget(self._input_plazo)

        row3.addWidget(QLabel("Cond. Pago:"))
        self._input_condpago = QLineEdit()
        self._input_condpago.setMaxLength(100)
        self._input_condpago.setPlaceholderText("Ej: 30 dias")
        self._input_condpago.setFixedWidth(100)
        row3.addWidget(self._input_condpago)

        btn_add = QPushButton("  Agregar")
        btn_add.setIcon(qta.icon("fa5s.plus", color="#10b981"))
        btn_add.setFixedHeight(28)
        btn_add.clicked.connect(self._agregar_item)
        row3.addWidget(btn_add)
        row3.addStretch()
        flay.addLayout(row3)
        layout.addWidget(frame)

        # Tabla items
        self._tabla = QTableWidget()
        self._tabla.setColumnCount(6)
        self._tabla.setHorizontalHeaderLabels(["Proveedor", "Descripcion", "Cantidad", "Precio Unit.", "Total", "Plazo"])
        self._tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla.setAlternatingRowColors(True)
        self._tabla.verticalHeader().setVisible(False)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._tabla, 1)

        # Botones
        bot = QHBoxLayout()
        self._lbl_total = QLabel("0 lineas")
        self._lbl_total.setStyleSheet("color: #888;")
        bot.addWidget(self._lbl_total)
        bot.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        bot.addWidget(btn_cancel)
        btn_ok = QPushButton("  Crear Cotizacion")
        btn_ok.setIcon(qta.icon("fa5s.check", color="#0f0f0f"))
        btn_ok.setFixedHeight(32)
        btn_ok.clicked.connect(self._guardar)
        bot.addWidget(btn_ok)
        layout.addLayout(bot)

    def _agregar_item(self):
        if not self._input_item.text().strip():
            return
        self._items.append({
            "proveedor_id": self._combo_prov.currentData(),
            "proveedor_nombre": self._combo_prov.currentText(),
            "descripcion": self._input_item.text().strip(),
            "cantidad": self._spin_cant.value(),
            "precio_unitario": self._spin_precio.value(),
            "plazo_entrega": self._input_plazo.text().strip(),
            "condicion_pago": self._input_condpago.text().strip(),
        })
        self._actualizar_tabla()
        self._input_item.clear()
        self._spin_precio.setValue(0)

    def _actualizar_tabla(self):
        self._tabla.setRowCount(len(self._items))
        for i, item in enumerate(self._items):
            self._tabla.setItem(i, 0, QTableWidgetItem(item["proveedor_nombre"]))
            self._tabla.setItem(i, 1, QTableWidgetItem(item["descripcion"]))
            self._tabla.setItem(i, 2, QTableWidgetItem(str(item["cantidad"])))
            self._tabla.setItem(i, 3, QTableWidgetItem(f"$ {item['precio_unitario']:,.2f}"))
            total = item["cantidad"] * item["precio_unitario"]
            self._tabla.setItem(i, 4, QTableWidgetItem(f"$ {total:,.2f}"))
            self._tabla.setItem(i, 5, QTableWidgetItem(item["plazo_entrega"]))
        self._lbl_total.setText(f"{len(self._items)} lineas")

    def _guardar(self):
        if not self._input_desc.text().strip():
            QMessageBox.warning(self, "Error", "Ingresa una descripcion.")
            return
        if not self._items:
            QMessageBox.warning(self, "Error", "Agrega al menos una linea.")
            return
        self.accept()

    def datos(self):
        return {
            "descripcion": self._input_desc.text().strip(),
            "items": self._items,
        }


class _ComparacionDialog(QDialog):
    """Muestra comparacion lado a lado de proveedores cotizados."""
    def __init__(self, cotizacion_id, descripcion, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Comparacion: {descripcion}")
        self.setMinimumSize(800, 450)
        layout = QVBoxLayout(self)

        from services.compras.compras_service import compras_service
        detalles = compras_service.obtener_cotizacion_detalles(cotizacion_id)

        if not detalles:
            layout.addWidget(QLabel("No hay cotizaciones cargadas."))
            return

        # Agrupar por proveedor
        por_proveedor = {}
        for d in detalles:
            prov = d["proveedor"]
            if prov not in por_proveedor:
                por_proveedor[prov] = {"items": [], "total": 0}
            por_proveedor[prov]["items"].append(d)
            por_proveedor[prov]["total"] += d["total"]

        # Resumen comparativo
        resumen = QTableWidget()
        resumen.setColumnCount(4)
        resumen.setHorizontalHeaderLabels(["Proveedor", "Cant. Items", "Total", "Mejor Precio"])
        resumen.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        resumen.setAlternatingRowColors(True)
        resumen.verticalHeader().setVisible(False)
        resumen.setEditTriggers(QTableWidget.NoEditTriggers)
        resumen.setRowCount(len(por_proveedor))

        mejor_total = min(p["total"] for p in por_proveedor.values())
        for i, (prov, data) in enumerate(por_proveedor.items()):
            resumen.setItem(i, 0, QTableWidgetItem(prov))
            resumen.setItem(i, 1, QTableWidgetItem(str(len(data["items"]))))
            total_item = QTableWidgetItem(f"$ {data['total']:,.2f}")
            if data["total"] == mejor_total:
                total_item.setForeground(Qt.green)
            resumen.setItem(i, 2, total_item)
            es_mejor = "★ SI" if data["total"] == mejor_total else ""
            mejor_item = QTableWidgetItem(es_mejor)
            mejor_item.setTextAlignment(Qt.AlignCenter)
            if es_mejor:
                mejor_item.setForeground(Qt.green)
            resumen.setItem(i, 3, mejor_item)

        resumen.setMaximumHeight(120)
        layout.addWidget(QLabel("Resumen Comparativo:"))
        layout.addWidget(resumen)

        # Detalle completo
        layout.addWidget(QLabel("Detalle por linea:"))
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels(["Proveedor", "Descripcion", "Cant", "Precio", "Total", "Plazo", "Cond. Pago"])
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tabla.setAlternatingRowColors(True)
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setRowCount(len(detalles))
        for i, d in enumerate(detalles):
            tabla.setItem(i, 0, QTableWidgetItem(d["proveedor"]))
            tabla.setItem(i, 1, QTableWidgetItem(d["descripcion"]))
            tabla.setItem(i, 2, QTableWidgetItem(str(d["cantidad"])))
            tabla.setItem(i, 3, QTableWidgetItem(f"$ {d['precio_unitario']:,.2f}"))
            tabla.setItem(i, 4, QTableWidgetItem(f"$ {d['total']:,.2f}"))
            tabla.setItem(i, 5, QTableWidgetItem(d["plazo_entrega"]))
            tabla.setItem(i, 6, QTableWidgetItem(d["condicion_pago"]))
        layout.addWidget(tabla, 1)

        btn = QPushButton("Cerrar")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)
