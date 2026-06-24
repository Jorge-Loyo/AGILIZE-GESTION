"""
Facturador Interno - Genera facturas a partir de presupuestos o pedidos aprobados.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QMessageBox, QTabWidget,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.ventas_service import ventas_service
from services.finanzas_service import finanzas_service
from services.empresa_service import empresa_service


class FacturarInternoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items_factura = []
        self._origen_tipo = ""
        self._origen_id = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Facturar desde Presupuesto / Pedido")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Seleccione un presupuesto aprobado o pedido pendiente para generar la factura.")
        subtitle.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(subtitle)

        # Tabs: presupuestos / pedidos
        tabs = QTabWidget()
        tabs.addTab(self._build_presupuestos_tab(), "Presupuestos Aprobados")
        tabs.addTab(self._build_pedidos_tab(), "Pedidos Pendientes")
        layout.addWidget(tabs)

        # Preview de factura
        grp_preview = QFrame()
        grp_preview.setObjectName("card")
        preview_lay = QVBoxLayout(grp_preview)
        preview_lay.setContentsMargins(12, 10, 12, 10)
        preview_lay.setSpacing(6)

        lbl_preview = QLabel("Vista previa de factura:")
        lbl_preview.setStyleSheet("font-weight: bold; font-size: 12px;")
        preview_lay.addWidget(lbl_preview)

        self._lbl_origen = QLabel("Ninguno seleccionado")
        self._lbl_origen.setStyleSheet("font-size: 11px; color: #888;")
        preview_lay.addWidget(self._lbl_origen)

        self._tabla_preview = QTableWidget()
        self._tabla_preview.setColumnCount(4)
        self._tabla_preview.setHorizontalHeaderLabels(["Descripcion", "Cant", "Precio", "Subtotal"])
        self._tabla_preview.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tabla_preview.verticalHeader().setVisible(False)
        self._tabla_preview.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_preview.setMaximumHeight(150)
        preview_lay.addWidget(self._tabla_preview)

        self._lbl_total = QLabel("Total: $ 0.00")
        self._lbl_total.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        preview_lay.addWidget(self._lbl_total)

        layout.addWidget(grp_preview)

        # Boton facturar
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_facturar = QPushButton("  Emitir Factura")
        btn_facturar.setIcon(qta.icon("fa5s.file-invoice", color="#0f0f0f"))
        btn_facturar.setFixedHeight(38)
        btn_facturar.setFixedWidth(200)
        btn_facturar.setCursor(Qt.PointingHandCursor)
        btn_facturar.clicked.connect(self._facturar)
        btn_row.addWidget(btn_facturar)
        layout.addLayout(btn_row)

    def _build_presupuestos_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setSpacing(6)

        self._tabla_pres = QTableWidget()
        self._tabla_pres.setColumnCount(4)
        self._tabla_pres.setHorizontalHeaderLabels(["Nro", "Fecha", "Cliente", "Total"])
        self._tabla_pres.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._tabla_pres.setAlternatingRowColors(True)
        self._tabla_pres.verticalHeader().setVisible(False)
        self._tabla_pres.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_pres.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_pres.clicked.connect(self._seleccionar_presupuesto)
        lay.addWidget(self._tabla_pres)

        self._cargar_presupuestos()
        return page

    def _build_pedidos_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setSpacing(6)

        self._tabla_ped = QTableWidget()
        self._tabla_ped.setColumnCount(4)
        self._tabla_ped.setHorizontalHeaderLabels(["Nro", "Fecha", "Cliente", "Total"])
        self._tabla_ped.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._tabla_ped.setAlternatingRowColors(True)
        self._tabla_ped.verticalHeader().setVisible(False)
        self._tabla_ped.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_ped.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_ped.clicked.connect(self._seleccionar_pedido)
        lay.addWidget(self._tabla_ped)

        self._cargar_pedidos()
        return page

    def _cargar_presupuestos(self):
        presupuestos = ventas_service.listar_presupuestos()
        aprobados = [p for p in presupuestos if p.estado == "aprobado"]
        self._presupuestos = aprobados
        self._tabla_pres.setRowCount(len(aprobados))
        for i, p in enumerate(aprobados):
            self._tabla_pres.setItem(i, 0, QTableWidgetItem(str(p.numero)))
            self._tabla_pres.setItem(i, 1, QTableWidgetItem(p.fecha.strftime("%d/%m/%Y") if p.fecha else ""))
            self._tabla_pres.setItem(i, 2, QTableWidgetItem(p.cliente_nombre))
            t = QTableWidgetItem(f"$ {p.total:,.2f}")
            t.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._tabla_pres.setItem(i, 3, t)

    def _cargar_pedidos(self):
        pedidos = ventas_service.listar_pedidos()
        pendientes = [p for p in pedidos if p.estado == "pendiente"]
        self._pedidos = pendientes
        self._tabla_ped.setRowCount(len(pendientes))
        for i, p in enumerate(pendientes):
            self._tabla_ped.setItem(i, 0, QTableWidgetItem(str(p.numero)))
            self._tabla_ped.setItem(i, 1, QTableWidgetItem(p.fecha.strftime("%d/%m/%Y") if p.fecha else ""))
            self._tabla_ped.setItem(i, 2, QTableWidgetItem(p.cliente_nombre))
            t = QTableWidgetItem(f"$ {p.total:,.2f}")
            t.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._tabla_ped.setItem(i, 3, t)

    def _seleccionar_presupuesto(self):
        row = self._tabla_pres.currentRow()
        if row < 0 or row >= len(self._presupuestos):
            return
        p = self._presupuestos[row]
        self._origen_tipo = "presupuesto"
        self._origen_id = p.id
        self._lbl_origen.setText(f"Presupuesto #{p.numero} - {p.cliente_nombre}")

        # Cargar detalles
        from core.database import get_db
        from models.comercial import PresupuestoDetalle
        with get_db() as db:
            detalles = db.query(PresupuestoDetalle).filter(PresupuestoDetalle.presupuesto_id == p.id).all()
            self._items_factura = [{"descripcion": d.descripcion, "cantidad": d.cantidad, "precio_unitario": d.precio_unitario} for d in detalles]

        self._actualizar_preview(p.cliente_nombre, p.total)

    def _seleccionar_pedido(self):
        row = self._tabla_ped.currentRow()
        if row < 0 or row >= len(self._pedidos):
            return
        p = self._pedidos[row]
        self._origen_tipo = "pedido"
        self._origen_id = p.id
        self._lbl_origen.setText(f"Pedido #{p.numero} - {p.cliente_nombre}")

        from core.database import get_db
        from models.comercial import PedidoVentaDetalle
        with get_db() as db:
            detalles = db.query(PedidoVentaDetalle).filter(PedidoVentaDetalle.pedido_id == p.id).all()
            self._items_factura = [{"descripcion": d.descripcion, "cantidad": d.cantidad, "precio_unitario": d.precio_unitario} for d in detalles]

        self._actualizar_preview(p.cliente_nombre, p.total)

    def _actualizar_preview(self, cliente: str, total: float):
        self._tabla_preview.setRowCount(len(self._items_factura))
        for i, item in enumerate(self._items_factura):
            self._tabla_preview.setItem(i, 0, QTableWidgetItem(item["descripcion"]))
            self._tabla_preview.setItem(i, 1, QTableWidgetItem(f"{item['cantidad']:.2f}"))
            self._tabla_preview.setItem(i, 2, QTableWidgetItem(f"$ {item['precio_unitario']:,.2f}"))
            st = item["cantidad"] * item["precio_unitario"]
            self._tabla_preview.setItem(i, 3, QTableWidgetItem(f"$ {st:,.2f}"))
        self._lbl_total.setText(f"Total: $ {total:,.2f}")

    def _facturar(self):
        if not self._items_factura:
            QMessageBox.warning(self, "Error", "Seleccione un presupuesto o pedido primero.")
            return

        pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
        iva_pct = 16 if pais == "Venezuela" else 21

        # Obtener nombre del cliente
        cliente_nombre = ""
        if self._origen_tipo == "presupuesto":
            row = self._tabla_pres.currentRow()
            if row >= 0:
                cliente_nombre = self._presupuestos[row].cliente_nombre
        elif self._origen_tipo == "pedido":
            row = self._tabla_ped.currentRow()
            if row >= 0:
                cliente_nombre = self._pedidos[row].cliente_nombre

        resp = QMessageBox.question(
            self, "Confirmar Factura",
            f"Emitir factura para: {cliente_nombre}\nConfirmar?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        try:
            datos = {
                "tipo_comprobante": "factura",
                "letra": "A" if pais == "Argentina" else "",
                "tipo_entidad": "cliente",
                "entidad_nombre": cliente_nombre,
                "impuesto_porcentaje": iva_pct,
            }
            finanzas_service.crear_factura(datos, self._items_factura)

            # Cambiar estado del origen
            if self._origen_tipo == "pedido" and self._origen_id:
                ventas_service.cambiar_estado_pedido(self._origen_id, "entregado")

            QMessageBox.information(self, "Factura Emitida", f"Factura generada para {cliente_nombre}.")

            # Limpiar
            self._items_factura = []
            self._origen_tipo = ""
            self._origen_id = None
            self._lbl_origen.setText("Ninguno seleccionado")
            self._tabla_preview.setRowCount(0)
            self._lbl_total.setText("Total: $ 0.00")
            self._cargar_presupuestos()
            self._cargar_pedidos()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
