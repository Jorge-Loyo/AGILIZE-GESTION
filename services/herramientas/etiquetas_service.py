"""
Servicio de generacion de etiquetas en PDF.
- Etiquetas de estante: nombre + precio
- Etiquetas de producto: codigo de barras + nombre + precio
"""
from pathlib import Path
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.barcode import code128, code39, eanbc
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF


def generar_etiquetas_estante(items: list, ruta: str, tamano: tuple = (5, 7)):
    """
    Genera PDF con etiquetas de estante en hoja horizontal (landscape).
    Cada etiqueta es apaisada (mas ancha que alta) con espacio de corte.
    items: [{"codigo": "", "descripcion": "", "precio": "", "cantidad": 1}]
    tamano: (ancho_cm, alto_cm) - referencia, se adapta a landscape
    """
    # Expandir por cantidad
    etiquetas = []
    for item in items:
        for _ in range(item.get("cantidad", 1)):
            etiquetas.append(item)

    # Hoja horizontal
    pagesize = landscape(A4)
    page_w, page_h = pagesize
    margin = 1.0 * cm
    gap = 0.4 * cm  # espacio de corte entre etiquetas

    usable_w = page_w - 2 * margin
    usable_h = page_h - 2 * margin

    # Etiqueta apaisada: ancho > alto
    # Grande: 3 cols x 2 filas, Mediano: 4x3, Pequeno: 5x4
    ancho_cm, alto_cm = tamano
    if ancho_cm >= 7:
        cols, rows_per_page = 3, 2
    elif ancho_cm >= 5:
        cols, rows_per_page = 4, 3
    else:
        cols, rows_per_page = 5, 4

    ancho = (usable_w - gap * (cols - 1)) / cols
    alto = (usable_h - gap * (rows_per_page - 1)) / rows_per_page

    doc = SimpleDocTemplate(ruta, pagesize=pagesize,
                            leftMargin=margin, rightMargin=margin,
                            topMargin=margin, bottomMargin=margin)

    styles = getSampleStyleSheet()
    style_nombre = ParagraphStyle("nombre", parent=styles["Normal"],
                                   fontSize=14, leading=16, alignment=1,
                                   fontName="Helvetica-Bold")
    style_precio = ParagraphStyle("precio", parent=styles["Normal"],
                                   fontSize=22, leading=24, alignment=1,
                                   fontName="Helvetica-Bold")

    # Logo de empresa grande
    logo_img = _get_empresa_logo_image(max_w=ancho * 0.55, max_h=1.8 * cm)

    elements = []

    for page_start in range(0, len(etiquetas), cols * rows_per_page):
        page_items = etiquetas[page_start:page_start + cols * rows_per_page]

        table_data = []
        row_data = []

        for item in page_items:
            cell_content = []

            if logo_img:
                cell_content.append(logo_img)

            cell_content.append(Paragraph(item["descripcion"][:50], style_nombre))

            if item.get("codigo"):
                bc = _crear_barcode(item["codigo"], "code128", ancho * 0.55)
                cell_content.append(bc)

            if item.get("precio"):
                from services.core.pais_config_service import moneda
                cell_content.append(Paragraph(f"{moneda()} {item['precio']}", style_precio))

            inner = Table([[p] for p in cell_content], colWidths=[ancho - 4 * mm])
            inner.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]))
            row_data.append(inner)

            if len(row_data) == cols:
                table_data.append(row_data)
                row_data = []

        if row_data:
            while len(row_data) < cols:
                row_data.append("")
            table_data.append(row_data)

        if table_data:
            # Anchos con gap entre columnas
            col_widths = [ancho + gap] * (cols - 1) + [ancho]
            row_heights = [alto + gap] * (len(table_data) - 1) + [alto]
            if len(table_data) == 1:
                row_heights = [alto]

            t = Table(table_data, colWidths=col_widths, rowHeights=row_heights)
            t.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
                # Linea de corte punteada
                ("GRID", (0, 0), (-1, -1), 0.3, colors.Color(0.6, 0.6, 0.6)),
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
    bar_height = 0.6 * cm
    try:
        if formato == "ean13":
            codigo_clean = "".join(c for c in codigo if c.isdigit())
            if len(codigo_clean) < 12:
                codigo_clean = codigo_clean.ljust(12, "0")
            codigo_clean = codigo_clean[:12]
            d = createBarcodeDrawing("EAN13", value=codigo_clean,
                                     barHeight=bar_height, humanReadable=True,
                                     width=float(ancho))
        elif formato == "code39":
            d = createBarcodeDrawing("Standard39", value=codigo,
                                     barHeight=bar_height, humanReadable=True,
                                     barWidth=0.4 * mm)
        else:
            d = createBarcodeDrawing("Code128", value=codigo,
                                     barHeight=bar_height, humanReadable=True,
                                     barWidth=0.4 * mm)
        return d
    except Exception:
        # Fallback: retornar drawing vacio
        return Drawing(float(ancho), float(bar_height))


def _get_empresa_logo_image(max_w, max_h):
    """Obtiene el logo de empresa como Image de ReportLab, o None."""
    try:
        from services.core.logo_service import get_empresa_logo_path
        path = get_empresa_logo_path()
        if path and Path(path).exists():
            img = Image(path)
            # Escalar proporcionalmente
            ratio = min(float(max_w) / img.drawWidth, float(max_h) / img.drawHeight)
            img.drawWidth *= ratio
            img.drawHeight *= ratio
            img.hAlign = "CENTER"
            return img
    except Exception:
        pass
    return None
