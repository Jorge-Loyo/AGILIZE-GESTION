from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QLabel, QDateEdit, QDialog,
    QMessageBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, QDate
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

        subtitle = QLabel("Cierra quincenas por rango de fechas. No se pueden solapar periodos.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Form cerrar
        grp = QGroupBox("Cerrar Quincena")
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        form = QGridLayout(grp)
        form.setSpacing(10)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        form.addWidget(QLabel("Desde:"), 0, 0)
        self.input_desde = QDateEdit()
        self.input_desde.setMinimumHeight(34)
        self.input_desde.setCalendarPopup(True)
        # Default: dia 1 del mes actual
        hoy = date.today()
        self.input_desde.setDate(QDate(hoy.year, hoy.month, 1))
        form.addWidget(self.input_desde, 0, 1)

        form.addWidget(QLabel("Hasta:"), 0, 2)
        self.input_hasta = QDateEdit()
        self.input_hasta.setMinimumHeight(34)
        self.input_hasta.setCalendarPopup(True)
        self.input_hasta.setDate(QDate(hoy.year, hoy.month, 15))
        form.addWidget(self.input_hasta, 0, 3)

        btn_cerrar = QPushButton("Cerrar Quincena")
        btn_cerrar.setMinimumHeight(36)
        btn_cerrar.clicked.connect(self._cerrar)
        form.addWidget(btn_cerrar, 1, 1)

        btn_reabrir = QPushButton("Reabrir Seleccionado")
        btn_reabrir.setMinimumHeight(36)
        btn_reabrir.setStyleSheet("QPushButton { background-color: #f59e0b; color: #0f0f0f; } QPushButton:hover { background-color: #d97706; }")
        btn_reabrir.clicked.connect(self._reabrir)
        form.addWidget(btn_reabrir, 1, 3)

        layout.addWidget(grp)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Periodo", "Desde", "Hasta", "Estado", "Fecha Cierre"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.tabla)

        # Botones abajo
        bottom = QHBoxLayout()
        bottom.addStretch()

        btn_editar_cierre = QPushButton("Editar Cierre")
        btn_editar_cierre.setMinimumHeight(34)
        btn_editar_cierre.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_editar_cierre.clicked.connect(self._editar_cierre)
        bottom.addWidget(btn_editar_cierre)

        btn_borrar_cierre = QPushButton("Eliminar Cierre")
        btn_borrar_cierre.setMinimumHeight(34)
        btn_borrar_cierre.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_borrar_cierre.clicked.connect(self._borrar_cierre)
        bottom.addWidget(btn_borrar_cierre)

        layout.addLayout(bottom)

    def _cargar_cierres(self):
        cierres = cierre_service.listar_cierres_asistencia()
        self.tabla.setRowCount(len(cierres))
        for i, c in enumerate(cierres):
            quincena_txt = f"{c.periodo} Q{c.quincena}"
            self.tabla.setItem(i, 0, QTableWidgetItem(quincena_txt))
            self.tabla.setItem(i, 1, QTableWidgetItem(c.fecha_desde.strftime("%d/%m/%Y") if c.fecha_desde else ""))
            self.tabla.setItem(i, 2, QTableWidgetItem(c.fecha_hasta.strftime("%d/%m/%Y") if c.fecha_hasta else ""))
            estado = "CERRADO" if c.cerrado else "ABIERTO"
            self.tabla.setItem(i, 3, QTableWidgetItem(estado))
            fecha = c.fecha_cierre.strftime("%d/%m/%Y %H:%M") if c.fecha_cierre else ""
            self.tabla.setItem(i, 4, QTableWidgetItem(fecha))

    def _cerrar(self):
        desde = self.input_desde.date().toPython()
        hasta = self.input_hasta.date().toPython()

        if hasta <= desde:
            QMessageBox.warning(self, "Error", "La fecha 'Hasta' debe ser posterior a 'Desde'.")
            return

        # Verificar solapamiento
        cierres = cierre_service.listar_cierres_asistencia()
        for c in cierres:
            if c.cerrado and c.fecha_desde and c.fecha_hasta:
                if desde <= c.fecha_hasta and hasta >= c.fecha_desde:
                    QMessageBox.warning(self, "Solapamiento",
                        f"El rango se solapa con el cierre {c.periodo} Q{c.quincena} ({c.fecha_desde} - {c.fecha_hasta}).")
                    return

        # Verificar incompletos
        try:
            user_id = auth_service.current_user.id if auth_service.current_user else None
            cierre_service.cerrar_asistencia_rango(desde, hasta, user_id)
            self._cargar_cierres()
            QMessageBox.information(self, "OK", f"Quincena {desde.strftime('%d/%m')} al {hasta.strftime('%d/%m/%Y')} cerrada.")
        except ValueError as e:
            QMessageBox.warning(self, "No se puede cerrar", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _reabrir(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccion", "Selecciona un cierre de la tabla.")
            return

        cierres = cierre_service.listar_cierres_asistencia()
        if row >= len(cierres):
            return
        cierre = cierres[row]

        if not cierre.cerrado:
            QMessageBox.information(self, "Info", "Este periodo ya esta abierto.")
            return

        # Verificar liquidaciones
        liquidaciones = nomina_service.listar_liquidaciones(periodo=cierre.periodo)
        mensaje = f"Reabrir quincena {cierre.periodo} Q{cierre.quincena}?"
        if liquidaciones:
            mensaje += f"\n\nATENCION: Hay {len(liquidaciones)} liquidacion(es) en este periodo."

        resp = QMessageBox.warning(self, "Confirmar reapertura", mensaje, QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            user_id = auth_service.current_user.id if auth_service.current_user else None
            cierre_service.reabrir_cierre(cierre.id, user_id)
            self._cargar_cierres()
            QMessageBox.information(self, "OK", "Periodo reabierto.")

    def _editar_cierre(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccion", "Selecciona un cierre de la tabla.")
            return

        cierres = cierre_service.listar_cierres_asistencia()
        if row >= len(cierres):
            return
        cierre = cierres[row]

        from PySide6.QtWidgets import QDialog, QFormLayout
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Cierre")
        dialog.setFixedSize(400, 200)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        form = QHBoxLayout()
        form.setSpacing(8)

        form.addWidget(QLabel("Desde:"))
        edit_desde = QDateEdit()
        edit_desde.setMinimumHeight(34)
        edit_desde.setCalendarPopup(True)
        if cierre.fecha_desde:
            edit_desde.setDate(QDate(cierre.fecha_desde.year, cierre.fecha_desde.month, cierre.fecha_desde.day))
        form.addWidget(edit_desde)

        form.addWidget(QLabel("Hasta:"))
        edit_hasta = QDateEdit()
        edit_hasta.setMinimumHeight(34)
        edit_hasta.setCalendarPopup(True)
        if cierre.fecha_hasta:
            edit_hasta.setDate(QDate(cierre.fecha_hasta.year, cierre.fecha_hasta.month, cierre.fecha_hasta.day))
        form.addWidget(edit_hasta)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dialog.reject)
        btns.addWidget(btn_cancel)
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(dialog.accept)
        btns.addWidget(btn_save)
        layout.addLayout(btns)

        if dialog.exec() == QDialog.Accepted:
            nueva_desde = edit_desde.date().toPython()
            nueva_hasta = edit_hasta.date().toPython()
            if nueva_hasta <= nueva_desde:
                QMessageBox.warning(self, "Error", "Hasta debe ser posterior a Desde.")
                return
            try:
                from core.database import get_db
                from models.cierre import CierreAsistencia
                with get_db() as db:
                    c = db.query(CierreAsistencia).get(cierre.id)
                    if c:
                        c.fecha_desde = nueva_desde
                        c.fecha_hasta = nueva_hasta
                        c.periodo = nueva_desde.strftime("%Y-%m")
                        c.quincena = 1 if nueva_desde.day <= 15 else 2
                self._cargar_cierres()
                QMessageBox.information(self, "OK", "Cierre actualizado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _borrar_cierre(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccion", "Selecciona un cierre de la tabla.")
            return

        cierres = cierre_service.listar_cierres_asistencia()
        if row >= len(cierres):
            return
        cierre = cierres[row]

        resp = QMessageBox.warning(
            self, "Eliminar Cierre",
            f"Eliminar cierre {cierre.periodo} Q{cierre.quincena}?\nEsto no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            try:
                from core.database import get_db
                from models.cierre import CierreAsistencia
                with get_db() as db:
                    c = db.query(CierreAsistencia).get(cierre.id)
                    if c:
                        db.delete(c)
                self._cargar_cierres()
                QMessageBox.information(self, "OK", "Cierre eliminado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
