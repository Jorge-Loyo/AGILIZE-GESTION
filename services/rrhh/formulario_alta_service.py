"""Genera un formulario PDF en blanco para alta de empleado."""
from pathlib import Path
from datetime import date
from core.config import BASE_DIR
from services.core.empresa_service import empresa_service
from services.core.pais_config_service import label_doc_identidad, label_id_fiscal


def generar_formulario_alta() -> str:
    """Genera PDF con formulario de alta y retorna el filepath."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm, mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    from services.core.logo_service import get_empresa_logo_path, get_app_icon_path

    output_dir = BASE_DIR / "exports"
    output_dir.mkdir(exist_ok=True)
    filepath = str(output_dir / "formulario_alta_empleado.pdf")

    c = canvas.Canvas(filepath, pagesize=A4)
    w, h = A4
    margen = 2 * cm
    gold = HexColor("#D4AF37")
    gris = HexColor("#666666")
    negro = HexColor("#000000")

    datos = empresa_service.obtener_todos()
    empresa = datos.get("razon_social", datos.get("nombre_app", "Empresa"))
    nombre_app = datos.get("nombre_app", "Agilize Gestion")
    pais = (datos.get("cotizacion_pais", "Venezuela")).lower().strip()
    lbl_doc = label_doc_identidad()
    lbl_fiscal = label_id_fiscal()

    # === HEADER con logos ===
    # Logo empresa (izquierda)
    logo_empresa = get_empresa_logo_path()
    if logo_empresa and Path(logo_empresa).exists():
        try:
            c.drawImage(logo_empresa, margen, h - 3.2 * cm, width=1.8 * cm, height=1.8 * cm, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Logo app (derecha, mas grande)
    logo_app = get_app_icon_path()
    if logo_app and Path(logo_app).exists():
        try:
            c.drawImage(logo_app, w - margen - 2.2 * cm, h - 3.4 * cm, width=2.0 * cm, height=2.0 * cm, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Linea dorada superior
    c.setStrokeColor(gold)
    c.setLineWidth(3)
    c.line(margen, h - 1.2 * cm, w - margen, h - 1.2 * cm)

    # Nombre empresa centrado: "Agilize" en dorado, "Gestion" en negro
    c.setFont("Helvetica-Bold", 16)
    texto_agilize = "Agilize"
    texto_gestion = " Gestion"
    ancho_agilize = c.stringWidth(texto_agilize, "Helvetica-Bold", 16)
    ancho_gestion = c.stringWidth(texto_gestion, "Helvetica-Bold", 16)
    ancho_total = ancho_agilize + ancho_gestion
    x_inicio = (w - ancho_total) / 2
    c.setFillColor(gold)
    c.drawString(x_inicio, h - 2.2 * cm, texto_agilize)
    c.setFillColor(negro)
    c.drawString(x_inicio + ancho_agilize, h - 2.2 * cm, texto_gestion)

    c.setFillColor(gris)
    c.setFont("Helvetica", 10)
    c.drawCentredString(w / 2, h - 2.8 * cm, "Formulario de Alta de Empleado")

    c.setFont("Helvetica", 9)
    c.drawRightString(w - margen, h - 3.5 * cm, "Fecha: ____/____/________")

    y = h - 4.5 * cm

    # === HELPERS ===
    def seccion(titulo):
        nonlocal y
        y -= 0.6 * cm
        c.setStrokeColor(gold)
        c.setLineWidth(1.5)
        c.line(margen, y, w - margen, y)
        y -= 0.45 * cm
        c.setFillColor(gold)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margen, y, titulo.upper())
        c.setFillColor(negro)
        y -= 0.7 * cm

    def campo(label, x_start=None, x_end=None):
        nonlocal y
        x = x_start or margen
        fin = x_end or (w - margen)
        c.setFont("Helvetica", 9)
        c.setFillColor(gris)
        c.drawString(x, y + 0.15 * cm, label)
        c.setStrokeColor(HexColor("#cccccc"))
        c.setLineWidth(0.5)
        c.line(x, y - 0.1 * cm, fin, y - 0.1 * cm)
        c.setFillColor(negro)
        y -= 0.85 * cm

    def campo_doble(label1, label2):
        nonlocal y
        medio = w / 2
        c.setFont("Helvetica", 9)
        c.setFillColor(gris)
        c.drawString(margen, y + 0.15 * cm, label1)
        c.setStrokeColor(HexColor("#cccccc"))
        c.setLineWidth(0.5)
        c.line(margen, y - 0.1 * cm, medio - 0.5 * cm, y - 0.1 * cm)
        c.drawString(medio + 0.3 * cm, y + 0.15 * cm, label2)
        c.line(medio + 0.3 * cm, y - 0.1 * cm, w - margen, y - 0.1 * cm)
        c.setFillColor(negro)
        y -= 0.85 * cm

    def campo_triple(label1, label2, label3):
        nonlocal y
        tercio = (w - 2 * margen) / 3
        x1 = margen
        x2 = margen + tercio + 0.3 * cm
        x3 = margen + 2 * tercio + 0.6 * cm
        c.setFont("Helvetica", 9)
        c.setFillColor(gris)
        c.setStrokeColor(HexColor("#cccccc"))
        c.setLineWidth(0.5)
        c.drawString(x1, y + 0.15 * cm, label1)
        c.line(x1, y - 0.1 * cm, x1 + tercio - 0.2 * cm, y - 0.1 * cm)
        c.drawString(x2, y + 0.15 * cm, label2)
        c.line(x2, y - 0.1 * cm, x2 + tercio - 0.2 * cm, y - 0.1 * cm)
        c.drawString(x3, y + 0.15 * cm, label3)
        c.line(x3, y - 0.1 * cm, w - margen, y - 0.1 * cm)
        c.setFillColor(negro)
        y -= 0.85 * cm

    # === DATOS PERSONALES ===
    seccion("Datos Personales")
    campo_doble("Apellido", "Nombre")
    campo_triple(lbl_doc, lbl_fiscal, "Fecha Nac.")
    campo("Domicilio")
    if pais == "venezuela":
        campo_triple("Ciudad", "Estado", "Codigo Postal")
    else:
        campo_triple("Localidad", "Provincia", "Codigo Postal")
    campo_doble("Telefono", "Email")
    campo("Estado Civil")
    campo("Contacto de Emergencia (nombre y telefono)")

    # === DATOS LABORALES ===
    seccion("Datos Laborales")
    campo_doble("Puesto / Cargo", "Departamento / Area")
    campo_doble("Sucursal", "Fecha de Ingreso")
    campo_doble("Horario Entrada", "Horario Salida")

    # Dias laborales con checkboxes
    y -= 0.1 * cm
    c.setFont("Helvetica", 9)
    c.setFillColor(gris)
    c.drawString(margen, y + 0.15 * cm, "Dias laborales:")
    c.setFillColor(negro)
    c.setFont("Helvetica", 10)
    dias = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
    x_dias = margen + 3.5 * cm
    for dia in dias:
        c.rect(x_dias, y - 0.05 * cm, 0.35 * cm, 0.35 * cm)
        c.drawString(x_dias + 0.5 * cm, y + 0.05 * cm, dia)
        x_dias += 2 * cm
    y -= 0.85 * cm

    campo_doble("Tipo de Liquidacion (Hora / Mensual)", "Valor Hora / Sueldo Mensual")

    # === DOCUMENTACION ADJUNTA ===
    seccion("Documentacion Adjunta")
    y -= 0.1 * cm
    c.setFont("Helvetica", 9)
    c.setFillColor(gris)

    if pais == "venezuela":
        docs = [
            f"Fotocopia {lbl_doc} (frente y dorso)",
            f"Copia del {lbl_fiscal}",
            "Constancia de residencia",
            "Certificado de salud",
            "Foto tipo carnet",
            "Cuenta bancaria (numero y banco)",
        ]
    else:
        docs = [
            "Fotocopia DNI (frente y dorso)",
            "Constancia CUIL",
            "Certificado domicilio",
            "Certificado de estudios",
            "Aptitud fisica (apto medico)",
        ]

    for doc in docs:
        c.rect(margen + 0.1 * cm, y - 0.05 * cm, 0.3 * cm, 0.3 * cm)
        c.drawString(margen + 0.7 * cm, y + 0.02 * cm, doc)
        y -= 0.6 * cm

    # === OBSERVACIONES ===
    seccion("Observaciones")
    c.setStrokeColor(HexColor("#cccccc"))
    c.setLineWidth(0.5)
    for _ in range(3):
        c.line(margen, y, w - margen, y)
        y -= 0.65 * cm

    # === FIRMAS ===
    y -= 0.8 * cm
    c.setStrokeColor(negro)
    c.setLineWidth(0.8)
    c.line(margen, y, margen + 6 * cm, y)
    c.line(w - margen - 6 * cm, y, w - margen, y)
    c.setFont("Helvetica", 9)
    c.setFillColor(gris)
    c.drawString(margen, y - 0.4 * cm, "Firma del Empleado")
    c.drawString(w - margen - 6 * cm, y - 0.4 * cm, "Firma del Responsable")

    # === FOOTER ===
    c.setFont("Helvetica", 7)
    c.setFillColor(gris)
    c.drawCentredString(w / 2, 0.7 * cm, f"{nombre_app} — Generado el {date.today().strftime('%d/%m/%Y')}")

    c.save()
    return filepath
