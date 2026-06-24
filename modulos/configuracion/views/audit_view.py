from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from services.core.audit_service import listar_auditoria


class AuditView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Log de Auditor\u00eda")
        title.setObjectName("title")
        layout.addWidget(title)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Fecha/Hora", "Usuario", "Acci\u00f3n", "Tabla", "Detalle"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)

    def _cargar(self):
        logs = listar_auditoria(200)
        self.tabla.setRowCount(len(logs))
        for i, log in enumerate(logs):
            fecha = log.timestamp.strftime("%d/%m/%Y %H:%M") if log.timestamp else "\u2014"
            self.tabla.setItem(i, 0, QTableWidgetItem(fecha))
            self.tabla.setItem(i, 1, QTableWidgetItem(str(log.usuario_id or "\u2014")))
            self.tabla.setItem(i, 2, QTableWidgetItem(log.accion))
            self.tabla.setItem(i, 3, QTableWidgetItem(log.tabla or ""))
            self.tabla.setItem(i, 4, QTableWidgetItem(log.detalle or ""))
