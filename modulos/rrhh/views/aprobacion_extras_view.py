from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox, QLineEdit, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt
from services.aprobacion_extras_service import aprobacion_extras_service
from services.auth_service import auth_service


class AprobacionExtrasView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._registros = []
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        # Filtro
        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Estado:"))
        self.filtro_estado = QComboBox()
        self.filtro_estado.setMinimumHeight(32)
        self.filtro_estado.addItem("Pendientes", "pendiente")
        self.filtro_estado.addItem("Aprobadas", "aprobada")
        self.filtro_estado.addItem("Rechazadas", "rechazada")
        self.filtro_estado.addItem("Todas", "")
        self.filtro_estado.currentIndexChanged.connect(self._cargar)
        filtros.addWidget(self.filtro_estado)
        filtros.addStretch()

        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("font-weight: bold; color: #D4AF37;")
        filtros.addWidget(self.lbl_count)
        layout.addLayout(filtros)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Empleado", "Fecha", "Hs Extra", "Estado", "Aprobado por", "Fecha Aprob.", "Motivo"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.MultiSelection)
        layout.addWidget(self.tabla)

        # Botones
        btns = QHBoxLayout()
        btns.addStretch()

        btn_aprobar = QPushButton("Aprobar Seleccion")
        btn_aprobar.setMinimumHeight(36)
        btn_aprobar.setStyleSheet("QPushButton { background-color: #10b981; } QPushButton:hover { background-color: #059669; }")
        btn_aprobar.clicked.connect(self._aprobar_seleccion)
        btns.addWidget(btn_aprobar)

        btn_aprobar_todo = QPushButton("Aprobar Todos")
        btn_aprobar_todo.setMinimumHeight(36)
        btn_aprobar_todo.setStyleSheet("QPushButton { background-color: #D4AF37; color: #121212; font-weight: bold; }")
        btn_aprobar_todo.clicked.connect(self._aprobar_todos)
        btns.addWidget(btn_aprobar_todo)

        btn_rechazar = QPushButton("Rechazar")
        btn_rechazar.setMinimumHeight(36)
        btn_rechazar.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_rechazar.clicked.connect(self._rechazar_seleccion)
        btns.addWidget(btn_rechazar)

        layout.addLayout(btns)

    def _cargar(self):
        estado = self.filtro_estado.currentData()
        if estado:
            self._registros = aprobacion_extras_service.listar_todas(estado=estado)
        else:
            self._registros = aprobacion_extras_service.listar_todas()

        self.tabla.setRowCount(len(self._registros))
        for i, ap in enumerate(self._registros):
            nombre = ""
            fecha = ""
            if ap.asistencia and ap.asistencia.empleado:
                emp = ap.asistencia.empleado
                nombre = f"{emp.legajo} - {emp.nombre} {emp.apellido or ''}"
                fecha = ap.asistencia.fecha.strftime("%d/%m/%Y")

            self.tabla.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla.setItem(i, 1, QTableWidgetItem(fecha))
            self.tabla.setItem(i, 2, QTableWidgetItem(f"{ap.horas_extra:.2f}"))
            item_estado = QTableWidgetItem(ap.estado.capitalize())
            self.tabla.setItem(i, 3, item_estado)
            aprobador = ap.aprobador.nombre_completo if ap.aprobador else ""
            self.tabla.setItem(i, 4, QTableWidgetItem(aprobador))
            fecha_ap = ap.fecha_aprobacion.strftime("%d/%m/%Y %H:%M") if ap.fecha_aprobacion else ""
            self.tabla.setItem(i, 5, QTableWidgetItem(fecha_ap))
            self.tabla.setItem(i, 6, QTableWidgetItem(ap.motivo_rechazo or ""))

        self.lbl_count.setText(f"{len(self._registros)} registro(s)")

    def _get_selected_ids(self) -> list[int]:
        rows = set(idx.row() for idx in self.tabla.selectedIndexes())
        ids = []
        for row in rows:
            if row < len(self._registros):
                ids.append(self._registros[row].id)
        return ids

    def _aprobar_seleccion(self):
        ids = self._get_selected_ids()
        if not ids:
            QMessageBox.information(self, "Info", "Selecciona al menos un registro.")
            return
        user = auth_service.current_user
        aprobacion_extras_service.aprobar_masivo(ids, user.id if user else None)
        self._cargar()
        QMessageBox.information(self, "OK", f"{len(ids)} registro(s) aprobado(s).")

    def _aprobar_todos(self):
        pendientes = [r for r in self._registros if r.estado == "pendiente"]
        if not pendientes:
            QMessageBox.information(self, "Info", "No hay pendientes.")
            return
        resp = QMessageBox.question(
            self, "Aprobar Todos",
            f"Aprobar {len(pendientes)} registro(s) pendiente(s)?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            user = auth_service.current_user
            ids = [r.id for r in pendientes]
            aprobacion_extras_service.aprobar_masivo(ids, user.id if user else None)
            self._cargar()

    def _rechazar_seleccion(self):
        ids = self._get_selected_ids()
        if not ids:
            QMessageBox.information(self, "Info", "Selecciona al menos un registro.")
            return
        motivo, ok = QInputDialog.getText(self, "Motivo", "Motivo del rechazo (opcional):")
        if not ok:
            return
        user = auth_service.current_user
        for ap_id in ids:
            aprobacion_extras_service.rechazar(ap_id, user.id if user else None, motivo)
        self._cargar()
        QMessageBox.information(self, "OK", f"{len(ids)} registro(s) rechazado(s).")
