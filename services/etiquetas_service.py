"""
Servicio de generacion de etiquetas en PDF.
- Etiquetas de estante: nombre + precio
- Etiquetas de producto: codigo de barras + nombre + precio
"""
from pathlib import Path
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.barcode import code128, code39, eanbc
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF


def generar_etiquetas_estante(items: list, ruta: str, tamano: tuple = (5, 7)):
    """
    Genera PDF con etiquetas de estante.
    items: [{"codigo": "", "descripcion": "", "precio": "", "cantidad": 1}]
    tamano: (ancho_cm, alto_cm)
    """
    ancho_cm, alto_cm = tamano
    ancho = ancho_cm * cm
    alto = alto_cm * cm

    # Expandir por cantidad
    etiquetas = []
    for item in items:
        for _ in range(item.get("cantidad", 1)):
            etiquetas.append(item)

    # Calcular columnas que entran en A4
    page_w, page_h = A4
    margin = 1 * cm
    usable_w = page_w - 2 * margin
    usable_h = page_h - 2 * margin
    cols = int(usable_w / ancho)
    rows_per_page = int(usable_h / alto)

    doc = SimpleDocTemplate(ruta, pagesize=A4,
                            leftMargin=margin, rightMargin=margin,
                            topMargin=margin, bottomMargin=margin)

    styles = getSampleStyleSheet()
    style_nombre = ParagraphStyle("nombre", parent=styles["Normal"],
                                   fontSize=8, leading=9, alignment=1)
    style_precio = ParagraphStyle("precio", parent=styles["Normal"],
                                   fontSize=14, leading=16, alignment=1, fontName="Helvetica-Bold")
    style_codigo = ParagraphStyle("codigo", parent=styles["Normal"],
                                   fontSize=6, leading=7, alignment=1, textColor=colors.grey)

    elements = []

    # Procesar en bloques de filas
    for page_start in range(0, len(etiquetas), cols * rows_per_page):
        page_items = etiquetas[page_start:page_start + cols * rows_per_page]

        table_data = []
        row_data = []

        for idx, item in enumerate(page_items):
            cell_content = []
            cell_content.append(Paragraph(item["descripcion"][:40], style_nombre))
            if item.get("precio"):
                cell_content.append(Paragraph(str(item["precio"]), style_precio))
            if item.get("codigo"):
                cell_content.append(Paragraph(item["codigo"], style_codigo))

            # Crear una mini-tabla dentro de la celda
            inner = Table([[p] for p in cell_content], colWidths=[ancho - 4 * mm])
            inner.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            row_data.append(inner)

            if len(row_data) == cols:
                table_data.append(row_data)
                row_data = []

        # Fila incompleta
        if row_data:
            while len(row_data) < cols:
                row_data.append("")
            table_data.append(row_data)

        if table_data:
            t = Table(table_data, colWidths=[ancho] * cols, rowHeights=[alto] * len(table_data))
            t.setStyle(TableStyle([
                ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ]))
            elements.append(t)

    doc.build(elements)
    return ruta


def generar_etiquetas_producto(items: list, ruta: str, formato: str = "code128", columnas: int = 3):
    """
    Genera PDF con etiquetas de producto con codigo de barras.
    items: [{"codigo": "", "descripcion": "", "precio": "", "cantidad": 1}]
    formato: "ean13", "code128", "code39"
    """
    # Expandir por cantidad
    etiquetas = []
    for item in items:
        for _ in range(item.get("cantidad", 1)):
            etiquetas.append(item)

    ancho_etiqueta = 6 * cm
    alto_etiqueta = 3 * cm

    doc = SimpleDocTemplate(ruta, pagesize=A4,
                            leftMargin=0.5 * cm, rightMargin=0.5 * cm,
                            topMargin=0.5 * cm, bottomMargin=0.5 * cm)

    styles = getSampleStyleSheet()
    style_desc = ParagraphStyle("desc", parent=styles["Normal"],
                                 fontSize=7, leading=8, alignment=1)
    style_precio = ParagraphStyle("precio", parent=styles["Normal"],
                                   fontSize=9, leading=10, alignment=1, fontName="Helvetica-Bold")

    elements = []
    table_data = []
    row_data = []

    for item in etiquetas:
        codigo = item["codigo"]

        # Generar codigo de barras como imagen
        barcode_img = _crear_barcode(codigo, formato, ancho_etiqueta - 1 * cm)

        # Construir celda
        cell_parts = []
        if item.get("descripcion"):
            cell_parts.append(Paragraph(item["descripcion"][:30], style_desc))
        cell_parts.append(barcode_img)
        if item.get("precio"):
            cell_parts.append(Paragraph(f"$ {item['precio']}", style_precio))

        inner = Table([[p] for p in cell_parts], colWidths=[ancho_etiqueta - 6 * mm])
        inner.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))

        row_data.append(inner)
        if len(row_data) == columnas:
            table_data.append(row_data)
            row_data = []

    if row_data:
        while len(row_data) < columnas:
            row_data.append("")
        table_data.append(row_data)

    if table_data:
        t = Table(table_data,
                  colWidths=[ancho_etiqueta] * columnas,
                  rowHeights=[alto_etiqueta] * len(table_data))
        t.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 1 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1 * mm),
        ]))
        elements.append(t)

    doc.build(elements)
    return ruta


def _crear_barcode(codigo: str, formato: str, ancho) -> Drawing:
    """Crea un codigo de barras como Drawing de ReportLab."""
    bar_height = 1.2 * cm
    bar_width = ancho

    d = Drawing(float(bar_width), float(bar_height) + 4 * mm)

    if formato == "ean13":
        # EAN-13 requiere exactamente 12-13 digitos
        codigo_clean = "".join(c for c in codigo if c.isdigit())
        if len(codigo_clean) < 12:
            codigo_clean = codigo_clean.ljust(12, "0")
        codigo_clean = codigo_clean[:12]
        bc = eanbc.Ean13BarcodeWidget(codigo_clean)
    elif formato == "code39":
        bc = code39.Extended39(codigo, barWidth=0.5 * mm, barHeight=bar_height, humanReadable=True)
        d.add(bc)
        return d
    elif formato == "code128":
        bc = code128.Code128(codigo, barWidth=0.5 * mm, barHeight=bar_height, humanReadable=True)
        d.add(bc)
        return d
    else:
        bc = code128.Code128(codigo, barWidth=0.5 * mm, barHeight=bar_height, humanReadable=True)
        d.add(bc)
        return d

    bc.x = 0
    bc.y = 0
    d.add(bc)
    return d
