from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QMessageBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.facturador_config_service import facturador_config_service
from services.inventario_service import inventario_service
from core.database import get_db
from models.sucursal import Sucursal


class ConfigFacturadoresView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Configuracion de Facturadores")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Define los puntos de venta con su sucursal y depositos asignados.")
        subtitle.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(subtitle)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        btn_nuevo = QPushButton("  Nuevo Facturador")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(32)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self._nuevo)
        toolbar.addWidget(btn_nuevo)
        layout.addLayout(toolbar)

        self._tabla = QTableWidget()
        self._tabla.setColumnCount(4)
        self._tabla.setHorizontalHeaderLabels(["Codigo", "Nombre", "Sucursal", "Depositos"])
        self._tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._tabla.setAlternatingRowColors(True)
        self._tabla.verticalHeader().setVisible(False)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla.doubleClicked.connect(self._editar)
        layout.addWidget(self._tabla, 1)

    def _cargar(self):
        facturadores = facturador_config_service.listar()
        self._tabla.setRowCount(len(facturadores))
        for i, f in enumerate(facturadores):
            self._tabla.setItem(i, 0, QTableWidgetItem(f.codigo))
            self._tabla.setItem(i, 1, QTableWidgetItem(f.nombre or ""))
            # Sucursal
            suc_nombre = ""
            if f.sucursal_id:
                with get_db() as db:
                    suc = db.get(Sucursal, f.sucursal_id)
                    suc_nombre = suc.nombre if suc else ""
            self._tabla.setItem(i, 2, QTableWidgetItem(suc_nombre))
            # Depositos
            dep_nombres = []
            if f.depositos_ids:
                depositos = inventario_service.listar_depositos()
                ids = [int(x) for x in f.depositos_ids.split(",") if x.strip().isdigit()]
                for d in depositos:
                    if d.id in ids:
                        dep_nombres.append(d.nombre)
            self._tabla.setItem(i, 3, QTableWidgetItem(", ".join(dep_nombres)))

    def _nuevo(self):
        dlg = FacturadorDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()

    def _editar(self):
        row = self._tabla.currentRow()
        if row < 0:
            return
        facturadores = facturador_config_service.listar()
        if row < len(facturadores):
            dlg = FacturadorDialog(facturador=facturadores[row], parent=self)
            if dlg.exec() == QDialog.Accepted:
                self._cargar()


class FacturadorDialog(QDialog):
    def __init__(self, facturador=None, parent=None):
        super().__init__(parent)
        self._facturador = facturador
        self.setWindowTitle("Editar Facturador" if facturador else "Nuevo Facturador")
        self.setMinimumWidth(450)
        self._build_ui()
        if facturador:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(8)

        self._input_codigo = QLineEdit()
        self._input_codigo.setFixedHeight(28)
        self._input_codigo.setPlaceholderText("Ej: F01, F02, CAJA1")
        form.addRow("Codigo:", self._input_codigo)

        self._input_nombre = QLineEdit()
        self._input_nombre.setFixedHeight(28)
        self._input_nombre.setPlaceholderText("Ej: Caja Principal")
        form.addRow("Nombre:", self._input_nombre)

        self._combo_sucursal = QComboBox()
        self._combo_sucursal.setFixedHeight(28)
        self._combo_sucursal.addItem("Sin asignar", None)
        with get_db() as db:
            for s in db.query(Sucursal).filter(Sucursal.activo == True).all():
                self._combo_sucursal.addItem(s.nombre, s.id)
        form.addRow("Sucursal:", self._combo_sucursal)

        # Depositos (seleccion multiple con checkboxes simulado)
        self._input_depositos = QLineEdit()
        self._input_depositos.setFixedHeight(28)
        self._input_depositos.setPlaceholderText("IDs separados por coma: 1,3,5")

        # Mostrar depositos disponibles como ayuda
        depositos = inventario_service.listar_depositos()
        dep_help = ", ".join([f"{d.id}={d.nombre}" for d in depositos])

        form.addRow("Depositos IDs:", self._input_depositos)

        lbl_help = QLabel(f"Disponibles: {dep_help}" if dep_help else "No hay depositos creados")
        lbl_help.setStyleSheet("font-size: 10px; color: #888;")
        lbl_help.setWordWrap(True)
        form.addRow("", lbl_help)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(30)
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setFixedHeight(30)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _cargar_datos(self):
        f = self._facturador
        self._input_codigo.setText(f.codigo)
        self._input_nombre.setText(f.nombre or "")
        if f.sucursal_id:
            idx = self._combo_sucursal.findData(f.sucursal_id)
            if idx >= 0:
                self._combo_sucursal.setCurrentIndex(idx)
        self._input_depositos.setText(f.depositos_ids or "")

    def _guardar(self):
        codigo = self._input_codigo.text().strip().upper()
        if not codigo:
            QMessageBox.warning(self, "Error", "El codigo es obligatorio.")
            return

        datos = {
            "codigo": codigo,
            "nombre": self._input_nombre.text().strip(),
            "sucursal_id": self._combo_sucursal.currentData(),
            "depositos_ids": self._input_depositos.text().strip(),
        }

        try:
            if self._facturador:
                facturador_config_service.actualizar(self._facturador.id, datos)
            else:
                facturador_config_service.crear(**datos)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
