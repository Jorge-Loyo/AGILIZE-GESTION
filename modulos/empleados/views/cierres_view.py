from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel,
    QMessageBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt
from datetime import date
from services.cierre_service import cierre_service
from services.nomina_service import nomina_service
from services.auth_service import auth_service


class CierresAsistenciaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar_cierres()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Cierres de Asistencia")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Al cerrar un periodo no se podran editar los registros de asistencia de ese mes.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Form
        grp = QGroupBox("Gestionar Periodo")
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        form = QHBoxLayout(grp)
        form.setSpacing(12)

        form.addWidget(QLabel("Periodo (YYYY-MM):"))
        self.input_periodo = QLineEdit()
        self.input_periodo.setMinimumHeight(34)
        self.input_periodo.setPlaceholderText("2025-06")
        self.input_periodo.setText(date.today().strftime("%Y-%m"))
        self.input_periodo.setMaximumWidth(150)
        form.addWidget(self.input_periodo)

        btn_cerrar = QPushButton("Cerrar Asistencia")
        btn_cerrar.setMinimumHeight(34)
        btn_cerrar.clicked.connect(self._cerrar)
        form.addWidget(btn_cerrar)

        btn_reabrir = QPushButton("Reabrir Periodo")
        btn_reabrir.setMinimumHeight(34)
        btn_reabrir.setStyleSheet("QPushButton { background-color: #f59e0b; color: #0f0f0f; } QPushButton:hover { background-color: #d97706; }")
        btn_reabrir.clicked.connect(self._reabrir)
        form.addWidget(btn_reabrir)

        form.addStretch()
        layout.addWidget(grp)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Periodo", "Estado", "Fecha Cierre"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)

    def _cargar_cierres(self):
        cierres = cierre_service.listar_cierres_asistencia()
        self.tabla.setRowCount(len(cierres))
        for i, c in enumerate(cierres):
            self.tabla.setItem(i, 0, QTableWidgetItem(c.periodo))
            estado = "CERRADO" if c.cerrado else "ABIERTO"
            self.tabla.setItem(i, 1, QTableWidgetItem(estado))
            fecha = c.fecha_cierre.strftime("%d/%m/%Y %H:%M") if c.fecha_cierre else ""
            self.tabla.setItem(i, 2, QTableWidgetItem(fecha))

    def _cerrar(self):
        periodo = self.input_periodo.text().strip()
        if not periodo:
            QMessageBox.warning(self, "Error", "Ingresa un periodo.")
            return
        if cierre_service.asistencia_cerrada(periodo):
            QMessageBox.information(self, "Info", f"El periodo {periodo} ya esta cerrado.")
            return
        resp = QMessageBox.question(
            self, "Confirmar",
            f"Cerrar asistencia del periodo {periodo}?\nNo se podran editar registros de este mes.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            user_id = auth_service.current_user.id if auth_service.current_user else None
            cierre_service.cerrar_asistencia(periodo, user_id)
            self._cargar_cierres()
            QMessageBox.information(self, "OK", f"Asistencia {periodo} cerrada.")

    def _reabrir(self):
        periodo = self.input_periodo.text().strip()
        if not periodo:
            QMessageBox.warning(self, "Error", "Ingresa un periodo.")
            return
        if not cierre_service.asistencia_cerrada(periodo):
            QMessageBox.information(self, "Info", f"El periodo {periodo} ya esta abierto.")
            return

        # Verificar si hay liquidaciones en este periodo
        liquidaciones = nomina_service.listar_liquidaciones(periodo=periodo)
        mensaje = f"Reabrir asistencia del periodo {periodo}?"
        if liquidaciones:
            mensaje += f"\n\nATENCION: Este periodo tiene {len(liquidaciones)} liquidacion(es) realizadas. Reabrir puede generar inconsistencias."

        resp = QMessageBox.warning(
            self, "Confirmar reapertura",
            mensaje,
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            user_id = auth_service.current_user.id if auth_service.current_user else None
            cierre_service.reabrir_asistencia(periodo, user_id)
            self._cargar_cierres()
            QMessageBox.information(self, "OK", f"Asistencia {periodo} reabierta.")
