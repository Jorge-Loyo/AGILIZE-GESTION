from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QStackedWidget,
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt
from datetime import date
from modulos.rrhh.views.liquidar_view import LiquidarView
from modulos.rrhh.views.adelantos_view import AdelantosView
from modulos.rrhh.views.sac_view import SACView
from modulos.rrhh.views.resumen_mensual_view import ResumenMensualView
from services.nomina_service import nomina_service
from services.recibo_pdf_service import generar_recibo_pdf
from services.export_service import exportar_excel
import os


class NominaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        tabs = QTabWidget()
        tabs.addTab(self._build_liquidaciones_tab(), "Liquidaciones")
        tabs.addTab(ResumenMensualView(), "Resumen Mensual")
        tabs.addTab(AdelantosView(), "Adelantos")
        tabs.addTab(SACView(), "SAC (Aguinaldo)")
        from modulos.rrhh.views.novedades_mensuales_view import NovedadesMensualesView
        tabs.addTab(NovedadesMensualesView(), "Novedades Mensuales")
        layout.addWidget(tabs)

    def _build_liquidaciones_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(8)

        self.stack = QStackedWidget()

        # Pagina 0: Historial
        lista_page = QWidget()
        lista_layout = QVBoxLayout(lista_page)
        lista_layout.setContentsMargins(0, 0, 0, 0)
        lista_layout.setSpacing(8)

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(8)

        filtros.addWidget(QLabel("Anio:"))
        self.filtro_anio = QSpinBox()
        self.filtro_anio.setMinimumHeight(32)
        self.filtro_anio.setRange(2020, 2050)
        self.filtro_anio.setValue(date.today().year)
        filtros.addWidget(self.filtro_anio)

        filtros.addWidget(QLabel("Mes:"))
        self.filtro_mes = QComboBox()
        self.filtro_mes.setMinimumHeight(32)
        self.filtro_mes.addItem("Todos", "")
        for m in range(1, 13):
            self.filtro_mes.addItem(f"{m:02d}", f"{m:02d}")
        filtros.addWidget(self.filtro_mes)

        filtros.addWidget(QLabel("Empleado:"))
        self.filtro_empleado = QLineEdit()
        self.filtro_empleado.setMinimumHeight(32)
        self.filtro_empleado.setPlaceholderText("Buscar por nombre...")
        filtros.addWidget(self.filtro_empleado)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setMinimumHeight(32)
        btn_filtrar.clicked.connect(self._cargar_lista)
        filtros.addWidget(btn_filtrar)

        btn_nuevo = QPushButton("+ Liquidar")
        btn_nuevo.setMinimumHeight(32)
        btn_nuevo.clicked.connect(self._nueva_liquidacion)
        filtros.addWidget(btn_nuevo)

        lista_layout.addLayout(filtros)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Empleado", "Periodo", "Bruto", "Haberes", "Deducciones", "Neto"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        lista_layout.addWidget(self.tabla)

        # Botones abajo
        bottom = QHBoxLayout()
        bottom.addStretch()

        btn_export = QPushButton("  Exportar Excel")
        btn_export.setMinimumHeight(36)
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.setStyleSheet("QPushButton { background-color: #10b981; } QPushButton:hover { background-color: #059669; }")
        btn_export.clicked.connect(self._exportar_liquidaciones)
        bottom.addWidget(btn_export)

        btn_print = QPushButton("  Imprimir Recibo")
        btn_print.setMinimumHeight(36)
        btn_print.setCursor(Qt.PointingHandCursor)
        btn_print.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_print.clicked.connect(self._imprimir_seleccionado)
        bottom.addWidget(btn_print)

        lista_layout.addLayout(bottom)
        self.stack.addWidget(lista_page)

        # Pagina 1: Form liquidar
        self._form_container = QWidget()
        self._form_layout = QVBoxLayout(self._form_container)
        self._form_layout.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(self._form_container)

        layout.addWidget(self.stack)
        self._cargar_lista()
        return page

    def _cargar_lista(self):
        anio = self.filtro_anio.value()
        mes = self.filtro_mes.currentData()
        busqueda = self.filtro_empleado.text().strip().lower()

        if mes:
            periodo = f"{anio}-{mes}"
        else:
            periodo = ""

        liquidaciones = nomina_service.listar_liquidaciones(periodo=periodo)

        if not mes:
            liquidaciones = [l for l in liquidaciones if l.periodo.startswith(str(anio))]

        if busqueda:
            liquidaciones = [
                l for l in liquidaciones
                if l.empleado and busqueda in f"{l.empleado.apellido} {l.empleado.nombre}".lower()
            ]

        self._liquidaciones = liquidaciones
        self.tabla.setRowCount(len(liquidaciones))

        for i, liq in enumerate(liquidaciones):
            nombre = f"{liq.empleado.apellido}, {liq.empleado.nombre}" if liq.empleado else ""
            self.tabla.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla.setItem(i, 1, QTableWidgetItem(liq.periodo))
            self.tabla.setItem(i, 2, QTableWidgetItem(f"$ {liq.sueldo_basico:,.2f}"))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"$ {liq.total_haberes:,.2f}"))
            self.tabla.setItem(i, 4, QTableWidgetItem(f"$ {liq.total_deducciones:,.2f}"))
            self.tabla.setItem(i, 5, QTableWidgetItem(f"$ {liq.neto:,.2f}"))

    def _imprimir_seleccionado(self):
        row = self.tabla.currentRow()
        if row < 0 or row >= len(self._liquidaciones):
            QMessageBox.information(self, "Seleccion", "Selecciona una liquidacion de la lista.")
            return
        liq_id = self._liquidaciones[row].id
        try:
            filepath = generar_recibo_pdf(liq_id)
            os.startfile(filepath)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el recibo: {e}")

    def _exportar_liquidaciones(self):
        if not self._liquidaciones:
            QMessageBox.information(self, "Info", "No hay liquidaciones para exportar.")
            return
        headers = ["Empleado", "Periodo", "Bruto", "Haberes", "Deducciones", "Neto"]
        rows = []
        for liq in self._liquidaciones:
            nombre = f"{liq.empleado.apellido}, {liq.empleado.nombre}" if liq.empleado else ""
            rows.append([nombre, liq.periodo, float(liq.sueldo_basico), float(liq.total_haberes), float(liq.total_deducciones), float(liq.neto)])
        try:
            path = exportar_excel("liquidaciones.xlsx", headers, rows, "Liquidaciones")
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _nueva_liquidacion(self):
        for i in reversed(range(self._form_layout.count())):
            w = self._form_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        form = LiquidarView()
        form.liquidacion_creada.connect(self._on_liquidada)
        self._form_layout.addWidget(form)
        self.stack.setCurrentIndex(1)

    def _on_liquidada(self):
        self.stack.setCurrentIndex(0)
        self._cargar_lista()
