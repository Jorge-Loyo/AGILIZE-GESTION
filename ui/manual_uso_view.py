from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt


MANUAL_RRHH = {
    "Dashboard": (
        "El Dashboard muestra un resumen general del módulo RRHH.\n\n"
        "• Cards con métricas: empleados activos, registros del mes, liquidaciones\n"
        "• Notificaciones: alertas de registros incompletos, empleados sin valor hora, pendientes de liquidar\n"
        "• Click en una alerta te guía a la sección correspondiente"
    ),
    "Empleados": (
        "Gestión completa del legajo de empleados.\n\n"
        "• + Nuevo: crea un empleado completando datos personales, laborales y remuneración\n"
        "• Importar: carga masiva desde Excel (.xlsx). Opción de actualizar existentes\n"
        "• Exportar: descarga la lista en Excel\n"
        "• Detalle: doble click para ver ficha completa + histórico de sueldo\n"
        "• Tipo Liquidación: 'Por hora' (requiere fichado) o 'Mensual' (solo se descuentan faltas)\n"
        "• Plantilla: descarga el formato Excel para importación"
    ),
    "Asistencia": (
        "Control de fichadas y asistencia de empleados.\n\n"
        "PESTAÑA REGISTRO:\n"
        "• Filtrar por empleado, período, estado (completos/incompletos), ordenar\n"
        "• Importar Fichadas: XLS (reloj) o XLSX (planilla manual con mapeo)\n"
        "• Registro Manual: agregar fichada individualmente\n"
        "• Normalizar Entrada: ajusta la hora al horario configurado\n"
        "• Calendario: vista visual de asistencia por empleado\n\n"
        "PESTAÑA VACACIONES:\n"
        "• Solicitar vacaciones indicando empleado, período y fechas\n"
        "• El sistema calcula días según antigüedad (Ley 20.744)\n"
        "• Flujo: Solicitar → Aprobar → Marcar Tomada\n\n"
        "PESTAÑA APROBACIÓN EXTRAS:\n"
        "• Lista de horas extra pendientes de aprobación\n"
        "• Aprobar individual, masivo o rechazar con motivo"
    ),
    "Cierres": (
        "Cierre de períodos de asistencia.\n\n"
        "• Seleccionar rango de fechas (ej: 01/06 al 15/06)\n"
        "• Si hay registros incompletos en el rango, NO permite cerrar\n"
        "• Una vez cerrado, los registros de ese rango no se pueden modificar\n"
        "• Se puede reabrir un cierre si es necesario\n"
        "• El cierre es requisito para poder liquidar el período"
    ),
    "Nómina": (
        "Liquidación de sueldos y gestión de pagos.\n\n"
        "LIQUIDACIONES:\n"
        "• + Liquidar: seleccionar período y empleado pendiente\n"
        "• [H] = por hora: calcula desde asistencia real\n"
        "• [M] = mensual: sueldo - descuento por faltas\n"
        "• Si falta info aparece marcado con ** motivo\n"
        "• Verificar Periodo: muestra cuántos faltan liquidar\n"
        "• Imprimir Recibo: genera PDF detallado\n\n"
        "RESUMEN MENSUAL:\n"
        "• Vista por Mes / Q1 / Q2 / Comparar\n"
        "• Comparar muestra diferencias entre quincenas\n\n"
        "ADELANTOS:\n"
        "• Registrar adelantos con cuotas\n"
        "• Se descuentan automáticamente en cada liquidación\n\n"
        "SAC (Aguinaldo):\n"
        "• Cálculo automático por método legal o promedio"
    ),
    "Configuración": (
        "Parámetros del módulo RRHH.\n\n"
        "PERIODO DE PAGO:\n"
        "• Mensual / Quincenal / Semanal / Diario\n"
        "• Afecta cómo se generan los períodos de liquidación\n\n"
        "VALOR HORA EXTRA:\n"
        "• Multiplicadores: hora extra, sábado, domingo, feriado\n"
        "• Ej: 1.50x = 50% más sobre valor hora base\n\n"
        "CONCEPTOS NÓMINA:\n"
        "• Crear haberes/deducciones: porcentaje, monto fijo, o por día\n"
        "• Se aplican al liquidar seleccionándolos\n\n"
        "FERIADOS:\n"
        "• Cargar feriados del año\n"
        "• Afectan el multiplicador de horas feriado"
    ),
}

MANUAL_CONFIG = {
    "Datos Empresa": (
        "Información legal de la empresa.\n\n"
        "• Razón Social, CUIT, dirección, contacto\n"
        "• Estos datos aparecen en los recibos de sueldo\n"
        "• Sucursales: agregar múltiples ubicaciones"
    ),
    "Visual": (
        "Personalización de la aplicación.\n\n"
        "• Nombre comercial: se muestra en el header\n"
        "• Logo: imagen que aparece en recibos y login"
    ),
    "Usuarios": (
        "Gestión de usuarios del sistema.\n\n"
        "• Crear usuarios con rol asignado\n"
        "• Cambiar contraseñas\n"
        "• Activar/desactivar accesos"
    ),
    "Auditoría": (
        "Registro de todas las acciones realizadas en el sistema.\n\n"
        "• Quién hizo qué y cuándo\n"
        "• Filtrar por fecha, usuario o acción"
    ),
    "Actualizar": (
        "Actualizaciones de la aplicación.\n\n"
        "• Verificar si hay nueva versión disponible\n"
        "• Actualizar desde el repositorio Git\n"
        "• Reiniciar la aplicación después de actualizar"
    ),
}


class ManualUsoView(QWidget):
    def __init__(self, contenido: dict, parent=None):
        super().__init__(parent)
        self._build_ui(contenido)

    def _build_ui(self, contenido: dict):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        title = QLabel("Manual de Uso")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        clayout = QVBoxLayout(content)
        clayout.setSpacing(16)

        for seccion, texto in contenido.items():
            lbl_sec = QLabel(seccion)
            lbl_sec.setStyleSheet("font-size: 15px; font-weight: bold; color: #D4AF37; margin-top: 8px;")
            clayout.addWidget(lbl_sec)

            lbl_txt = QLabel(texto)
            lbl_txt.setWordWrap(True)
            lbl_txt.setStyleSheet("font-size: 13px; color: #d0d0d0; padding-left: 8px;")
            clayout.addWidget(lbl_txt)

        clayout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
