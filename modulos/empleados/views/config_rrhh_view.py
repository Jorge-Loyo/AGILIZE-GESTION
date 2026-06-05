from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QTabWidget, QFileDialog,
    QMessageBox, QComboBox, QDoubleSpinBox, QGroupBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QCheckBox,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from decimal import Decimal
from pathlib import Path
import shutil
from services.nomina_service import nomina_service
from modulos.empleados.views.editar_concepto_dialog import EditarConceptoDialog
from services.config_nomina_service import config_nomina_service
from services.permiso_ausencia_service import permiso_ausencia_service
from services.empresa_service import empresa_service
from core.config import BASE_DIR


class ConfigRRHHView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        title = QLabel("Configuracion de RRHH")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addSpacing(12)

        tabs = QTabWidget()
        tabs.addTab(self._build_multiplicadores_tab(), "Valor Hora Extra")
        tabs.addTab(self._build_sac_tab(), "SAC")
        tabs.addTab(self._build_conceptos_tab(), "Conceptos Nomina")
        tabs.addTab(self._build_permisos_tab(), "Tipos de Permiso")
        layout.addWidget(tabs)

    # === TAB MULTIPLICADORES ===
    def _build_multiplicadores_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Configuracion de multiplicadores para el calculo de horas en liquidacion."))

        form = QGridLayout()
        form.setSpacing(10)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        form.addWidget(QLabel("Hora Extra:"), 0, 0)
        self.spin_extra = QDoubleSpinBox()
        self.spin_extra.setMinimumHeight(32)
        self.spin_extra.setRange(1, 5)
        self.spin_extra.setDecimals(2)
        self.spin_extra.setSuffix("x")
        form.addWidget(self.spin_extra, 0, 1)

        form.addWidget(QLabel("Hora Sabado:"), 0, 2)
        self.spin_sabado = QDoubleSpinBox()
        self.spin_sabado.setMinimumHeight(32)
        self.spin_sabado.setRange(1, 5)
        self.spin_sabado.setDecimals(2)
        self.spin_sabado.setSuffix("x")
        form.addWidget(self.spin_sabado, 0, 3)

        form.addWidget(QLabel("Hora Domingo:"), 1, 0)
        self.spin_domingo = QDoubleSpinBox()
        self.spin_domingo.setMinimumHeight(32)
        self.spin_domingo.setRange(1, 5)
        self.spin_domingo.setDecimals(2)
        self.spin_domingo.setSuffix("x")
        form.addWidget(self.spin_domingo, 1, 1)

        form.addWidget(QLabel("Hora Feriado:"), 1, 2)
        self.spin_feriado = QDoubleSpinBox()
        self.spin_feriado.setMinimumHeight(32)
        self.spin_feriado.setRange(1, 5)
        self.spin_feriado.setDecimals(2)
        self.spin_feriado.setSuffix("x")
        form.addWidget(self.spin_feriado, 1, 3)

        layout.addLayout(form)

        lbl_info = QLabel("Ej: 1.50x = 50% mas sobre valor hora base. 2.00x = 100% mas.")
        lbl_info.setObjectName("subtitle")
        layout.addWidget(lbl_info)

        btn = QPushButton("Guardar Multiplicadores")
        btn.setMinimumHeight(36)
        btn.clicked.connect(self._guardar_multiplicadores)
        layout.addWidget(btn)
        layout.addStretch()

        self._cargar_multiplicadores()
        return page

    def _cargar_multiplicadores(self):
        params = config_nomina_service.obtener_todos()
        self.spin_extra.setValue(float(params.get("mult_hora_extra", Decimal("1.5"))))
        self.spin_sabado.setValue(float(params.get("mult_hora_sabado", Decimal("1.5"))))
        self.spin_domingo.setValue(float(params.get("mult_hora_domingo", Decimal("2.0"))))
        self.spin_feriado.setValue(float(params.get("mult_hora_feriado", Decimal("2.0"))))

    def _guardar_multiplicadores(self):
        try:
            config_nomina_service.guardar("mult_hora_extra", Decimal(str(self.spin_extra.value())))
            config_nomina_service.guardar("mult_hora_sabado", Decimal(str(self.spin_sabado.value())))
            config_nomina_service.guardar("mult_hora_domingo", Decimal(str(self.spin_domingo.value())))
            config_nomina_service.guardar("mult_hora_feriado", Decimal(str(self.spin_feriado.value())))
            QMessageBox.information(self, "OK", "Multiplicadores guardados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === TAB SAC ===
    def _build_sac_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Metodo de calculo del Sueldo Anual Complementario (Aguinaldo)."))

        self.radio_mayor = QRadioButton("50% de la mayor remuneracion mensual del semestre (metodo legal)")
        self.radio_mayor.setChecked(True)
        layout.addWidget(self.radio_mayor)

        self.radio_promedio = QRadioButton("50% del promedio de los 6 meses del semestre")
        layout.addWidget(self.radio_promedio)

        layout.addStretch()
        return page

    # === TAB CONCEPTOS ===
    def _build_conceptos_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form = QGridLayout()
        form.setSpacing(8)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        form.addWidget(QLabel("Codigo:"), 0, 0)
        self.concepto_codigo = QLineEdit()
        self.concepto_codigo.setMinimumHeight(32)
        self.concepto_codigo.setPlaceholderText("Ej: VIAT")
        form.addWidget(self.concepto_codigo, 0, 1)

        form.addWidget(QLabel("Nombre:"), 0, 2)
        self.concepto_nombre = QLineEdit()
        self.concepto_nombre.setMinimumHeight(32)
        self.concepto_nombre.setPlaceholderText("Ej: Viaticos")
        form.addWidget(self.concepto_nombre, 0, 3)

        form.addWidget(QLabel("Tipo:"), 1, 0)
        self.concepto_tipo = QComboBox()
        self.concepto_tipo.setMinimumHeight(32)
        self.concepto_tipo.addItems(["haber", "deduccion"])
        form.addWidget(self.concepto_tipo, 1, 1)

        form.addWidget(QLabel("Calculo:"), 1, 2)
        self.concepto_calculo = QComboBox()
        self.concepto_calculo.setMinimumHeight(32)
        self.concepto_calculo.addItem("Porcentaje sobre bruto", "porcentaje")
        self.concepto_calculo.addItem("Monto fijo", "fijo")
        self.concepto_calculo.addItem("Monto por dia trabajado", "por_dia")
        self.concepto_calculo.currentIndexChanged.connect(self._on_calculo_changed)
        form.addWidget(self.concepto_calculo, 1, 3)

        self.lbl_valor = QLabel("Porcentaje:")
        form.addWidget(self.lbl_valor, 2, 0)
        self.concepto_valor = QDoubleSpinBox()
        self.concepto_valor.setMinimumHeight(32)
        self.concepto_valor.setRange(0, 100)
        self.concepto_valor.setDecimals(2)
        self.concepto_valor.setSuffix(" %")
        form.addWidget(self.concepto_valor, 2, 1)

        self.lbl_valor_info = QLabel("Se aplica sobre el sueldo bruto")
        self.lbl_valor_info.setObjectName("subtitle")
        form.addWidget(self.lbl_valor_info, 2, 2, 1, 2)

        btn_agregar = QPushButton("Agregar Concepto")
        btn_agregar.setMinimumHeight(34)
        btn_agregar.clicked.connect(self._agregar_concepto)
        form.addWidget(btn_agregar, 3, 3)

        layout.addLayout(form)

        self.tabla_conceptos = QTableWidget()
        self.tabla_conceptos.setColumnCount(5)
        self.tabla_conceptos.setHorizontalHeaderLabels(["Codigo", "Nombre", "Tipo", "Calculo", "Valor"])
        self.tabla_conceptos.horizontalHeader().setStretchLastSection(True)
        self.tabla_conceptos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_conceptos.setAlternatingRowColors(True)
        self.tabla_conceptos.verticalHeader().setVisible(False)
        self.tabla_conceptos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_conceptos)

        self.tabla_conceptos.doubleClicked.connect(self._editar_concepto_dblclick)

        btn_editar_concepto = QPushButton("Editar Seleccionado")
        btn_editar_concepto.setMinimumHeight(34)
        btn_editar_concepto.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_editar_concepto.clicked.connect(self._editar_concepto)
        layout.addWidget(btn_editar_concepto)

        self._cargar_conceptos()
        return page

    def _editar_concepto_dblclick(self, index):
        row = index.row()
        self._abrir_editor_concepto(row)

    def _editar_concepto(self):
        row = self.tabla_conceptos.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccion", "Selecciona un concepto.")
            return
        self._abrir_editor_concepto(row)

    def _abrir_editor_concepto(self, row):
        conceptos = nomina_service.listar_conceptos(solo_activos=False)
        if row >= len(conceptos):
            return
        concepto_id = conceptos[row].id
        dialog = EditarConceptoDialog(concepto_id, parent=self)
        dialog.concepto_actualizado.connect(self._cargar_conceptos)
        dialog.exec()

    def _on_calculo_changed(self):
        calculo = self.concepto_calculo.currentData()
        self.concepto_valor.setPrefix("")
        self.concepto_valor.setSuffix("")
        if calculo == "porcentaje":
            self.lbl_valor.setText("Porcentaje:")
            self.concepto_valor.setSuffix(" %")
            self.concepto_valor.setRange(0, 100)
            self.lbl_valor_info.setText("Se aplica sobre el sueldo bruto")
        elif calculo == "fijo":
            self.lbl_valor.setText("Monto fijo:")
            self.concepto_valor.setPrefix("$ ")
            self.concepto_valor.setRange(0, 9999999)
            self.lbl_valor_info.setText("Valor fijo por liquidacion")
        elif calculo == "por_dia":
            self.lbl_valor.setText("Monto/dia:")
            self.concepto_valor.setPrefix("$ ")
            self.concepto_valor.setRange(0, 9999999)
            self.lbl_valor_info.setText("Se multiplica por dias trabajados del periodo")

    def _cargar_conceptos(self):
        conceptos = nomina_service.listar_conceptos(solo_activos=False)
        self.tabla_conceptos.setRowCount(len(conceptos))
        calculo_labels = {"porcentaje": "% sobre bruto", "fijo": "Monto fijo", "por_dia": "Por dia trabajado"}
        for i, c in enumerate(conceptos):
            calculo_tipo = getattr(c, 'calculo', None) or 'porcentaje'
            if c.porcentaje:
                valor_str = f"{c.porcentaje}%"
            elif c.monto_fijo:
                valor_str = f"$ {c.monto_fijo:,.2f}"
            else:
                valor_str = ""
            self.tabla_conceptos.setItem(i, 0, QTableWidgetItem(c.codigo))
            self.tabla_conceptos.setItem(i, 1, QTableWidgetItem(c.nombre))
            self.tabla_conceptos.setItem(i, 2, QTableWidgetItem(c.tipo.capitalize()))
            self.tabla_conceptos.setItem(i, 3, QTableWidgetItem(calculo_labels.get(calculo_tipo, calculo_tipo)))
            self.tabla_conceptos.setItem(i, 4, QTableWidgetItem(valor_str))

    def _agregar_concepto(self):
        codigo = self.concepto_codigo.text().strip().upper()
        nombre = self.concepto_nombre.text().strip()
        tipo = self.concepto_tipo.currentText()
        calculo = self.concepto_calculo.currentData()
        valor = self.concepto_valor.value()

        if not codigo or not nombre:
            QMessageBox.warning(self, "Error", "Codigo y Nombre son obligatorios.")
            return
        if valor == 0:
            QMessageBox.warning(self, "Error", "Ingresa un valor.")
            return

        datos = {
            "codigo": codigo,
            "nombre": nombre,
            "tipo": tipo,
            "calculo": calculo,
            "porcentaje": Decimal(str(valor)) if calculo == "porcentaje" else None,
            "monto_fijo": Decimal(str(valor)) if calculo in ("fijo", "por_dia") else None,
        }

        try:
            nomina_service.crear_concepto(datos)
            self.concepto_codigo.clear()
            self.concepto_nombre.clear()
            self.concepto_valor.setValue(0)
            self._cargar_conceptos()
            QMessageBox.information(self, "OK", "Concepto creado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === TAB TIPOS DE PERMISO ===
    def _build_permisos_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form = QGridLayout()
        form.setSpacing(8)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        form.addWidget(QLabel("Nombre:"), 0, 0)
        self.tipo_perm_nombre = QLineEdit()
        self.tipo_perm_nombre.setMinimumHeight(32)
        self.tipo_perm_nombre.setPlaceholderText("Ej: Licencia por enfermedad")
        form.addWidget(self.tipo_perm_nombre, 0, 1)

        self.tipo_perm_goce = QCheckBox("Con goce de sueldo")
        self.tipo_perm_goce.setChecked(True)
        form.addWidget(self.tipo_perm_goce, 0, 2)

        form.addWidget(QLabel("Dias max/anio:"), 1, 0)
        self.tipo_perm_dias = QSpinBox()
        self.tipo_perm_dias.setMinimumHeight(32)
        self.tipo_perm_dias.setRange(0, 365)
        self.tipo_perm_dias.setSpecialValueText("Sin limite")
        form.addWidget(self.tipo_perm_dias, 1, 1)

        btn_tipo_perm = QPushButton("Agregar Tipo")
        btn_tipo_perm.setMinimumHeight(34)
        btn_tipo_perm.clicked.connect(self._agregar_tipo_permiso)
        form.addWidget(btn_tipo_perm, 1, 3)

        layout.addLayout(form)

        self.tabla_tipos_permiso = QTableWidget()
        self.tabla_tipos_permiso.setColumnCount(3)
        self.tabla_tipos_permiso.setHorizontalHeaderLabels(["Nombre", "Con Goce", "Dias Max"])
        self.tabla_tipos_permiso.horizontalHeader().setStretchLastSection(True)
        self.tabla_tipos_permiso.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_tipos_permiso.setAlternatingRowColors(True)
        self.tabla_tipos_permiso.verticalHeader().setVisible(False)
        self.tabla_tipos_permiso.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_tipos_permiso)

        self._cargar_tipos_permiso()
        return page

    def _cargar_tipos_permiso(self):
        tipos = permiso_ausencia_service.listar_tipos()
        self.tabla_tipos_permiso.setRowCount(len(tipos))
        for i, t in enumerate(tipos):
            self.tabla_tipos_permiso.setItem(i, 0, QTableWidgetItem(t.nombre))
            self.tabla_tipos_permiso.setItem(i, 1, QTableWidgetItem("Si" if t.con_goce else "No"))
            self.tabla_tipos_permiso.setItem(i, 2, QTableWidgetItem(str(t.dias_max) if t.dias_max else "Sin limite"))

    def _agregar_tipo_permiso(self):
        nombre = self.tipo_perm_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return
        con_goce = self.tipo_perm_goce.isChecked()
        dias_max = self.tipo_perm_dias.value() or None
        try:
            permiso_ausencia_service.crear_tipo(nombre, con_goce, dias_max)
            self.tipo_perm_nombre.clear()
            self.tipo_perm_dias.setValue(0)
            self._cargar_tipos_permiso()
            QMessageBox.information(self, "OK", "Tipo de permiso creado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === TAB DATOS EMPRESA ===
    def _build_empresa_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Datos legales e informativos de la empresa."))

        form = QGridLayout()
        form.setSpacing(8)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        campos = [
            ("Razon Social:", "razon_social", 0, 0),
            ("CUIT:", "cuit", 0, 2),
            ("Direccion:", "direccion", 1, 0),
            ("Localidad:", "localidad", 1, 2),
            ("Provincia:", "provincia", 2, 0),
            ("Telefono:", "telefono", 2, 2),
            ("Email:", "email_empresa", 3, 0),
            ("Actividad:", "actividad", 3, 2),
            ("Convenio Colectivo:", "convenio_colectivo", 4, 0),
            ("Nro Establecimiento:", "nro_establecimiento", 4, 2),
        ]

        self._empresa_inputs = {}
        datos = empresa_service.obtener_todos()

        for label, clave, row, col in campos:
            form.addWidget(QLabel(label), row, col)
            inp = QLineEdit()
            inp.setMinimumHeight(32)
            inp.setText(datos.get(clave, ""))
            form.addWidget(inp, row, col + 1)
            self._empresa_inputs[clave] = inp

        layout.addLayout(form)

        btn = QPushButton("Guardar Datos Empresa")
        btn.setMinimumHeight(36)
        btn.clicked.connect(self._guardar_empresa)
        layout.addWidget(btn)
        layout.addStretch()
        return page

    def _guardar_empresa(self):
        datos = {clave: inp.text().strip() for clave, inp in self._empresa_inputs.items()}
        try:
            empresa_service.guardar_multiples(datos)
            QMessageBox.information(self, "OK", "Datos de empresa guardados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === TAB VISUAL ===
    def _build_visual_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Configuracion visual de la aplicacion."))

        form = QGridLayout()
        form.setSpacing(8)
        form.setColumnStretch(1, 1)

        datos = empresa_service.obtener_todos()

        form.addWidget(QLabel("Nombre de la App:"), 0, 0)
        self.input_nombre_app = QLineEdit()
        self.input_nombre_app.setMinimumHeight(32)
        self.input_nombre_app.setText(datos.get("nombre_app", "Agilize Gestion"))
        form.addWidget(self.input_nombre_app, 0, 1)

        form.addWidget(QLabel("Logo:"), 1, 0)
        logo_row = QHBoxLayout()
        self.lbl_logo_path = QLabel(datos.get("logo_path", "Sin logo cargado"))
        self.lbl_logo_path.setObjectName("subtitle")
        logo_row.addWidget(self.lbl_logo_path)

        btn_logo = QPushButton("Seleccionar Logo")
        btn_logo.setMinimumHeight(32)
        btn_logo.clicked.connect(self._seleccionar_logo)
        logo_row.addWidget(btn_logo)
        form.addLayout(logo_row, 1, 1)

        # Preview logo
        self.lbl_logo_preview = QLabel()
        self.lbl_logo_preview.setFixedSize(150, 150)
        self.lbl_logo_preview.setAlignment(Qt.AlignCenter)
        self.lbl_logo_preview.setStyleSheet("border: 1px solid #333; border-radius: 8px;")
        logo_actual = datos.get("logo_path", "")
        if logo_actual and Path(logo_actual).exists():
            pixmap = QPixmap(logo_actual).scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_logo_preview.setPixmap(pixmap)
        form.addWidget(self.lbl_logo_preview, 2, 1)

        layout.addLayout(form)

        btn = QPushButton("Guardar Visual")
        btn.setMinimumHeight(36)
        btn.clicked.connect(self._guardar_visual)
        layout.addWidget(btn)
        layout.addStretch()
        return page

    def _seleccionar_logo(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Logo", "", "Imagenes (*.png *.jpg *.jpeg *.svg *.ico)"
        )
        if filepath:
            # Copiar a assets/logos
            dest = BASE_DIR / "assets" / "logos" / Path(filepath).name
            shutil.copy2(filepath, str(dest))
            self.lbl_logo_path.setText(str(dest))
            pixmap = QPixmap(str(dest)).scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_logo_preview.setPixmap(pixmap)

    def _guardar_visual(self):
        datos = {
            "nombre_app": self.input_nombre_app.text().strip(),
            "logo_path": self.lbl_logo_path.text(),
        }
        try:
            empresa_service.guardar_multiples(datos)
            QMessageBox.information(self, "OK", "Configuracion visual guardada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === TAB DESARROLLADOR ===
    def _build_desarrollador_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Datos de la empresa desarrolladora del sistema."))

        form = QGridLayout()
        form.setSpacing(8)
        form.setColumnStretch(1, 1)

        datos = empresa_service.obtener_todos()

        campos_dev = [
            ("Nombre:", "dev_nombre"),
            ("Email:", "dev_email"),
            ("Web:", "dev_web"),
            ("Telefono:", "dev_telefono"),
            ("Direccion:", "dev_direccion"),
        ]

        self._dev_inputs = {}
        for i, (label, clave) in enumerate(campos_dev):
            form.addWidget(QLabel(label), i, 0)
            inp = QLineEdit()
            inp.setMinimumHeight(32)
            inp.setText(datos.get(clave, ""))
            form.addWidget(inp, i, 1)
            self._dev_inputs[clave] = inp

        layout.addLayout(form)

        btn = QPushButton("Guardar Datos Desarrollador")
        btn.setMinimumHeight(36)
        btn.clicked.connect(self._guardar_dev)
        layout.addWidget(btn)
        layout.addStretch()
        return page

    def _guardar_dev(self):
        datos = {clave: inp.text().strip() for clave, inp in self._dev_inputs.items()}
        try:
            empresa_service.guardar_multiples(datos)
            QMessageBox.information(self, "OK", "Datos del desarrollador guardados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
