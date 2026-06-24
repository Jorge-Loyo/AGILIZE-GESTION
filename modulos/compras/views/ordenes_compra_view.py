from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QMessageBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.compras_service import compras_service


class OrdenesCompraView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Ordenes de Compra")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        btn_nuevo = QPushButton("  Nueva Orden")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(32)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self._nuevo)
        header.addWidget(btn_nuevo)
        layout.addLayout(header)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Nro", "Fecha", "Proveedor", "Total", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabla, 1)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_enviar = QPushButton("  Marcar Enviada")
        btn_enviar.setFixedHeight(30)
        btn_enviar.clicked.connect(lambda: self._cambiar_estado("enviada"))
        btns.addWidget(btn_enviar)
        btn_recibir = QPushButton("  Marcar Recibida")
        btn_recibir.setIcon(qta.icon("fa5s.check", color="#10b981"))
        btn_recibir.setFixedHeight(30)
        btn_recibir.clicked.connect(lambda: self._cambiar_estado("recibida"))
        btns.addWidget(btn_recibir)
        layout.addLayout(btns)

    def _cargar(self):
        ordenes = compras_service.listar_ordenes()
        self.tabla.setRowCount(len(ordenes))
        for i, o in enumerate(ordenes):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(o.numero)))
            self.tabla.setItem(i, 1, QTableWidgetItem(o.fecha.strftime("%d/%m/%Y") if o.fecha else ""))
            self.tabla.setItem(i, 2, QTableWidgetItem(o.proveedor_nombre))
            t = QTableWidgetItem(f"$ {o.total:,.2f}")
            t.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 3, t)
            self.tabla.setItem(i, 4, QTableWidgetItem(o.estado.capitalize()))

    def _nuevo(self):
        from modulos.ventas.views.presupuestos_view import DocumentoComercialDialog
        dlg = DocumentoComercialDialog("Orden de Compra", parent=self)
        if dlg.exec() == QDialog.Accepted:
            datos = dlg.datos()
            try:
                compras_service.crear_orden(datos["nombre"], datos["items"])
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _cambiar_estado(self, estado: str):
        row = self.tabla.currentRow()
        if row < 0:
            return
        ordenes = compras_service.listar_ordenes()
        if row < len(ordenes):
            compras_service.cambiar_estado(ordenes[row].id, estado)
            self._cargar()
