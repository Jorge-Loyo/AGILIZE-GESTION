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
from services.empresa_service import empresa_service
from sqlalchemy.orm import joinedload
from models.nomina import Liquidacion, LiquidacionDetalle
from models.empleado import Empleado

RECIBOS_DIR = BASE_DIR / "recibos"
RECIBOS_DIR.mkdir(exist_ok=True)


def generar_recibo_pdf(liquidacion_id: int) -> str:
    """Genera el PDF del recibo y retorna la ruta del archivo."""
    with get_db() as db:
        liq = (
            db.query(Liquidacion)
            .options(
                joinedload(Liquidacion.empleado).joinedload(Empleado.departamento),
                joinedload(Liquidacion.empleado).joinedload(Empleado.cargo),
                joinedload(Liquidacion.detalles).joinedload(LiquidacionDetalle.concepto),
            )
            .get(liquidacion_id)
        )
        if not liq:
            raise ValueError("Liquidacion no encontrada")

        emp = liq.empleado
        emp_nombre = emp.nombre
        emp_apellido = emp.apellido
        emp_dni = emp.dni
        emp_cuil = emp.cuil
        emp_id = emp.id
        emp_depto = emp.departamento.nombre if emp.departamento else "\u2014"
        emp_cargo = emp.cargo.nombre if emp.cargo else "\u2014"
        emp_ingreso = emp.fecha_ingreso.strftime("%d/%m/%Y") if emp.fecha_ingreso else "\u2014"
        liq_periodo = liq.periodo
        liq_basico = liq.sueldo_basico
        liq_haberes = liq.total_haberes
        liq_deducciones = liq.total_deducciones
        liq_neto = liq.neto
        detalles_data = [(d.concepto.nombre if d.concepto else "\u2014", d.tipo, d.monto) for d in liq.detalles]

    filename = f"recibo_{emp_apellido}_{emp_nombre}_{liq_periodo}.pdf".replace(" ", "_")
    filepath = str(RECIBOS_DIR / filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    elements = []

    style_title = ParagraphStyle("title_recibo", parent=styles["Heading1"], fontSize=16, alignment=TA_CENTER, textColor=colors.HexColor("#D4AF37"))
    style_subtitle = ParagraphStyle("sub_recibo", parent=styles["Normal"], fontSize=10, alignment=TA_CENTER, textColor=colors.gray)
    style_section = ParagraphStyle("section_recibo", parent=styles["Heading3"], fontSize=11, spaceAfter=4)

    # Header
    app_name = empresa_service.obtener("dev_nombre") or settings.APP_NAME
    elements.append(Paragraph(app_name, style_title))
    elements.append(Paragraph("Recibo de Sueldo", style_subtitle))
    elements.append(Spacer(1, 8*mm))

    # Datos empleado
    elements.append(Paragraph("Datos del Empleado", style_section))
    emp_data = [
        ["Nombre:", f"{emp_nombre} {emp_apellido}", "DNI:", emp_dni],
        ["CUIL:", emp_cuil, "Legajo:", str(emp_id)],
        ["Departamento:", emp_depto, "Cargo:", emp_cargo],
        ["Fecha Ingreso:", emp_ingreso, "Periodo:", liq_periodo],
    ]
    t = Table(emp_data, colWidths=[3*cm, 5.5*cm, 3*cm, 5.5*cm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 6*mm))

    # Detalle
    elements.append(Paragraph("Detalle de Haberes y Deducciones", style_section))
    detail_data = [["Concepto", "Tipo", "Monto"]]
    detail_data.append(["Sueldo Basico (Asistencia)", "Haber", f"$ {liq_basico:,.2f}"])
    for nombre, tipo, monto in detalles_data:
        detail_data.append([nombre, tipo.capitalize(), f"$ {monto:,.2f}"])

    t2 = Table(detail_data, colWidths=[8*cm, 3.5*cm, 5.5*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2D2D2D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 6*mm))

    # Totales
    elements.append(Paragraph("Resumen", style_section))
    totales_data = [
        ["Total Haberes:", f"$ {liq_haberes:,.2f}"],
        ["Total Deducciones:", f"$ {liq_deducciones:,.2f}"],
        ["NETO A COBRAR:", f"$ {liq_neto:,.2f}"],
    ]
    t3 = Table(totales_data, colWidths=[8*cm, 9*cm])
    t3.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 12),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#D4AF37")),
        ("TOPPADDING", (0, -1), (-1, -1), 8),
    ]))
    elements.append(t3)
    elements.append(Spacer(1, 15*mm))

    # Firmas
    firma_data = [
        ["_________________________", "", "_________________________"],
        ["Firma Empleado", "", "Firma Empleador"],
    ]
    t4 = Table(firma_data, colWidths=[6*cm, 5*cm, 6*cm])
    t4.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 1), (-1, 1), 4),
    ]))
    elements.append(t4)

    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(
        f"Generado el {date.today().strftime('%d/%m/%Y')} - {app_name} v{settings.APP_VERSION}",
        style_subtitle
    ))

    doc.build(elements)
    return filepath
