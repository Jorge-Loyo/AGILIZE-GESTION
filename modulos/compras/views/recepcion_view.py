from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QMessageBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.compras.compras_service import compras_service


class RecepcionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Recepcion de Mercaderia")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        btn_nueva = QPushButton("  Recibir OC")
        btn_nueva.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nueva.setFixedHeight(32)
        btn_nueva.setCursor(Qt.PointingHandCursor)
        btn_nueva.clicked.connect(self._recibir)
        header.addWidget(btn_nueva)
        layout.addLayout(header)

        subtitle = QLabel("Registro de mercaderia recibida. Seleccione una OC enviada para dar ingreso al deposito.")
        subtitle.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(subtitle)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Nro", "Fecha", "Proveedor", "Remito Prov.", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla, 1)

    def _cargar(self):
        recepciones = compras_service.listar_recepciones()
        self.tabla.setRowCount(len(recepciones))
        for i, r in enumerate(recepciones):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(r.numero)))
            self.tabla.setItem(i, 1, QTableWidgetItem(r.fecha.strftime("%d/%m/%Y") if r.fecha else ""))
            self.tabla.setItem(i, 2, QTableWidgetItem(r.proveedor_nombre))
            self.tabla.setItem(i, 3, QTableWidgetItem(r.remito_proveedor))
            self.tabla.setItem(i, 4, QTableWidgetItem(r.estado.capitalize()))

    def _recibir(self):
        ordenes = compras_service.listar_ordenes()
        enviadas = [o for o in ordenes if o.estado == "enviada"]
        if not enviadas:
            QMessageBox.information(self, "Info", "No hay ordenes de compra enviadas para recibir.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Recibir Orden de Compra")
        dlg.setMinimumWidth(400)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Seleccione la OC a recibir:"))

        combo = QComboBox()
        combo.setFixedHeight(28)
        for o in enviadas:
            combo.addItem(f"OC #{o.numero} - {o.proveedor_nombre} ($ {o.total:,.2f})", o.id)
        lay.addWidget(combo)

        lay.addWidget(QLabel("Nro Remito del proveedor:"))
        input_remito = QLineEdit()
        input_remito.setFixedHeight(28)
        input_remito.setMaxLength(50)
        lay.addWidget(input_remito)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dlg.reject)
        btns.addWidget(btn_cancel)
        btn_ok = QPushButton("Confirmar Recepcion")
        btn_ok.clicked.connect(dlg.accept)
        btns.addWidget(btn_ok)
        lay.addLayout(btns)

        if dlg.exec() == QDialog.Accepted:
            oc_id = combo.currentData()
            remito = input_remito.text().strip()
            try:
                compras_service.registrar_recepcion(oc_id, remito)
                self._cargar()
                QMessageBox.information(self, "OK", "Recepcion registrada. Stock actualizado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
