from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QMessageBox, QTextEdit,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.datos_service import datos_service


class ProveedoresView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Proveedores")
        title.setObjectName("title")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar por razon social, nombre o CUIT/RIF...")
        self._search.setFixedHeight(32)
        self._search.textChanged.connect(self._buscar)
        toolbar.addWidget(self._search)

        btn_nuevo = QPushButton("  Nuevo Proveedor")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(32)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self._nuevo)
        toolbar.addWidget(btn_nuevo)
        layout.addLayout(toolbar)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "Razon Social", "Nombre Fantasia", "CUIT/RIF", "Telefono", "Rubro", "Estado"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.doubleClicked.connect(self._editar_seleccionado)
        layout.addWidget(self.tabla, 1)

    def _cargar(self):
        proveedores = datos_service.listar_proveedores()
        self._poblar_tabla(proveedores)

    def _buscar(self, texto):
        if not texto:
            self._cargar()
            return
        self._poblar_tabla(datos_service.buscar_proveedores(texto))

    def _poblar_tabla(self, proveedores):
        self.tabla.setRowCount(len(proveedores))
        for i, p in enumerate(proveedores):
            self.tabla.setItem(i, 0, QTableWidgetItem(p.razon_social))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.nombre_fantasia))
            self.tabla.setItem(i, 2, QTableWidgetItem(p.cuit_rif))
            self.tabla.setItem(i, 3, QTableWidgetItem(p.telefono))
            self.tabla.setItem(i, 4, QTableWidgetItem(p.rubro))
            self.tabla.setItem(i, 5, QTableWidgetItem("Activo" if p.activo else "Inactivo"))

    def _nuevo(self):
        dlg = ProveedorDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()

    def _editar_seleccionado(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
        proveedores = datos_service.listar_proveedores()
        if row < len(proveedores):
            dlg = ProveedorDialog(proveedor=proveedores[row], parent=self)
            if dlg.exec() == QDialog.Accepted:
                self._cargar()


class ProveedorDialog(QDialog):
    def __init__(self, proveedor=None, parent=None):
        super().__init__(parent)
        self._proveedor = proveedor
        self.setWindowTitle("Editar Proveedor" if proveedor else "Nuevo Proveedor")
        self.setMinimumWidth(500)
        self._build_ui()
        if proveedor:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(6)

        campos = [
            ("Razon Social:", "razon_social", False),
            ("Nombre Fantasia:", "nombre_fantasia", False),
            ("CUIT/RIF:", "cuit_rif", False),
            ("Direccion:", "direccion", False),
            ("Ciudad:", "ciudad", False),
            ("Provincia/Estado:", "provincia_estado", False),
            ("Telefono:", "telefono", False),
            ("Celular:", "celular", False),
            ("Email:", "email", False),
            ("Web:", "web", False),
            ("Contacto:", "contacto", False),
            ("Rubro:", "rubro", False),
            ("Condicion de Pago:", "condicion_pago", False),
            ("Cuenta Bancaria:", "cuenta_bancaria", False),
        ]

        self._inputs = {}
        for label, key, _ in campos:
            inp = QLineEdit()
            inp.setFixedHeight(26)
            form.addRow(label, inp)
            self._inputs[key] = inp

        self._input_notas = QTextEdit()
        self._input_notas.setMaximumHeight(50)
        form.addRow("Notas:", self._input_notas)

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
        p = self._proveedor
        for key, inp in self._inputs.items():
            inp.setText(getattr(p, key, "") or "")
        self._input_notas.setPlainText(p.notas or "")

    def _guardar(self):
        razon = self._inputs["razon_social"].text().strip()
        if not razon:
            QMessageBox.warning(self, "Error", "La razon social es obligatoria.")
            return

        datos = {key: inp.text().strip() for key, inp in self._inputs.items()}
        datos["notas"] = self._input_notas.toPlainText().strip()

        try:
            if self._proveedor:
                datos_service.actualizar_proveedor(self._proveedor.id, datos)
            else:
                datos_service.crear_proveedor(datos)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
