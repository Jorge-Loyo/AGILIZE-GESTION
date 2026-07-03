import re
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QScrollArea,
    QPushButton, QLabel, QMessageBox, QDoubleSpinBox,
    QCheckBox, QTimeEdit, QFrame, QGroupBox,
)
from PySide6.QtCore import Qt, Signal, QDate, QTime
from PySide6.QtGui import QIntValidator
from services.rrhh.empleado_service import empleado_service
from services.core.pais_config_service import label_doc_identidad, label_id_fiscal
from decimal import Decimal


class FormEmpleado(QWidget):
    guardado = Signal()
    cancelado = Signal()

    def __init__(self, empleado_id: int | None = None, parent=None):
        super().__init__(parent)
        self._empleado_id = empleado_id
        self._departamentos = []
        self._cargos = []
        self._calculando = False
        self._build_ui()
        self._cargar_combos()
        if empleado_id:
            self._cargar_datos()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area completo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(4, 4, 12, 4)

        # Header
        titulo = "Editar Empleado" if self._empleado_id else "Nuevo Empleado"
        lbl_title = QLabel(titulo)
        lbl_title.setObjectName("title")
        content_layout.addWidget(lbl_title)

        # === Datos Personales ===
        grp_personal = self._create_group("Datos Personales")
        form1 = QGridLayout(grp_personal)
        form1.setSpacing(8)
        form1.setColumnStretch(1, 1)
        form1.setColumnStretch(3, 1)

        form1.addWidget(QLabel("Nombre *"), 0, 0)
        self.input_nombre = QLineEdit()
        self.input_nombre.setMinimumHeight(32)
        form1.addWidget(self.input_nombre, 0, 1)

        form1.addWidget(QLabel("Apellido *"), 0, 2)
        self.input_apellido = QLineEdit()
        self.input_apellido.setMinimumHeight(32)
        form1.addWidget(self.input_apellido, 0, 3)

        self._lbl_dni = label_doc_identidad()
        self._lbl_cuil = label_id_fiscal()

        form1.addWidget(QLabel(f"{self._lbl_dni} *"), 1, 0)
        self.input_dni = QLineEdit()
        self.input_dni.setMinimumHeight(32)
        self.input_dni.setPlaceholderText("7-9 dígitos")
        self.input_dni.setMaxLength(15)
        form1.addWidget(self.input_dni, 1, 1)

        form1.addWidget(QLabel(f"{self._lbl_cuil} *"), 1, 2)
        self.input_cuil = QLineEdit()
        self.input_cuil.setMinimumHeight(32)
        self.input_cuil.setPlaceholderText("Identificación fiscal")
        self.input_cuil.setMaxLength(20)
        form1.addWidget(self.input_cuil, 1, 3)

        form1.addWidget(QLabel("Email"), 2, 0)
        self.input_email = QLineEdit()
        self.input_email.setMinimumHeight(32)
        self.input_email.setPlaceholderText("ejemplo@mail.com")
        form1.addWidget(self.input_email, 2, 1)

        form1.addWidget(QLabel("Teléfono"), 2, 2)
        self.input_telefono = QLineEdit()
        self.input_telefono.setMinimumHeight(32)
        form1.addWidget(self.input_telefono, 2, 3)

        form1.addWidget(QLabel("Dirección"), 3, 0)
        self.input_direccion = QLineEdit()
        self.input_direccion.setMinimumHeight(32)
        form1.addWidget(self.input_direccion, 3, 1, 1, 3)

        form1.addWidget(QLabel("Fecha Nac. *"), 4, 0)
        self.input_fecha_nac = QDateEdit()
        self.input_fecha_nac.setMinimumHeight(32)
        self.input_fecha_nac.setCalendarPopup(True)
        self.input_fecha_nac.setDate(QDate(1990, 1, 1))
        self.input_fecha_nac.dateChanged.connect(self._calcular_edad)
        form1.addWidget(self.input_fecha_nac, 4, 1)

        form1.addWidget(QLabel("Edad:"), 4, 2)
        self.lbl_edad = QLabel("—")
        self.lbl_edad.setStyleSheet("font-weight: bold;")
        form1.addWidget(self.lbl_edad, 4, 3)

        content_layout.addWidget(grp_personal)

        # === Datos Laborales ===
        grp_laboral = self._create_group("Datos Laborales")
        form2 = QGridLayout(grp_laboral)
        form2.setSpacing(8)
        form2.setColumnStretch(1, 1)
        form2.setColumnStretch(3, 1)

        form2.addWidget(QLabel("Fecha Ingreso"), 0, 0)
        self.input_fecha_ingreso = QDateEdit()
        self.input_fecha_ingreso.setMinimumHeight(32)
        self.input_fecha_ingreso.setCalendarPopup(True)
        self.input_fecha_ingreso.setDate(QDate.currentDate())
        form2.addWidget(self.input_fecha_ingreso, 0, 1)

        form2.addWidget(QLabel("Departamento"), 0, 2)
        self.combo_depto = QComboBox()
        self.combo_depto.setMinimumHeight(32)
        form2.addWidget(self.combo_depto, 0, 3)

        form2.addWidget(QLabel("Cargo"), 1, 0)
        self.combo_cargo = QComboBox()
        self.combo_cargo.setMinimumHeight(32)
        form2.addWidget(self.combo_cargo, 1, 1)

        form2.addWidget(QLabel("Sucursal"), 1, 2)
        self.combo_sucursal = QComboBox()
        self.combo_sucursal.setMinimumHeight(32)
        form2.addWidget(self.combo_sucursal, 1, 3)

        content_layout.addWidget(grp_laboral)

        # === Jornada y Remuneración ===
        grp_jornada = self._create_group("Jornada y Remuneración")
        form3 = QGridLayout(grp_jornada)
        form3.setSpacing(8)
        form3.setColumnStretch(1, 1)
        form3.setColumnStretch(3, 1)
        form3.setColumnStretch(5, 1)

        form3.addWidget(QLabel("Entrada"), 0, 0)
        self.input_hora_entrada = QTimeEdit()
        self.input_hora_entrada.setMinimumHeight(32)
        self.input_hora_entrada.setDisplayFormat("HH:mm")
        # Leer default de config
        from services.core.empresa_service import empresa_service as _emp_svc
        _ent = (_emp_svc.obtener("jornada_entrada") or "08:00").split(":")
        _sal = (_emp_svc.obtener("jornada_salida") or "17:00").split(":")
        self.input_hora_entrada.setTime(QTime(int(_ent[0]), int(_ent[1])))
        self.input_hora_entrada.timeChanged.connect(self._on_horario_changed)
        form3.addWidget(self.input_hora_entrada, 0, 1)

        form3.addWidget(QLabel("Salida"), 0, 2)
        self.input_hora_salida = QTimeEdit()
        self.input_hora_salida.setMinimumHeight(32)
        self.input_hora_salida.setDisplayFormat("HH:mm")
        self.input_hora_salida.setTime(QTime(int(_sal[0]), int(_sal[1])))
        self.input_hora_salida.timeChanged.connect(self._on_horario_changed)
        form3.addWidget(self.input_hora_salida, 0, 3)

        form3.addWidget(QLabel("Hs/Día"), 0, 4)
        self.input_horas_jornada = QDoubleSpinBox()
        self.input_horas_jornada.setMinimumHeight(32)
        self.input_horas_jornada.setRange(1, 24)
        self.input_horas_jornada.setDecimals(1)
        self.input_horas_jornada.setValue(8.0)
        self.input_horas_jornada.setSuffix(" hs")
        self.input_horas_jornada.setReadOnly(True)
        form3.addWidget(self.input_horas_jornada, 0, 5)

        form3.addWidget(QLabel("Días"), 1, 0)
        dias_widget = QWidget()
        dias_layout = QHBoxLayout(dias_widget)
        dias_layout.setContentsMargins(0, 0, 0, 0)
        dias_layout.setSpacing(8)
        self._dias_checks = {}
        for code, label in [("lun", "Lu"), ("mar", "Ma"), ("mie", "Mi"), ("jue", "Ju"), ("vie", "Vi"), ("sab", "Sá"), ("dom", "Do")]:
            chk = QCheckBox(label)
            chk.setChecked(code in "lun,mar,mie,jue,vie")
            chk.stateChanged.connect(self._on_dias_changed)
            dias_layout.addWidget(chk)
            self._dias_checks[code] = chk
        form3.addWidget(dias_widget, 1, 1, 1, 5)

        form3.addWidget(QLabel("Valor Hora"), 2, 0)
        self.input_valor_hora = QDoubleSpinBox()
        self.input_valor_hora.setMinimumHeight(32)
        self.input_valor_hora.setRange(0, 999999)
        self.input_valor_hora.setDecimals(2)
        self.input_valor_hora.setPrefix("$ ")
        self.input_valor_hora.valueChanged.connect(self._on_valor_hora_changed)
        form3.addWidget(self.input_valor_hora, 2, 1)

        form3.addWidget(QLabel("Sueldo Mensual"), 2, 2)
        self.input_sueldo_mensual = QDoubleSpinBox()
        self.input_sueldo_mensual.setMinimumHeight(32)
        self.input_sueldo_mensual.setRange(0, 99999999)
        self.input_sueldo_mensual.setDecimals(2)
        self.input_sueldo_mensual.setPrefix("$ ")
        self.input_sueldo_mensual.valueChanged.connect(self._on_sueldo_mensual_changed)
        form3.addWidget(self.input_sueldo_mensual, 2, 3)

        self.lbl_calculo = QLabel("")
        self.lbl_calculo.setObjectName("subtitle")
        form3.addWidget(self.lbl_calculo, 2, 4, 1, 2)

        form3.addWidget(QLabel("Valor Hora Extra"), 3, 0)
        self.input_valor_hora_extra = QDoubleSpinBox()
        self.input_valor_hora_extra.setMinimumHeight(32)
        self.input_valor_hora_extra.setRange(0, 999999)
        self.input_valor_hora_extra.setDecimals(2)
        self.input_valor_hora_extra.setPrefix("$ ")
        form3.addWidget(self.input_valor_hora_extra, 3, 1)

        form3.addWidget(QLabel("Tipo Liquidación"), 3, 2)
        self.combo_tipo_liquidacion = QComboBox()
        self.combo_tipo_liquidacion.setMinimumHeight(32)
        self.combo_tipo_liquidacion.addItem("Por hora (fichado)", "por_hora")
        self.combo_tipo_liquidacion.addItem("Sueldo mensual (sin fichado)", "mensual")
        form3.addWidget(self.combo_tipo_liquidacion, 3, 3)

        self.lbl_calculo.setObjectName("subtitle")
        form3.addWidget(self.lbl_calculo, 2, 4, 1, 2)

        content_layout.addWidget(grp_jornada)

        # === Observaciones ===
        grp_obs = self._create_group("Observaciones")
        obs_layout = QVBoxLayout(grp_obs)
        self.input_obs = QTextEdit()
        self.input_obs.setMaximumHeight(60)
        obs_layout.addWidget(self.input_obs)
        content_layout.addWidget(grp_obs)

        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # === Botones (fuera del scroll, siempre visibles) ===
        btns = QHBoxLayout()
        btns.setContentsMargins(4, 8, 12, 4)
        btns.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_cancelar.setMinimumHeight(38)
        btn_cancelar.setMinimumWidth(110)
        btn_cancelar.clicked.connect(self.cancelado.emit)
        btns.addWidget(btn_cancelar)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setMinimumHeight(38)
        btn_guardar.setMinimumWidth(110)
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)

        main_layout.addLayout(btns)

        # Calcular edad inicial
        self._calcular_edad()

    def _create_group(self, title: str) -> QGroupBox:
        grp = QGroupBox(title)
        grp.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        return grp

    # === Validaciones ===

    def _validar(self) -> str | None:
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()
        dni = self.input_dni.text().strip()
        cuil = self.input_cuil.text().strip()
        email = self.input_email.text().strip()

        if not nombre:
            return "El nombre es obligatorio."
        if not apellido:
            return "El apellido es obligatorio."

        if not dni:
            return f"El {self._lbl_dni} es obligatorio."
        if len(dni) < 5:
            return f"El {self._lbl_dni} debe tener al menos 5 caracteres."

        if not cuil:
            return f"El {self._lbl_cuil} es obligatorio."

        # Email (si se ingresó)
        if email:
            email_pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email):
                return "El email no tiene un formato válido."

        # Edad mínima 17 años
        fecha_nac = self.input_fecha_nac.date().toPython()
        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        if edad < 17:
            return f"El empleado tiene {edad} años. Debe ser mayor de 17."

        return None

    def _calcular_edad(self):
        fecha_nac = self.input_fecha_nac.date().toPython()
        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        self.lbl_edad.setText(f"{edad} años")

    # === Cálculos automáticos ===

    def _on_horario_changed(self):
        entrada = self.input_hora_entrada.time()
        salida = self.input_hora_salida.time()
        mins = entrada.secsTo(salida) / 60
        if mins <= 0:
            mins += 1440
        self.input_horas_jornada.setValue(round(mins / 60, 1))
        self._recalcular_sueldo_desde_hora()

    def _on_dias_changed(self):
        self._recalcular_sueldo_desde_hora()

    def _dias_laborales_count(self) -> int:
        return sum(1 for chk in self._dias_checks.values() if chk.isChecked())

    def _horas_mensuales(self) -> float:
        return round(self._dias_laborales_count() * 4.33 * self.input_horas_jornada.value(), 2)

    def _on_valor_hora_changed(self, value):
        if self._calculando:
            return
        self._calculando = True
        if value > 0:
            self.input_sueldo_mensual.setValue(round(value * self._horas_mensuales(), 2))
            self.lbl_calculo.setText(f"{self._horas_mensuales():.0f} hs/mes")
        self._calculando = False

    def _on_sueldo_mensual_changed(self, value):
        if self._calculando:
            return
        self._calculando = True
        hs = self._horas_mensuales()
        if value > 0 and hs > 0:
            self.input_valor_hora.setValue(round(value / hs, 2))
            self.lbl_calculo.setText(f"{hs:.0f} hs/mes")
        self._calculando = False

    def _recalcular_sueldo_desde_hora(self):
        if self._calculando:
            return
        valor_hora = self.input_valor_hora.value()
        if valor_hora > 0:
            self._calculando = True
            self.input_sueldo_mensual.setValue(round(valor_hora * self._horas_mensuales(), 2))
            self.lbl_calculo.setText(f"{self._horas_mensuales():.0f} hs/mes")
            self._calculando = False

    # === Carga de datos ===

    def _cargar_combos(self):
        self._departamentos = empleado_service.listar_departamentos()
        self._cargos = empleado_service.listar_cargos()
        self.combo_depto.addItem("— Sin asignar —", None)
        for d in self._departamentos:
            self.combo_depto.addItem(d.nombre, d.id)
        self.combo_cargo.addItem("— Sin asignar —", None)
        for c in self._cargos:
            self.combo_cargo.addItem(c.nombre, c.id)
        # Sucursales
        from core.database import get_db
        from models.sucursal import Sucursal
        self.combo_sucursal.addItem("— Sin asignar —", None)
        with get_db() as db:
            sucursales = db.query(Sucursal).filter(Sucursal.activo == True).order_by(Sucursal.nombre).all()
            for s in sucursales:
                self.combo_sucursal.addItem(s.nombre, s.id)

    def _cargar_datos(self):
        emp = empleado_service.obtener(self._empleado_id)
        if not emp:
            return
        self._calculando = True
        self.input_nombre.setText(emp.nombre)
        self.input_apellido.setText(emp.apellido)
        self.input_dni.setText(emp.dni)
        self.input_cuil.setText(emp.cuil)
        self.input_email.setText(emp.email or "")
        self.input_telefono.setText(emp.telefono or "")
        self.input_direccion.setText(emp.direccion or "")
        if emp.fecha_nacimiento:
            self.input_fecha_nac.setDate(QDate(emp.fecha_nacimiento.year, emp.fecha_nacimiento.month, emp.fecha_nacimiento.day))
        if emp.fecha_ingreso:
            self.input_fecha_ingreso.setDate(QDate(emp.fecha_ingreso.year, emp.fecha_ingreso.month, emp.fecha_ingreso.day))
        if emp.departamento_id:
            idx = self.combo_depto.findData(emp.departamento_id)
            if idx >= 0:
                self.combo_depto.setCurrentIndex(idx)
        if emp.cargo_id:
            idx = self.combo_cargo.findData(emp.cargo_id)
            if idx >= 0:
                self.combo_cargo.setCurrentIndex(idx)
        if getattr(emp, 'sucursal_id', None):
            idx = self.combo_sucursal.findData(emp.sucursal_id)
            if idx >= 0:
                self.combo_sucursal.setCurrentIndex(idx)
        if emp.hora_entrada:
            h, m = emp.hora_entrada.split(":")
            self.input_hora_entrada.setTime(QTime(int(h), int(m)))
        if emp.hora_salida:
            h, m = emp.hora_salida.split(":")
            self.input_hora_salida.setTime(QTime(int(h), int(m)))
        self.input_horas_jornada.setValue(float(emp.horas_jornada) if emp.horas_jornada else 8.0)
        dias = (emp.dias_laborales or "lun,mar,mie,jue,vie").split(",")
        for code, chk in self._dias_checks.items():
            chk.setChecked(code in dias)
        self.input_valor_hora.setValue(float(emp.valor_hora) if emp.valor_hora else 0.0)
        self.input_valor_hora_extra.setValue(float(emp.valor_hora_extra) if getattr(emp, "valor_hora_extra", None) else 0.0)
        self.input_sueldo_mensual.setValue(float(emp.sueldo_mensual) if emp.sueldo_mensual else 0.0)
        # Tipo liquidacion
        idx_tipo = self.combo_tipo_liquidacion.findData(getattr(emp, "tipo_liquidacion", "por_hora"))
        if idx_tipo >= 0:
            self.combo_tipo_liquidacion.setCurrentIndex(idx_tipo)
        self.input_obs.setPlainText(emp.observaciones or "")
        self._calculando = False
        self._calcular_edad()

    # === Guardar ===

    def _guardar(self):
        error = self._validar()
        if error:
            QMessageBox.warning(self, "Validación", error)
            return

        fecha_nac = self.input_fecha_nac.date().toPython()
        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

        datos = {
            "nombre": self.input_nombre.text().strip(),
            "apellido": self.input_apellido.text().strip(),
            "dni": self.input_dni.text().strip(),
            "cuil": self.input_cuil.text().strip(),
            "email": self.input_email.text().strip(),
            "telefono": self.input_telefono.text().strip(),
            "direccion": self.input_direccion.text().strip(),
            "fecha_nacimiento": fecha_nac,
            "edad": edad,
            "fecha_ingreso": self.input_fecha_ingreso.date().toPython(),
            "departamento_id": self.combo_depto.currentData(),
            "cargo_id": self.combo_cargo.currentData(),
            "sucursal_id": self.combo_sucursal.currentData(),
            "horas_jornada": self.input_horas_jornada.value(),
            "valor_hora": self.input_valor_hora.value(),
            "valor_hora_extra": self.input_valor_hora_extra.value(),
            "sueldo_mensual": self.input_sueldo_mensual.value(),
            "hora_entrada": self.input_hora_entrada.time().toString("HH:mm"),
            "hora_salida": self.input_hora_salida.time().toString("HH:mm"),
            "dias_laborales": ",".join(code for code, chk in self._dias_checks.items() if chk.isChecked()),
            "tipo_liquidacion": self.combo_tipo_liquidacion.currentData(),
            "observaciones": self.input_obs.toPlainText().strip(),
        }

        try:
            if self._empleado_id:
                empleado_service.actualizar(self._empleado_id, datos)
            else:
                empleado_service.crear(datos)
            self.guardado.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
