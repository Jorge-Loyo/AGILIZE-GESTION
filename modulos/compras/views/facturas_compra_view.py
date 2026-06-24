from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QMessageBox, QDateEdit,
)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta
from services.compras.compras_service import compras_service


class FacturasCompraView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Facturas de Compra")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        btn_nueva = QPushButton("  Registrar Factura")
        btn_nueva.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nueva.setFixedHeight(32)
        btn_nueva.setCursor(Qt.PointingHandCursor)
        btn_nueva.clicked.connect(self._nueva)
        header.addWidget(btn_nueva)
        layout.addLayout(header)

        subtitle = QLabel("Facturas recibidas de proveedores. Se concilian contra OC y Recepcion (Three-Way Match).")
        subtitle.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(subtitle)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["Nro Factura", "Fecha", "Proveedor", "Total", "Vto.", "Estado", "Conciliada"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabla, 1)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_traza = QPushButton("  Trazabilidad")
        btn_traza.setIcon(qta.icon("fa5s.project-diagram", color="#3b82f6"))
        btn_traza.setFixedHeight(30)
        btn_traza.clicked.connect(self._ver_trazabilidad)
        btns.addWidget(btn_traza)
        btn_conciliar = QPushButton("  Conciliar (3-Way Match)")
        btn_conciliar.setIcon(qta.icon("fa5s.check-double", color="#10b981"))
        btn_conciliar.setFixedHeight(30)
        btn_conciliar.clicked.connect(self._conciliar)
        btns.addWidget(btn_conciliar)
        btn_pagar = QPushButton("  Marcar Pagada")
        btn_pagar.setFixedHeight(30)
        btn_pagar.clicked.connect(self._marcar_pagada)
        btns.addWidget(btn_pagar)
        layout.addLayout(btns)

    def _cargar(self):
        facturas = compras_service.listar_facturas_compra()
        self.tabla.setRowCount(len(facturas))
        for i, f in enumerate(facturas):
            self.tabla.setItem(i, 0, QTableWidgetItem(f.numero_factura))
            self.tabla.setItem(i, 1, QTableWidgetItem(f.fecha.strftime("%d/%m/%Y") if f.fecha else ""))
            self.tabla.setItem(i, 2, QTableWidgetItem(f.proveedor_nombre))
            t = QTableWidgetItem(f"$ {f.total:,.2f}")
            t.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 3, t)
            self.tabla.setItem(i, 4, QTableWidgetItem(f.fecha_vencimiento.strftime("%d/%m/%Y") if f.fecha_vencimiento else ""))
            self.tabla.setItem(i, 5, QTableWidgetItem(f.estado.capitalize()))
            self.tabla.setItem(i, 6, QTableWidgetItem("Si" if f.conciliada else "No"))

    def _nueva(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Registrar Factura de Compra")
        dlg.setMinimumWidth(450)
        lay = QVBoxLayout(dlg)
        form = QFormLayout()

        input_nro = QLineEdit()
        input_nro.setFixedHeight(28)
        input_nro.setMaxLength(50)
        input_nro.setPlaceholderText("Ej: A-0001-00012345")
        form.addRow("Nro Factura:", input_nro)

        input_prov = QLineEdit()
        input_prov.setFixedHeight(28)
        input_prov.setMaxLength(200)
        form.addRow("Proveedor:", input_prov)

        input_total = QLineEdit()
        input_total.setFixedHeight(28)
        input_total.setMaxLength(20)
        input_total.setPlaceholderText("Total con IVA")
        form.addRow("Total:", input_total)

        date_vto = QDateEdit()
        date_vto.setDate(QDate.currentDate().addDays(30))
        date_vto.setCalendarPopup(True)
        date_vto.setFixedHeight(28)
        form.addRow("Vencimiento:", date_vto)

        # Vincular a OC
        combo_oc = QComboBox()
        combo_oc.setFixedHeight(28)
        combo_oc.addItem("-- Sin vincular --", None)
        for o in compras_service.listar_ordenes():
            if o.estado in ("enviada", "recibida"):
                combo_oc.addItem(f"OC #{o.numero} - {o.proveedor_nombre}", o.id)
        form.addRow("Orden de Compra:", combo_oc)

        lay.addLayout(form)
        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dlg.reject)
        btns.addWidget(btn_cancel)
        btn_ok = QPushButton("Registrar")
        btn_ok.clicked.connect(dlg.accept)
        btns.addWidget(btn_ok)
        lay.addLayout(btns)

        if dlg.exec() == QDialog.Accepted:
            try:
                total = float(input_total.text().strip().replace(",", "").replace("$", ""))
                compras_service.registrar_factura_compra(
                    numero_factura=input_nro.text().strip(),
                    proveedor_nombre=input_prov.text().strip(),
                    total=total,
                    fecha_vencimiento=date_vto.date().toPython(),
                    orden_compra_id=combo_oc.currentData(),
                )
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _conciliar(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
        facturas = compras_service.listar_facturas_compra()
        if row < len(facturas):
            compras_service.conciliar_factura(facturas[row].id)
            self._cargar()
            QMessageBox.information(self, "OK", "Factura conciliada (Three-Way Match).")

    def _marcar_pagada(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
        facturas = compras_service.listar_facturas_compra()
        if row < len(facturas):
            compras_service.cambiar_estado_factura(facturas[row].id, "pagada")
            self._cargar()

    def _ver_trazabilidad(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
        facturas = compras_service.listar_facturas_compra()
        if row >= len(facturas):
            return
        fact = facturas[row]
        from modulos.compras.views.trazabilidad_view import TrazabilidadCompraView
        from PySide6.QtWidgets import QDialog, QVBoxLayout
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Trazabilidad - Factura {fact.numero_factura}")
        dlg.setMinimumSize(800, 450)
        lay = QVBoxLayout(dlg)
        view = TrazabilidadCompraView()
        # Pre-cargar busqueda
        view._combo_tipo.setCurrentIndex(1)  # factura_compra
        view._spin_id.setValue(fact.id)
        view._buscar()
        lay.addWidget(view)
        dlg.exec()
