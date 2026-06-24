from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QMessageBox, QDoubleSpinBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.compras.compras_service import compras_service


class RequisicionesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Requerimientos de Compra")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        btn_nueva = QPushButton("  Nuevo Requerimiento")
        btn_nueva.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nueva.setFixedHeight(32)
        btn_nueva.setCursor(Qt.PointingHandCursor)
        btn_nueva.clicked.connect(self._nueva)
        header.addWidget(btn_nueva)
        layout.addLayout(header)

        subtitle = QLabel("Solicitudes internas de compra. Al aprobar, se puede generar una Orden de Compra.")
        subtitle.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(subtitle)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Nro", "Fecha", "Solicitante", "Departamento", "Prioridad", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabla, 1)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_aprobar = QPushButton("  Aprobar")
        btn_aprobar.setIcon(qta.icon("fa5s.check", color="#10b981"))
        btn_aprobar.setFixedHeight(30)
        btn_aprobar.clicked.connect(lambda: self._cambiar_estado("aprobada"))
        btns.addWidget(btn_aprobar)
        btn_rechazar = QPushButton("  Rechazar")
        btn_rechazar.setIcon(qta.icon("fa5s.times", color="#ef4444"))
        btn_rechazar.setFixedHeight(30)
        btn_rechazar.clicked.connect(lambda: self._cambiar_estado("rechazada"))
        btns.addWidget(btn_rechazar)
        btn_generar_oc = QPushButton("  Generar OC")
        btn_generar_oc.setIcon(qta.icon("fa5s.arrow-right", color="#3b82f6"))
        btn_generar_oc.setFixedHeight(30)
        btn_generar_oc.clicked.connect(self._generar_oc)
        btns.addWidget(btn_generar_oc)
        layout.addLayout(btns)

    def _cargar(self):
        requisiciones = compras_service.listar_requisiciones()
        self.tabla.setRowCount(len(requisiciones))
        for i, r in enumerate(requisiciones):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(r.numero)))
            self.tabla.setItem(i, 1, QTableWidgetItem(r.fecha.strftime("%d/%m/%Y") if r.fecha else ""))
            self.tabla.setItem(i, 2, QTableWidgetItem(r.solicitante))
            self.tabla.setItem(i, 3, QTableWidgetItem(r.departamento))
            self.tabla.setItem(i, 4, QTableWidgetItem(r.prioridad.capitalize()))
            self.tabla.setItem(i, 5, QTableWidgetItem(r.estado.replace("_", " ").capitalize()))

    def _nueva(self):
        from modulos.compras.views.requerimiento_dialog import RequerimientoDialog
        dlg = RequerimientoDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            datos = dlg.datos()
            try:
                compras_service.crear_requisicion(datos["solicitante"], datos["items"])
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _cambiar_estado(self, estado):
        row = self.tabla.currentRow()
        if row < 0:
            return
        requisiciones = compras_service.listar_requisiciones()
        if row < len(requisiciones):
            compras_service.cambiar_estado_requisicion(requisiciones[row].id, estado)
            self._cargar()

    def _generar_oc(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Selecciona una requisicion aprobada.")
            return
        requisiciones = compras_service.listar_requisiciones()
        if row < len(requisiciones):
            req = requisiciones[row]
            if req.estado != "aprobada":
                QMessageBox.warning(self, "Error", "Solo se pueden generar OC de requisiciones aprobadas.")
                return
            try:
                compras_service.generar_oc_desde_requisicion(req.id)
                compras_service.cambiar_estado_requisicion(req.id, "en_compra")
                self._cargar()
                QMessageBox.information(self, "OK", "Orden de Compra generada. Revise en 'Ordenes de Compra'.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
