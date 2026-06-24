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
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Razon Social", "Nombre Fantasia", "CUIT/RIF", "Telefono", "Rubro", "Cond. Pago", "Calif."
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
            self.tabla.setItem(i, 5, QTableWidgetItem(p.condicion_pago))
            cal = "★" * (p.calificacion if hasattr(p, 'calificacion') and p.calificacion else 0)
            self.tabla.setItem(i, 6, QTableWidgetItem(cal or "-"))

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
        self.setMinimumWidth(650)
        self.setMinimumHeight(500)
        self._build_ui()
        if proveedor:
            self._cargar_datos()

    def _build_ui(self):
        from PySide6.QtWidgets import QTabWidget, QScrollArea
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        tabs = QTabWidget()

        # Tab 1: Datos Basicos + Fiscales
        tab1 = QWidget()
        t1_lay = QFormLayout(tab1)
        t1_lay.setSpacing(5)

        self._inputs = {}

        # Basicos
        for label, key in [("Razon Social:", "razon_social"), ("Nombre Fantasia:", "nombre_fantasia")]:
            inp = QLineEdit(); inp.setFixedHeight(26)
            t1_lay.addRow(label, inp)
            self._inputs[key] = inp

        # Fiscales
        t1_lay.addRow(QLabel("--- Datos Fiscales ---"))
        for label, key in [
            ("CUIT/RIF:", "cuit_rif"),
            ("Tipo Contribuyente:", "tipo_contribuyente"),
            ("Condicion IVA:", "condicion_iva"),
            ("Nro Ingresos Brutos:", "numero_ingresos_brutos"),
        ]:
            inp = QLineEdit(); inp.setFixedHeight(26)
            t1_lay.addRow(label, inp)
            self._inputs[key] = inp

        # Condiciones comerciales
        t1_lay.addRow(QLabel("--- Condiciones Comerciales ---"))
        for label, key in [
            ("Rubro:", "rubro"),
            ("Categoria:", "categoria"),
            ("Condicion de Pago:", "condicion_pago"),
            ("Dias de Pago:", "dias_pago"),
            ("Moneda:", "moneda"),
            ("Descuento Default %:", "descuento_default"),
        ]:
            inp = QLineEdit(); inp.setFixedHeight(26)
            t1_lay.addRow(label, inp)
            self._inputs[key] = inp

        tabs.addTab(tab1, "Datos y Fiscal")

        # Tab 2: Direccion + Contacto
        tab2 = QWidget()
        t2_lay = QFormLayout(tab2)
        t2_lay.setSpacing(5)

        for label, key in [
            ("Direccion:", "direccion"),
            ("Ciudad:", "ciudad"),
            ("Provincia/Estado:", "provincia_estado"),
            ("Codigo Postal:", "codigo_postal"),
            ("Pais:", "pais"),
            ("Telefono:", "telefono"),
            ("Celular:", "celular"),
            ("Email:", "email"),
            ("Web:", "web"),
        ]:
            inp = QLineEdit(); inp.setFixedHeight(26)
            t2_lay.addRow(label, inp)
            self._inputs[key] = inp

        t2_lay.addRow(QLabel("--- Contacto Principal ---"))
        for label, key in [
            ("Nombre Contacto:", "contacto_nombre"),
            ("Cargo:", "contacto_cargo"),
            ("Telefono Contacto:", "contacto_telefono"),
            ("Email Contacto:", "contacto_email"),
        ]:
            inp = QLineEdit(); inp.setFixedHeight(26)
            t2_lay.addRow(label, inp)
            self._inputs[key] = inp

        tabs.addTab(tab2, "Direccion y Contacto")

        # Tab 3: Banco + Evaluacion
        tab3 = QWidget()
        t3_lay = QFormLayout(tab3)
        t3_lay.setSpacing(5)

        t3_lay.addRow(QLabel("--- Datos Bancarios ---"))
        for label, key in [
            ("Banco:", "banco"),
            ("Tipo Cuenta:", "tipo_cuenta_banco"),
            ("Numero Cuenta:", "numero_cuenta"),
            ("CBU/CLABE:", "cbu_clabe"),
            ("Titular:", "titular_cuenta"),
        ]:
            inp = QLineEdit(); inp.setFixedHeight(26)
            t3_lay.addRow(label, inp)
            self._inputs[key] = inp

        t3_lay.addRow(QLabel("--- Evaluacion ---"))
        for label, key in [
            ("Calificacion (1-5):", "calificacion"),
            ("Cumplimiento Plazo:", "cumplimiento_plazo"),
        ]:
            inp = QLineEdit(); inp.setFixedHeight(26)
            t3_lay.addRow(label, inp)
            self._inputs[key] = inp

        t3_lay.addRow(QLabel("--- Notas ---"))
        self._input_notas = QTextEdit()
        self._input_notas.setMaximumHeight(80)
        t3_lay.addRow(self._input_notas)

        tabs.addTab(tab3, "Banco y Evaluacion")

        layout.addWidget(tabs)

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
            val = getattr(p, key, "") or ""
            inp.setText(str(val))
        self._input_notas.setPlainText(p.notas or "")

    def _guardar(self):
        razon = self._inputs["razon_social"].text().strip()
        if not razon:
            QMessageBox.warning(self, "Error", "La razon social es obligatoria.")
            return

        datos = {}
        for key, inp in self._inputs.items():
            val = inp.text().strip()
            # Convertir numericos
            if key == "dias_pago":
                datos[key] = int(val) if val.isdigit() else 0
            elif key in ("descuento_default",):
                try:
                    datos[key] = float(val) if val else 0.0
                except ValueError:
                    datos[key] = 0.0
            elif key == "calificacion":
                datos[key] = int(val) if val.isdigit() else 0
            else:
                datos[key] = val
        datos["notas"] = self._input_notas.toPlainText().strip()

        try:
            if self._proveedor:
                datos_service.actualizar_proveedor(self._proveedor.id, datos)
            else:
                datos_service.crear_proveedor(datos)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
