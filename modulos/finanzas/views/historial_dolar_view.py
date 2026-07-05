"""Vista de Historial del Dolar - consulta BCV y muestra evolucion."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QFrame, QHeaderView, QMessageBox,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QBrush
import qtawesome as qta


class _LoadWorker(QThread):
    finished = Signal(list)

    def __init__(self, pais, dias):
        super().__init__()
        self.pais = pais
        self.dias = dias

    def run(self):
        from services.finanzas.dolar_service import dolar_service
        datos = dolar_service.obtener_historial(self.pais, self.dias)
        self.finished.emit([(d.fecha, float(d.valor), d.fuente, d.hora_consulta) for d in datos])


class _ScrapeWorker(QThread):
    finished = Signal(object)

    def __init__(self, pais):
        super().__init__()
        self.pais = pais

    def run(self):
        from services.finanzas.dolar_service import dolar_service
        result = dolar_service.scrape_y_guardar(self.pais)
        self.finished.emit(result)


class MiniChart(QWidget):
    """Grafico de linea simple para evolucion del dolar."""

    def __init__(self):
        super().__init__()
        self.data: list[tuple] = []
        self.setMinimumHeight(180)
        self.setMaximumHeight(220)

    def set_data(self, data: list[tuple]):
        self.data = list(reversed(data))
        self.update()

    def paintEvent(self, event):
        if len(self.data) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width() - 80, self.height() - 40
        x_off, y_off = 60, 20

        valores = [d[1] for d in self.data]
        v_min, v_max = min(valores), max(valores)
        rango = v_max - v_min if v_max != v_min else 1

        painter.fillRect(self.rect(), QColor("#1a1a2e"))

        painter.setPen(QPen(QColor("#555"), 1))
        painter.drawLine(x_off, y_off, x_off, y_off + h)
        painter.drawLine(x_off, y_off + h, x_off + w, y_off + h)

        painter.setFont(QFont("Consolas", 8))
        painter.setPen(QColor("#aaa"))
        for i in range(5):
            y = y_off + h - (h * i / 4)
            val = v_min + rango * i / 4
            painter.drawText(2, int(y) + 4, f"{val:.2f}")
            painter.setPen(QPen(QColor("#333"), 1, Qt.DashLine))
            painter.drawLine(x_off, int(y), x_off + w, int(y))
            painter.setPen(QColor("#aaa"))

        painter.setPen(QPen(QColor("#D4AF37"), 2))
        points = []
        step = w / (len(self.data) - 1) if len(self.data) > 1 else w
        for i, (fecha, val, _) in enumerate(self.data):
            x = x_off + i * step
            y = y_off + h - ((val - v_min) / rango * h)
            points.append((int(x), int(y)))

        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])

        painter.setBrush(QColor("#D4AF37"))
        for px, py in points:
            painter.drawEllipse(px - 3, py - 3, 6, 6)

        painter.setPen(QColor("#aaa"))
        if self.data:
            painter.drawText(x_off, y_off + h + 15, str(self.data[0][0]))
            painter.drawText(x_off + w - 60, y_off + h + 15, str(self.data[-1][0]))

        painter.end()


class HistorialDolarView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._scrape_worker = None
        self._build_ui()
        self._cargar()

    def _get_pais(self) -> str:
        try:
            from services.core.empresa_service import empresa_service
            return (empresa_service.obtener("cotizacion_pais") or "venezuela").lower().strip()
        except Exception:
            return "venezuela"

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        lbl = QLabel("Historial del Dolar")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #D4AF37;")
        header.addWidget(lbl)

        self.lbl_pais = QLabel(f"Pais: {self._get_pais().capitalize()}")
        self.lbl_pais.setStyleSheet("font-size: 12px; color: #888;")
        header.addWidget(self.lbl_pais)
        header.addStretch()

        header.addWidget(QLabel("Periodo:"))
        self.cmb_dias = QComboBox()
        self.cmb_dias.addItems(["30 dias", "60 dias", "90 dias", "180 dias", "365 dias"])
        self.cmb_dias.setCurrentIndex(2)
        self.cmb_dias.currentIndexChanged.connect(self._cargar)
        header.addWidget(self.cmb_dias)
        layout.addLayout(header)

        # Card valor actual + boton consultar
        self.card_actual = QFrame()
        self.card_actual.setStyleSheet(
            "QFrame { background: #1a1a2e; border-radius: 8px; padding: 16px; }"
        )
        card_lay = QHBoxLayout(self.card_actual)

        # Lado izquierdo: valor
        info_lay = QVBoxLayout()
        self.lbl_titulo_valor = QLabel("Valor actual del Dolar (BCV)")
        self.lbl_titulo_valor.setStyleSheet("font-size: 12px; color: #888;")
        info_lay.addWidget(self.lbl_titulo_valor)

        self.lbl_valor_hoy = QLabel("Cargando...")
        self.lbl_valor_hoy.setStyleSheet("font-size: 28px; font-weight: bold; color: #D4AF37;")
        info_lay.addWidget(self.lbl_valor_hoy)

        row_var = QHBoxLayout()
        self.lbl_variacion = QLabel("")
        self.lbl_variacion.setStyleSheet("font-size: 13px;")
        row_var.addWidget(self.lbl_variacion)
        self.lbl_fecha_hoy = QLabel("")
        self.lbl_fecha_hoy.setStyleSheet("font-size: 11px; color: #888;")
        row_var.addWidget(self.lbl_fecha_hoy)
        row_var.addStretch()
        info_lay.addLayout(row_var)

        card_lay.addLayout(info_lay)
        card_lay.addStretch()

        # Lado derecho: boton consultar
        self.btn_consultar = QPushButton("  Consultar BCV")
        self.btn_consultar.setIcon(qta.icon("fa5s.sync", color="#121212"))
        self.btn_consultar.setCursor(Qt.PointingHandCursor)
        self.btn_consultar.setMinimumHeight(44)
        self.btn_consultar.setMinimumWidth(180)
        self.btn_consultar.setToolTip("Consulta el valor actual del dolar en el Banco Central de Venezuela y lo guarda")
        self.btn_consultar.setStyleSheet(
            "QPushButton { background-color: #D4AF37; color: #121212; font-weight: bold; font-size: 13px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #c9a030; }"
            "QPushButton:disabled { background-color: #555; color: #999; }"
        )
        self.btn_consultar.clicked.connect(self._scrape_ahora)
        card_lay.addWidget(self.btn_consultar)

        layout.addWidget(self.card_actual)

        # Grafico
        self.chart = MiniChart()
        layout.addWidget(self.chart)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Fecha", "Hora", "Valor (Bs.)", "Variacion", "Fuente"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

    def _dias_seleccionados(self) -> int:
        mapeo = {0: 30, 1: 60, 2: 90, 3: 180, 4: 365}
        return mapeo.get(self.cmb_dias.currentIndex(), 90)

    def _cargar(self):
        pais = self._get_pais()
        self._worker = _LoadWorker(pais, self._dias_seleccionados())
        self._worker.finished.connect(self._mostrar_datos)
        self._worker.start()

    def _mostrar_datos(self, datos: list[tuple]):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(datos))
        for i, (fecha, valor, fuente, hora) in enumerate(datos):
            self.table.setItem(i, 0, QTableWidgetItem(str(fecha)))
            hora_str = hora.strftime("%H:%M") if hora else "-"
            self.table.setItem(i, 1, QTableWidgetItem(hora_str))
            item_val = QTableWidgetItem(f"{valor:,.4f}")
            item_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 2, item_val)

            # Variacion vs registro anterior
            if i < len(datos) - 1:
                valor_ant = datos[i + 1][1]
                diff = valor - valor_ant
                pct = (diff / valor_ant * 100) if valor_ant else 0
                signo = "+" if diff >= 0 else ""
                var_text = f"{signo}{diff:,.4f} ({signo}{pct:.2f}%)"
                item_var = QTableWidgetItem(var_text)
                item_var.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if diff >= 0:
                    item_var.setForeground(QColor("#4ade80"))
                else:
                    item_var.setForeground(QColor("#ef4444"))
                self.table.setItem(i, 3, item_var)
            else:
                self.table.setItem(i, 3, QTableWidgetItem("-"))

            self.table.setItem(i, 4, QTableWidgetItem(fuente))
        self.table.setSortingEnabled(True)

        if datos:
            fecha_hoy, valor_hoy, _, hora_hoy = datos[0]
            hora_str = hora_hoy.strftime("%H:%M") if hora_hoy else ""
            self.lbl_valor_hoy.setText(f"Bs. {valor_hoy:,.4f}")
            self.lbl_fecha_hoy.setText(f"Ultima consulta: {fecha_hoy} {hora_str}")

            if len(datos) > 1:
                valor_ant = datos[1][1]
                diff = valor_hoy - valor_ant
                pct = (diff / valor_ant * 100) if valor_ant else 0
                color = "#4ade80" if diff >= 0 else "#ef4444"
                signo = "+" if diff >= 0 else ""
                self.lbl_variacion.setText(f"{signo}{diff:,.4f} ({signo}{pct:.2f}%)")
                self.lbl_variacion.setStyleSheet(f"font-size: 13px; color: {color};")
            else:
                self.lbl_variacion.setText("")
        else:
            self.lbl_valor_hoy.setText("Sin datos")
            self.lbl_fecha_hoy.setText("")
            self.lbl_variacion.setText("")

        self.chart.set_data([(f, v, src) for f, v, src, _ in datos])

    def _scrape_ahora(self):
        self.btn_consultar.setEnabled(False)
        self.btn_consultar.setText("  Consultando...")
        pais = self._get_pais()
        self._scrape_worker = _ScrapeWorker(pais)
        self._scrape_worker.finished.connect(self._on_scrape_done)
        self._scrape_worker.start()

    def _on_scrape_done(self, result):
        self.btn_consultar.setEnabled(True)
        self.btn_consultar.setText("  Consultar BCV")
        if result:
            self._cargar()
            QMessageBox.information(self, "Exito", f"Valor actualizado: Bs. {float(result.valor):,.4f}")
        else:
            QMessageBox.warning(self, "Error", "No se pudo obtener el valor del dolar desde el BCV.\nVerifique su conexion a internet.")
