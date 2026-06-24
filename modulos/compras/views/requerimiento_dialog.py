"""
Dialog para crear nuevo Requerimiento de Compra.
Permite buscar productos de la BD con info de stock, ultimo precio de compra/venta.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QSpinBox, QMessageBox, QFrame, QComboBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta


class RequerimientoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Requerimiento de Compra")
        self.setMinimumSize(900, 600)
        self._items = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QHBoxLayout()
        title = QLabel("Nuevo Requerimiento")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Sucursal + Departamento + Tipo de compra
        sol_row = QHBoxLayout()

        sol_row.addWidget(QLabel("Sucursal:"))
        self._combo_sucursal = QComboBox()
        self._combo_sucursal.setFixedHeight(28)
        self._combo_sucursal.setMinimumWidth(140)
        self._combo_sucursal.addItem("General", None)
        try:
            from core.database import get_db
            from models.sucursal import Sucursal
            with get_db() as db:
                for s in db.query(Sucursal).filter(Sucursal.activo == True).order_by(Sucursal.nombre).all():
                    self._combo_sucursal.addItem(s.nombre, s.id)
        except Exception:
            pass
        sol_row.addWidget(self._combo_sucursal)

        sol_row.addWidget(QLabel("Departamento:"))
        self._combo_depto = QComboBox()
        self._combo_depto.setFixedHeight(28)
        self._combo_depto.setMinimumWidth(140)
        self._combo_depto.addItem("-- Seleccionar --", None)
        try:
            from core.database import get_db
            from models.empleado import Departamento
            with get_db() as db:
                for d in db.query(Departamento).filter(Departamento.activo == True).order_by(Departamento.nombre).all():
                    self._combo_depto.addItem(d.nombre, d.id)
        except Exception:
            pass
        sol_row.addWidget(self._combo_depto)

        sol_row.addWidget(QLabel("Tipo de Compra:"))
        self._combo_tipo_compra = QComboBox()
        self._combo_tipo_compra.setFixedHeight(28)
        self._combo_tipo_compra.setMinimumWidth(140)
        self._combo_tipo_compra.addItem("-- Seleccionar --", None)
        try:
            from core.database import get_db
            from models.compras import TipoCompra
            with get_db() as db:
                for tc in db.query(TipoCompra).filter(TipoCompra.activo == True).order_by(TipoCompra.nombre).all():
                    self._combo_tipo_compra.addItem(tc.nombre, tc.id)
        except Exception:
            pass
        sol_row.addWidget(self._combo_tipo_compra)
        sol_row.addStretch()
        layout.addLayout(sol_row)

        # === Busqueda de producto ===
        search_frame = QFrame()
        search_frame.setStyleSheet("QFrame { background-color: #1a1a1a; border-radius: 8px; padding: 8px; }")
        search_lay = QVBoxLayout(search_frame)
        search_lay.setSpacing(6)

        lbl_buscar = QLabel("Buscar Producto")
        lbl_buscar.setStyleSheet("font-weight: bold; font-size: 12px;")
        search_lay.addWidget(lbl_buscar)

        search_row = QHBoxLayout()
        self._input_buscar = QLineEdit()
        self._input_buscar.setFixedHeight(30)
        self._input_buscar.setMaxLength(100)
        self._input_buscar.setPlaceholderText("Buscar por codigo o nombre de producto...")
        self._input_buscar.returnPressed.connect(self._buscar_producto)
        search_row.addWidget(self._input_buscar)
        btn_buscar = QPushButton("  Buscar")
        btn_buscar.setIcon(qta.icon("fa5s.search", color="#0f0f0f"))
        btn_buscar.setFixedHeight(30)
        btn_buscar.clicked.connect(self._buscar_producto)
        search_row.addWidget(btn_buscar)
        search_lay.addLayout(search_row)

        # Tabla de resultados de busqueda
        self._tabla_busqueda = QTableWidget()
        self._tabla_busqueda.setColumnCount(7)
        self._tabla_busqueda.setHorizontalHeaderLabels([
            "Codigo", "Producto", "Stock", "Ult. Compra $", "Fecha Compra",
            "Ult. Venta $", "Fecha Venta"
        ])
        self._tabla_busqueda.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla_busqueda.setAlternatingRowColors(True)
        self._tabla_busqueda.verticalHeader().setVisible(False)
        self._tabla_busqueda.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_busqueda.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_busqueda.setMaximumHeight(150)
        self._tabla_busqueda.doubleClicked.connect(self._agregar_desde_busqueda)
        search_lay.addWidget(self._tabla_busqueda)

        # Agregar manual
        add_row = QHBoxLayout()
        add_row.addWidget(QLabel("Cant:"))
        self._spin_cant = QSpinBox()
        self._spin_cant.setRange(1, 99999)
        self._spin_cant.setValue(1)
        self._spin_cant.setFixedHeight(28)
        self._spin_cant.setFixedWidth(70)
        add_row.addWidget(self._spin_cant)

        btn_agregar = QPushButton("  Agregar Seleccionado")
        btn_agregar.setIcon(qta.icon("fa5s.plus", color="#10b981"))
        btn_agregar.setFixedHeight(28)
        btn_agregar.clicked.connect(self._agregar_desde_busqueda)
        add_row.addWidget(btn_agregar)
        add_row.addStretch()

        lbl_hint = QLabel("Doble clic en un producto para agregarlo")
        lbl_hint.setStyleSheet("font-size: 10px; color: #888;")
        add_row.addWidget(lbl_hint)
        search_lay.addLayout(add_row)

        layout.addWidget(search_frame)

        # === Items del requerimiento ===
        lbl_items = QLabel("Items del Requerimiento")
        lbl_items.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(lbl_items)

        self._tabla_items = QTableWidget()
        self._tabla_items.setColumnCount(5)
        self._tabla_items.setHorizontalHeaderLabels(["Codigo", "Descripcion", "Cantidad", "Stock Actual", ""])
        self._tabla_items.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla_items.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self._tabla_items.setColumnWidth(4, 40)
        self._tabla_items.setAlternatingRowColors(True)
        self._tabla_items.verticalHeader().setVisible(False)
        self._tabla_items.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._tabla_items, 1)

        # Botones
        btn_row = QHBoxLayout()
        self._lbl_total = QLabel("0 items")
        self._lbl_total.setStyleSheet("font-size: 12px; color: #888;")
        btn_row.addWidget(self._lbl_total)
        btn_row.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(32)
        btn_cancelar.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancelar)

        btn_guardar = QPushButton("  Crear Requerimiento")
        btn_guardar.setIcon(qta.icon("fa5s.check", color="#0f0f0f"))
        btn_guardar.setFixedHeight(32)
        btn_guardar.setFixedWidth(180)
        btn_guardar.clicked.connect(self._guardar)
        btn_row.addWidget(btn_guardar)
        layout.addLayout(btn_row)

    def _buscar_producto(self):
        texto = self._input_buscar.text().strip()
        if not texto:
            return

        from services.inventario_service import inventario_service
        from core.database import get_db
        from models.inventario import StockDeposito, MovimientoStock
        from models.comercial import OrdenCompraDetalle, OrdenCompra
        from models.finanzas import Factura, FacturaDetalle
        from sqlalchemy import func, desc

        productos = inventario_service.buscar_productos(texto)
        self._resultados_busqueda = productos

        self._tabla_busqueda.setRowCount(len(productos))
        for i, p in enumerate(productos):
            self._tabla_busqueda.setItem(i, 0, QTableWidgetItem(p.codigo))
            self._tabla_busqueda.setItem(i, 1, QTableWidgetItem(p.nombre))

            # Stock total
            stock = p.stock_total
            stock_item = QTableWidgetItem(str(stock))
            stock_item.setTextAlignment(Qt.AlignCenter)
            if stock == 0:
                stock_item.setForeground(Qt.red)
            self._tabla_busqueda.setItem(i, 2, stock_item)

            # Ultimo precio de compra y fecha
            ult_compra_precio = "---"
            ult_compra_fecha = "---"
            with get_db() as db:
                # Buscar en ordenes de compra
                ult_oc = db.query(OrdenCompraDetalle).join(OrdenCompra).filter(
                    OrdenCompraDetalle.descripcion.ilike(f"%{p.codigo}%"),
                    OrdenCompra.estado.in_(["recibida", "enviada"]),
                ).order_by(OrdenCompra.fecha.desc()).first()
                if ult_oc:
                    ult_compra_precio = f"$ {ult_oc.precio_unitario:,.2f}"
                    oc = db.get(OrdenCompra, ult_oc.orden_id)
                    if oc and oc.fecha:
                        ult_compra_fecha = oc.fecha.strftime("%d/%m/%Y")

                # Ultimo precio de venta y fecha
                ult_venta_precio = f"$ {p.precio_venta:,.2f}" if p.precio_venta else "---"
                ult_venta_fecha = "---"
                ult_fact = db.query(FacturaDetalle).join(Factura).filter(
                    FacturaDetalle.descripcion.ilike(f"%{p.nombre[:20]}%"),
                    Factura.tipo_entidad == "cliente",
                ).order_by(Factura.fecha.desc()).first()
                if ult_fact:
                    ult_venta_precio = f"$ {ult_fact.precio_unitario:,.2f}"
                    fact = db.get(Factura, ult_fact.factura_id)
                    if fact and fact.fecha:
                        ult_venta_fecha = fact.fecha.strftime("%d/%m/%Y")

            self._tabla_busqueda.setItem(i, 3, QTableWidgetItem(ult_compra_precio))
            self._tabla_busqueda.setItem(i, 4, QTableWidgetItem(ult_compra_fecha))
            self._tabla_busqueda.setItem(i, 5, QTableWidgetItem(ult_venta_precio))
            self._tabla_busqueda.setItem(i, 6, QTableWidgetItem(ult_venta_fecha))

    def _agregar_desde_busqueda(self):
        row = self._tabla_busqueda.currentRow()
        if row < 0 or row >= len(self._resultados_busqueda):
            return

        p = self._resultados_busqueda[row]
        cantidad = self._spin_cant.value()

        # Verificar si ya existe
        for item in self._items:
            if item["codigo"] == p.codigo:
                item["cantidad"] += cantidad
                self._actualizar_items()
                return

        self._items.append({
            "codigo": p.codigo,
            "descripcion": p.nombre,
            "cantidad": cantidad,
            "stock": p.stock_total,
        })
        self._actualizar_items()
        self._spin_cant.setValue(1)

    def _actualizar_items(self):
        self._tabla_items.setRowCount(len(self._items))
        for i, item in enumerate(self._items):
            self._tabla_items.setItem(i, 0, QTableWidgetItem(item["codigo"]))
            self._tabla_items.setItem(i, 1, QTableWidgetItem(item["descripcion"]))
            cant_item = QTableWidgetItem(str(item["cantidad"]))
            cant_item.setTextAlignment(Qt.AlignCenter)
            self._tabla_items.setItem(i, 2, cant_item)
            stock_item = QTableWidgetItem(str(item["stock"]))
            stock_item.setTextAlignment(Qt.AlignCenter)
            self._tabla_items.setItem(i, 3, stock_item)
            self._tabla_items.setItem(i, 4, QTableWidgetItem("X"))

        self._lbl_total.setText(f"{len(self._items)} items")

    def _guardar(self):
        if not self._items:
            QMessageBox.warning(self, "Error", "Agrega al menos un item.")
            return
        self.accept()

    def datos(self) -> dict:
        # Obtener usuario actual como solicitante
        solicitante = ""
        try:
            from services.auth_service import auth_service
            if auth_service.current_user:
                solicitante = auth_service.current_user.nombre_completo
        except Exception:
            pass

        return {
            "solicitante": solicitante,
            "sucursal_id": self._combo_sucursal.currentData(),
            "departamento": self._combo_depto.currentText() if self._combo_depto.currentData() else "",
            "tipo_compra_id": self._combo_tipo_compra.currentData(),
            "items": [{"descripcion": f"{i['codigo']} - {i['descripcion']}", "cantidad": i["cantidad"], "precio_unitario": 0} for i in self._items],
        }
