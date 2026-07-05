"""Genera PDF del recibo real en USD para liquidaciones duales (Casa Dulce VE)."""
import os
from datetime import date
from decimal import Decimal
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from core.config import settings, BASE_DIR
from core.database import get_db
from services.core.empresa_service import empresa_service
from models.liquidacion_dual import LiquidacionDual
from models.empleado import Empleado

RECIBOS_DIR = BASE_DIR / "recibos"
RECIBOS_DIR.mkdir(exist_ok=True)


def generar_recibo_real_usd(dual_id: int) -> str:
    """Genera PDF del recibo real en USD."""
    with get_db() as db:
        dual = db.query(LiquidacionDual).get(dual_id)
        if not dual:
            raise ValueError("Liquidación dual no encontrada")
        emp = db.query(Empleado).get(dual.empleado_id)

        # Extraer datos en sesión
        data = {
            "nombre": f"{emp.nombre} {emp.apellido or ''}".strip(),
            "legajo": emp.legajo or "",
            "dni": emp.dni or "",
            "cargo": emp.cargo.nombre if emp.cargo else "",
            "ingreso": emp.fecha_ingreso.strftime("%d/%m/%Y") if emp.fecha_ingreso else "",
            "periodo": dual.periodo,
            "fecha": dual.fecha.strftime("%d/%m/%Y") if dual.fecha else "",
            "tasa_bcv": dual.tasa_bcv,
            "fecha_tasa": dual.fecha_tasa.strftime("%d/%m/%Y") if dual.fecha_tasa else "",
            "sueldo_legal_bs": dual.sueldo_legal_bs,
            "sueldo_legal_usd": dual.sueldo_legal_usd,
            "complemento_usd": dual.complemento_usd,
            "bono_usd": dual.bono_empresa_usd,
            "canasta_usd": dual.canasta_usd,
            "faltas": dual.faltas,
            "descuento_faltas_usd": dual.descuento_faltas_usd,
            "deducciones_legal_bs": dual.deducciones_legal_bs,
            "deducciones_legal_usd": dual.deducciones_legal_usd,
            "neto_nomina_usd": dual.neto_nomina_usd,
            "neto_total_usd": dual.neto_total_usd,
            "neto_total_bs": dual.neto_total_bs,
            "pago_total_usd": dual.pago_total_usd,
        }

    d = data
    filename = f"recibo_real_{d['legajo']}_{d['periodo']}.pdf".replace(" ", "_")
    filepath = str(RECIBOS_DIR / filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=1.2*cm, bottomMargin=1.2*cm)
    styles = getSampleStyleSheet()
    elements = []

    style_section = ParagraphStyle("section", parent=styles["Heading3"], fontSize=10, spaceAfter=3)
    style_footer = ParagraphStyle("footer", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=colors.gray)

    # === HEADER ===
    razon_social = empresa_service.obtener("razon_social") or settings.APP_NAME
    header_data = [
        [razon_social, "", "RECIBO DE PAGO (USD)"],
        ["", "", f"Periodo: {d['periodo']}"],
        [f"Tasa BCV: {d['tasa_bcv']:,.2f} Bs/USD ({d['fecha_tasa']})", "", f"Fecha: {d['fecha']}"],
    ]
    t_header = Table(header_data, colWidths=[7*cm, 3*cm, 7*cm])
    t_header.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (0, 0), 12),
        ("FONTSIZE", (2, 0), (2, 0), 11),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 6*mm))

    # === DATOS EMPLEADO ===
    elements.append(Paragraph("Datos del Empleado", style_section))
    emp_data = [
        ["Legajo:", d["legajo"], "Nombre:", d["nombre"]],
        ["DNI:", d["dni"], "Cargo:", d["cargo"]],
        ["Ingreso:", d["ingreso"], "", ""],
    ]
    t_emp = Table(emp_data, colWidths=[3*cm, 5*cm, 3*cm, 6*cm])
    t_emp.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#eeeeee")),
    ]))
    elements.append(t_emp)
    elements.append(Spacer(1, 6*mm))

    # === DETALLE HABERES USD ===
    elements.append(Paragraph("Detalle de Haberes (USD)", style_section))
    haberes_data = [
        ["Concepto", "Monto USD"],
        [f"Sueldo Legal ({d['sueldo_legal_bs']:,.2f} Bs ÷ {d['tasa_bcv']:,.2f})", f"$ {d['sueldo_legal_usd']:,.2f}"],
        ["Complemento USD", f"$ {d['complemento_usd']:,.2f}"],
        ["Bono Empresa", f"$ {d['bono_usd']:,.2f}"],
    ]
    t_hab = Table(haberes_data, colWidths=[11*cm, 6*cm])
    t_hab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2D2D2D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_hab)
    elements.append(Spacer(1, 4*mm))

    # === DESCUENTOS ===
    if d["faltas"] > 0 or d["deducciones_legal_usd"] > 0:
        elements.append(Paragraph("Descuentos", style_section))
        desc_data = [["Concepto", "Monto USD"]]
        if d["faltas"] > 0:
            desc_data.append([f"Faltas ({d['faltas']} días × ${d['pago_total_usd']/Decimal('30'):,.2f})", f"- $ {d['descuento_faltas_usd']:,.2f}"])
        if d["deducciones_legal_usd"] > 0:
            desc_data.append([f"Deducciones legales ({d['deducciones_legal_bs']:,.2f} Bs)", f"- $ {d['deducciones_legal_usd']:,.2f}"])
        t_desc = Table(desc_data, colWidths=[11*cm, 6*cm])
        t_desc.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#444444")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("TEXTCOLOR", (1, 1), (1, -1), colors.HexColor("#ef4444")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_desc)
        elements.append(Spacer(1, 4*mm))

    # === TOTALES ===
    elements.append(Paragraph("Resumen", style_section))
    totales_data = [
        ["Subtotal Nómina USD:", f"$ {d['neto_nomina_usd']:,.2f}"],
        ["Canasta (beneficio):", f"$ {d['canasta_usd']:,.2f}"],
        ["TOTAL A COBRAR USD:", f"$ {d['neto_total_usd']:,.2f}"],
        ["Equivalente Bs:", f"Bs {d['neto_total_bs']:,.2f}"],
    ]
    t_tot = Table(totales_data, colWidths=[8*cm, 9*cm])
    t_tot.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 2), (-1, 2), 14),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEABOVE", (0, 2), (-1, 2), 1.5, colors.HexColor("#10b981")),
        ("TOPPADDING", (0, 2), (-1, 2), 8),
        ("TEXTCOLOR", (1, 2), (1, 2), colors.HexColor("#10b981")),
        ("FONTSIZE", (0, 3), (-1, 3), 9),
        ("TEXTCOLOR", (0, 3), (-1, 3), colors.gray),
    ]))
    elements.append(t_tot)
    elements.append(Spacer(1, 15*mm))

    # === FIRMAS ===
    firma_data = [
        ["_________________________", "", "_________________________"],
        ["Firma Empleado", "", "Firma Empleador"],
    ]
    t_firma = Table(firma_data, colWidths=[6*cm, 5*cm, 6*cm])
    t_firma.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 1), (-1, 1), 4),
    ]))
    elements.append(t_firma)

    # Footer
    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph(
        f"Generado el {date.today().strftime('%d/%m/%Y')} - {settings.APP_NAME} v{settings.APP_VERSION}",
        style_footer
    ))

    doc.build(elements)
    return filepath
