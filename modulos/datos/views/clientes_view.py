from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QComboBox, QMessageBox, QTextEdit,
    QDoubleSpinBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.datos.datos_service import datos_service


class ClientesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Clientes")
        title.setObjectName("title")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar por razon social, nombre, CUIT/RIF o documento...")
        self._search.setFixedHeight(32)
        self._search.textChanged.connect(self._buscar)
        toolbar.addWidget(self._search)

        btn_nuevo = QPushButton("  Nuevo Cliente")
        btn_nuevo.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nuevo.setFixedHeight(32)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self._nuevo)
        toolbar.addWidget(btn_nuevo)
        layout.addLayout(toolbar)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Razon Social", "Nombre Fantasia", "CUIT/RIF", "Telefono", "Categoria", "Saldo", "Estado"
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
        clientes = datos_service.listar_clientes()
        self._poblar_tabla(clientes)

    def _buscar(self, texto):
        if not texto:
            self._cargar()
            return
        self._poblar_tabla(datos_service.buscar_clientes(texto))

    def _poblar_tabla(self, clientes):
        self.tabla.setRowCount(len(clientes))
        for i, c in enumerate(clientes):
            self.tabla.setItem(i, 0, QTableWidgetItem(c.razon_social))
            self.tabla.setItem(i, 1, QTableWidgetItem(c.nombre_fantasia))
            self.tabla.setItem(i, 2, QTableWidgetItem(c.cuit_rif))
            self.tabla.setItem(i, 3, QTableWidgetItem(c.telefono))
            self.tabla.setItem(i, 4, QTableWidgetItem(c.categoria))
            saldo_item = QTableWidgetItem(f"{c.saldo:,.2f}")
            saldo_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 5, saldo_item)
            self.tabla.setItem(i, 6, QTableWidgetItem("Activo" if c.activo else "Inactivo"))

    def _nuevo(self):
        dlg = ClienteDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()

    def _editar_seleccionado(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
        clientes = datos_service.listar_clientes()
        if row < len(clientes):
            dlg = ClienteDialog(cliente=clientes[row], parent=self)
            if dlg.exec() == QDialog.Accepted:
                self._cargar()


class ClienteDialog(QDialog):
    def __init__(self, cliente=None, parent=None):
        super().__init__(parent)
        self._cliente = cliente
        self.setWindowTitle("Editar Cliente" if cliente else "Nuevo Cliente")
        self.setMinimumWidth(500)
        self._build_ui()
        if cliente:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(6)

        campos = [
            ("Razon Social:", "razon_social"),
            ("Nombre Fantasia:", "nombre_fantasia"),
            ("CUIT/RIF:", "cuit_rif"),
            ("Direccion:", "direccion"),
            ("Ciudad:", "ciudad"),
            ("Provincia/Estado:", "provincia_estado"),
            ("Telefono:", "telefono"),
            ("Celular:", "celular"),
            ("Email:", "email"),
            ("Contacto:", "contacto"),
            ("Condicion de Pago:", "condicion_pago"),
        ]

        self._inputs = {}
        for label, key in campos:
            inp = QLineEdit()
            inp.setFixedHeight(26)
            form.addRow(label, inp)
            self._inputs[key] = inp

        # Tipo documento
        self._combo_tipo_doc = QComboBox()
        self._combo_tipo_doc.setFixedHeight(26)
        self._combo_tipo_doc.addItems(["", "DNI", "CUIT", "RIF", "CI", "Pasaporte", "Otro"])
        form.addRow("Tipo Documento:", self._combo_tipo_doc)

        self._input_nro_doc = QLineEdit()
        self._input_nro_doc.setFixedHeight(26)
        form.addRow("Nro Documento:", self._input_nro_doc)

        # Categoria
        self._combo_cat = QComboBox()
        self._combo_cat.setFixedHeight(26)
        self._combo_cat.addItems(["", "Minorista", "Mayorista", "VIP", "Corporativo"])
        self._combo_cat.setEditable(True)
        form.addRow("Categoria:", self._combo_cat)

        # Limite credito
        self._input_limite = QDoubleSpinBox()
        self._input_limite.setRange(0, 99999999)
        self._input_limite.setDecimals(2)
        self._input_limite.setFixedHeight(26)
        form.addRow("Limite Credito:", self._input_limite)

        # Notas
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
        c = self._cliente
        for key, inp in self._inputs.items():
            inp.setText(getattr(c, key, "") or "")
        self._combo_tipo_doc.setCurrentText(c.tipo_documento or "")
        self._input_nro_doc.setText(c.numero_documento or "")
        self._combo_cat.setCurrentText(c.categoria or "")
        self._input_limite.setValue(c.limite_credito or 0)
        self._input_notas.setPlainText(c.notas or "")

    def _guardar(self):
        razon = self._inputs["razon_social"].text().strip()
        if not razon:
            QMessageBox.warning(self, "Error", "La razon social es obligatoria.")
            return

        datos = {key: inp.text().strip() for key, inp in self._inputs.items()}
        datos["tipo_documento"] = self._combo_tipo_doc.currentText()
        datos["numero_documento"] = self._input_nro_doc.text().strip()
        datos["categoria"] = self._combo_cat.currentText()
        datos["limite_credito"] = self._input_limite.value()
        datos["notas"] = self._input_notas.toPlainText().strip()

        try:
            if self._cliente:
                datos_service.actualizar_cliente(self._cliente.id, datos)
            else:
                datos_service.crear_cliente(datos)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
