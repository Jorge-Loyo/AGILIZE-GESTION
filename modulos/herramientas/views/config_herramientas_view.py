from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QGroupBox, QMessageBox, QFrame,
    QScrollArea, QSpinBox, QDoubleSpinBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.empresa_service import empresa_service


# Claves de configuracion en BD
CONFIG_KEYS = {
    "iva_porcentaje": "16.00",
    "col_codigo": "0",
    "col_descripcion": "1",
    "col_costo": "8",
    "col_precio_con_iva": "16",
    "col_porcentaje_utilidad": "20",
    "col_stock": "25",
    "moneda_simbolo": "Bs.",
    "moneda_nombre": "Bolivares",
}


class ConfigHerramientasView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._inputs = {}
        self._build_ui()
        self._cargar_valores()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        page = QWidget()
        page.setMaximumWidth(600)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(14)

        title = QLabel("Configuracion - Herramientas")
        title.setObjectName("title")
        layout.addWidget(title)

        GRP_STYLE = "QGroupBox { font-weight: bold; font-size: 12px; padding-top: 14px; margin-top: 4px; }"

        # --- IVA y Moneda ---
        grp_fiscal = QGroupBox("Impuestos y Moneda")
        grp_fiscal.setStyleSheet(GRP_STYLE)
        fiscal_layout = QGridLayout(grp_fiscal)
        fiscal_layout.setSpacing(8)
        fiscal_layout.setColumnStretch(1, 1)
        fiscal_layout.setColumnStretch(3, 1)

        # IVA
        fiscal_layout.addWidget(QLabel("IVA (%):"), 0, 0)
        self._input_iva = QDoubleSpinBox()
        self._input_iva.setRange(0, 100)
        self._input_iva.setDecimals(2)
        self._input_iva.setSingleStep(0.5)
        self._input_iva.setFixedHeight(28)
        fiscal_layout.addWidget(self._input_iva, 0, 1)

        # Moneda simbolo
        fiscal_layout.addWidget(QLabel("Simbolo moneda:"), 0, 2)
        self._input_moneda_simbolo = QLineEdit()
        self._input_moneda_simbolo.setFixedHeight(28)
        self._input_moneda_simbolo.setPlaceholderText("Ej: Bs., $, AR$")
        fiscal_layout.addWidget(self._input_moneda_simbolo, 0, 3)

        # Moneda nombre
        fiscal_layout.addWidget(QLabel("Nombre moneda:"), 1, 0)
        self._input_moneda_nombre = QLineEdit()
        self._input_moneda_nombre.setFixedHeight(28)
        self._input_moneda_nombre.setPlaceholderText("Ej: Bolivares, Pesos")
        fiscal_layout.addWidget(self._input_moneda_nombre, 1, 1)

        # Formula
        self._lbl_formula = QLabel("")
        self._lbl_formula.setStyleSheet("font-size: 11px; color: #888; font-style: italic;")
        fiscal_layout.addWidget(self._lbl_formula, 2, 0, 1, 4)

        self._input_iva.valueChanged.connect(self._actualizar_formula)

        layout.addWidget(grp_fiscal)

        # --- Mapeo de columnas ---
        grp_cols = QGroupBox("Mapeo de Columnas del Excel")
        grp_cols.setStyleSheet(GRP_STYLE)
        cols_layout = QGridLayout(grp_cols)
        cols_layout.setSpacing(8)
        cols_layout.setColumnStretch(1, 1)
        cols_layout.setColumnStretch(3, 1)

        hint = QLabel("Indice de columna en el archivo Excel (empieza en 0)")
        hint.setStyleSheet("font-size: 10px; color: #888; font-weight: normal;")
        cols_layout.addWidget(hint, 0, 0, 1, 4)

        columnas = [
            ("Codigo:", "col_codigo", 1, 0),
            ("Descripcion:", "col_descripcion", 1, 2),
            ("Costo:", "col_costo", 2, 0),
            ("Precio con IVA:", "col_precio_con_iva", 2, 2),
            ("% Utilidad:", "col_porcentaje_utilidad", 3, 0),
            ("Stock:", "col_stock", 3, 2),
        ]

        self._col_inputs = {}
        for label, key, row, col in columnas:
            lbl = QLabel(label)
            lbl.setStyleSheet("font-weight: normal;")
            cols_layout.addWidget(lbl, row, col)
            spin = QSpinBox()
            spin.setRange(0, 100)
            spin.setFixedHeight(28)
            cols_layout.addWidget(spin, row, col + 1)
            self._col_inputs[key] = spin

        layout.addWidget(grp_cols)

        # --- Boton guardar ---
        save_row = QHBoxLayout()
        save_row.addStretch()
        btn_guardar = QPushButton("  Guardar configuracion")
        btn_guardar.setIcon(qta.icon("fa5s.save", color="#10b981"))
        btn_guardar.setFixedHeight(34)
        btn_guardar.setFixedWidth(200)
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.clicked.connect(self._guardar)
        save_row.addWidget(btn_guardar)
        layout.addLayout(save_row)

        # --- Info ---
        info_grp = QGroupBox("Informacion")
        info_grp.setStyleSheet(GRP_STYLE)
        info_layout = QVBoxLayout(info_grp)
        info_layout.setSpacing(4)

        info_text = QLabel(
            "Estos valores se usan al procesar archivos Excel en el Limpiador de Productos.\n\n"
            "- IVA: se usa para calcular Precio sin IVA = Precio con IVA / (1 + IVA/100)\n"
            "- Columnas: indican en que columna del Excel esta cada dato (0 = primera columna)\n"
            "- Moneda: simbolo que se muestra en los indicadores"
        )
        info_text.setStyleSheet("font-size: 11px; color: #aaa; font-weight: normal;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_grp)

        layout.addStretch()

        # Centrar
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(page)
        wrapper_layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(wrapper)
        main_layout.addWidget(scroll)

    def _cargar_valores(self):
        datos = empresa_service.obtener_todos()

        iva = float(datos.get("iva_porcentaje", CONFIG_KEYS["iva_porcentaje"]))
        self._input_iva.setValue(iva)

        self._input_moneda_simbolo.setText(datos.get("moneda_simbolo", CONFIG_KEYS["moneda_simbolo"]))
        self._input_moneda_nombre.setText(datos.get("moneda_nombre", CONFIG_KEYS["moneda_nombre"]))

        for key, spin in self._col_inputs.items():
            val = int(datos.get(key, CONFIG_KEYS[key]))
            spin.setValue(val)

        self._actualizar_formula()

    def _actualizar_formula(self):
        iva = self._input_iva.value()
        factor = 1 + iva / 100
        self._lbl_formula.setText(
            f"Formula: Precio sin IVA = Precio con IVA / {factor:.4f}"
        )

    def _guardar(self):
        datos = {
            "iva_porcentaje": f"{self._input_iva.value():.2f}",
            "moneda_simbolo": self._input_moneda_simbolo.text().strip(),
            "moneda_nombre": self._input_moneda_nombre.text().strip(),
        }
        for key, spin in self._col_inputs.items():
            datos[key] = str(spin.value())

        try:
            empresa_service.guardar_multiples(datos)
            QMessageBox.information(self, "OK", "Configuracion guardada correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
