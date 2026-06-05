from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QGroupBox, QTextEdit,
)
from PySide6.QtCore import Qt
from services.update_service import update_service


class UpdateView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._verificar_estado()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("Actualizar Aplicacion")
        title.setObjectName("title")
        layout.addWidget(title)

        layout.addWidget(QLabel("Conecta al repositorio y descarga la ultima version disponible."))

        # Estado
        grp_estado = QGroupBox("Estado Actual")
        grp_estado.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        estado_layout = QVBoxLayout(grp_estado)

        self.lbl_git = QLabel("Git: verificando...")
        estado_layout.addWidget(self.lbl_git)

        self.lbl_version = QLabel("Version: ...")
        estado_layout.addWidget(self.lbl_version)

        self.lbl_repo = QLabel("Repositorio: ...")
        self.lbl_repo.setObjectName("subtitle")
        estado_layout.addWidget(self.lbl_repo)

        self.lbl_rama = QLabel("Rama: Deploy-Ferrelum")
        estado_layout.addWidget(self.lbl_rama)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("font-weight: bold;")
        estado_layout.addWidget(self.lbl_estado)

        layout.addWidget(grp_estado)

        # Detalle
        grp_detalle = QGroupBox("Detalle de Cambios")
        grp_detalle.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; padding-top: 14px; margin-top: 6px; }")
        detalle_layout = QVBoxLayout(grp_detalle)

        self.txt_detalle = QTextEdit()
        self.txt_detalle.setReadOnly(True)
        self.txt_detalle.setMaximumHeight(150)
        self.txt_detalle.setPlaceholderText("Sin cambios pendientes.")
        detalle_layout.addWidget(self.txt_detalle)

        layout.addWidget(grp_detalle)

        # Botones
        btns = QHBoxLayout()
        btns.addStretch()

        btn_verificar = QPushButton("  Verificar Actualizaciones")
        btn_verificar.setMinimumHeight(40)
        btn_verificar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; } QPushButton:hover { background-color: #3d3d3d; }")
        btn_verificar.clicked.connect(self._verificar)
        btns.addWidget(btn_verificar)

        btn_actualizar = QPushButton("  Actualizar Ahora")
        btn_actualizar.setMinimumHeight(40)
        btn_actualizar.clicked.connect(self._actualizar)
        btns.addWidget(btn_actualizar)

        layout.addLayout(btns)
        layout.addStretch()

    def _verificar_estado(self):
        if update_service.verificar_git():
            self.lbl_git.setText("Git: Instalado")
            self.lbl_git.setStyleSheet("color: #10b981;")
        else:
            self.lbl_git.setText("Git: No encontrado")
            self.lbl_git.setStyleSheet("color: #ef4444;")

        self.lbl_version.setText(f"Version local: {update_service.obtener_version_actual()}")
        self.lbl_repo.setText(f"Repositorio: github.com/Jorge-Loyo/AGILIZE-GESTION")

        if update_service.es_repositorio():
            self.lbl_estado.setText("Repositorio configurado")
            self.lbl_estado.setStyleSheet("color: #10b981; font-weight: bold;")
        else:
            self.lbl_estado.setText("Repositorio no inicializado")
            self.lbl_estado.setStyleSheet("color: #f59e0b; font-weight: bold;")

    def _verificar(self):
        if not update_service.verificar_git():
            QMessageBox.warning(self, "Error", "Git no esta instalado en el sistema.")
            return

        if not update_service.es_repositorio():
            resp = QMessageBox.question(
                self, "Inicializar",
                "El repositorio no esta configurado. Inicializar ahora?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if resp == QMessageBox.Yes:
                update_service.inicializar_repo()
                self._verificar_estado()
            return

        info = update_service.verificar_actualizaciones()
        if info["disponible"]:
            self.lbl_estado.setText(f"Hay {info['commits']} actualizacion(es) disponible(s)")
            self.lbl_estado.setStyleSheet("color: #D4AF37; font-weight: bold;")
            self.txt_detalle.setPlainText(info["detalle"])
        else:
            self.lbl_estado.setText("La aplicacion esta actualizada")
            self.lbl_estado.setStyleSheet("color: #10b981; font-weight: bold;")
            self.txt_detalle.clear()

    def _actualizar(self):
        if not update_service.verificar_git():
            QMessageBox.warning(self, "Error", "Git no esta instalado.")
            return

        resp = QMessageBox.question(
            self, "Confirmar Actualizacion",
            "Se descargara la ultima version. La aplicacion se debe reiniciar despues.\n\nContinuar?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        resultado = update_service.actualizar()
        if resultado["exito"]:
            self.txt_detalle.setPlainText(resultado["mensaje"])
            self.lbl_estado.setText("Actualizado correctamente. Reinicia la aplicacion.")
            self.lbl_estado.setStyleSheet("color: #10b981; font-weight: bold;")
            QMessageBox.information(self, "OK", "Actualizacion completada. Reinicia la aplicacion para aplicar los cambios.")
        else:
            self.txt_detalle.setPlainText(resultado["mensaje"])
            self.lbl_estado.setText("Error al actualizar")
            self.lbl_estado.setStyleSheet("color: #ef4444; font-weight: bold;")
            QMessageBox.critical(self, "Error", f"No se pudo actualizar:\n{resultado['mensaje']}")
