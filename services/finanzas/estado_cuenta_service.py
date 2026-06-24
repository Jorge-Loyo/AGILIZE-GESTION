"""Genera PDF de estado de cuenta para clientes."""
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from services.core.empresa_service import empresa_service


def generar_estado_cuenta_pdf(ruta: str, cliente_nombre: str, movimientos: list, saldo: float):
    """Genera un PDF con el estado de cuenta del cliente."""
    doc = SimpleDocTemplate(ruta, pagesize=A4,
                            leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)

    styles = getSampleStyleSheet()
    elements = []

    # Encabezado empresa
    empresa_nombre = empresa_service.obtener("razon_social") or empresa_service.obtener("nombre_app") or "Empresa"
    elements.append(Paragraph(empresa_nombre, styles["Title"]))
    elements.append(Spacer(1, 0.3 * cm))

    # Titulo
    elements.append(Paragraph("ESTADO DE CUENTA", ParagraphStyle(
        "titulo_ec", parent=styles["Heading2"], alignment=1
    )))
    elements.append(Spacer(1, 0.5 * cm))

    # Info cliente
    elements.append(Paragraph(f"<b>Cliente:</b> {cliente_nombre}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Fecha:</b> {date.today().strftime('%d/%m/%Y')}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Saldo Actual:</b> $ {saldo:,.2f}", ParagraphStyle(
        "saldo", parent=styles["Normal"], fontSize=12, textColor=colors.red if saldo > 0 else colors.green
    )))
    elements.append(Spacer(1, 0.8 * cm))

    # Tabla de movimientos
    data = [["Fecha", "Concepto", "Comprobante", "Debe", "Haber", "Saldo"]]

    for m in movimientos:
        fecha = m.fecha.strftime("%d/%m/%Y") if m.fecha else ""
        debe = f"$ {m.monto:,.2f}" if m.tipo == "debe" else ""
        haber = f"$ {m.monto:,.2f}" if m.tipo == "haber" else ""
        data.append([fecha, m.concepto[:40], m.comprobante or "", debe, haber, f"$ {m.saldo:,.2f}"])

    if len(data) > 1:
        col_widths = [2.2 * cm, 6 * cm, 3 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm]
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D4AF37")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No hay movimientos registrados.", styles["Normal"]))

    elements.append(Spacer(1, 1 * cm))

    # Pie
    elements.append(Paragraph(
        "Este documento es un resumen de su cuenta corriente. "
        "Para consultas comuniquese con nuestro departamento de cobranzas.",
        ParagraphStyle("pie", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    ))

    doc.build(elements)
    return ruta
