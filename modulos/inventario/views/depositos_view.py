from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QComboBox, QMessageBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.inventario import inventario_service
from core.database import get_db
from models.sucursal import Sucursal


class DepositosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Depositos")
        title.setObjectName("title")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        btn_nuevo = QPushButton("  Nuevo Deposito")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(32)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self._nuevo)
        toolbar.addWidget(btn_nuevo)
        layout.addLayout(toolbar)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Nombre", "Direccion", "Sucursal", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.doubleClicked.connect(self._editar_seleccionado)
        layout.addWidget(self.tabla, 1)

    def _cargar(self):
        depositos = inventario_service.listar_depositos(solo_activos=False)
        self.tabla.setRowCount(len(depositos))
        for i, d in enumerate(depositos):
            self.tabla.setItem(i, 0, QTableWidgetItem(d.nombre))
            self.tabla.setItem(i, 1, QTableWidgetItem(d.direccion or ""))
            self.tabla.setItem(i, 2, QTableWidgetItem(d.sucursal.nombre if d.sucursal else "Sin asignar"))
            self.tabla.setItem(i, 3, QTableWidgetItem("Activo" if d.activo else "Inactivo"))

    def _nuevo(self):
        dlg = DepositoDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()

    def _editar_seleccionado(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
        depositos = inventario_service.listar_depositos(solo_activos=False)
        if row < len(depositos):
            dlg = DepositoDialog(deposito=depositos[row], parent=self)
            if dlg.exec() == QDialog.Accepted:
                self._cargar()


class DepositoDialog(QDialog):
    def __init__(self, deposito=None, parent=None):
        super().__init__(parent)
        self._deposito = deposito
        self.setWindowTitle("Editar Deposito" if deposito else "Nuevo Deposito")
        self.setMinimumWidth(400)
        self._build_ui()
        if deposito:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(8)

        self._input_nombre = QLineEdit()
        self._input_nombre.setFixedHeight(28)
        form.addRow("Nombre:", self._input_nombre)

        self._input_dir = QLineEdit()
        self._input_dir.setFixedHeight(28)
        form.addRow("Direccion:", self._input_dir)

        self._combo_suc = QComboBox()
        self._combo_suc.setFixedHeight(28)
        self._combo_suc.addItem("Sin asignar", None)
        with get_db() as db:
            for s in db.query(Sucursal).filter(Sucursal.activo == True).all():
                self._combo_suc.addItem(s.nombre, s.id)
        form.addRow("Sucursal:", self._combo_suc)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(32)
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setFixedHeight(32)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _cargar_datos(self):
        d = self._deposito
        self._input_nombre.setText(d.nombre)
        self._input_dir.setText(d.direccion or "")
        if d.sucursal_id:
            idx = self._combo_suc.findData(d.sucursal_id)
            if idx >= 0:
                self._combo_suc.setCurrentIndex(idx)

    def _guardar(self):
        nombre = self._input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return
        try:
            datos = {
                "nombre": nombre,
                "direccion": self._input_dir.text().strip(),
                "sucursal_id": self._combo_suc.currentData(),
            }
            if self._deposito:
                inventario_service.actualizar_deposito(self._deposito.id, datos)
            else:
                inventario_service.crear_deposito(**datos)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
