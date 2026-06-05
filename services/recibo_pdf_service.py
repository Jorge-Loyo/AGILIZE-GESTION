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
from models.sucursal import Sucursal

RECIBOS_DIR = BASE_DIR / "recibos"
RECIBOS_DIR.mkdir(exist_ok=True)


def generar_recibo_pdf(liquidacion_id: int) -> str:
    """Genera el PDF del recibo con detalle completo."""
    with get_db() as db:
        liq = (
            db.query(Liquidacion)
            .options(
                joinedload(Liquidacion.empleado).joinedload(Empleado.departamento),
                joinedload(Liquidacion.empleado).joinedload(Empleado.cargo),
                joinedload(Liquidacion.empleado).joinedload(Empleado.sucursal),
                joinedload(Liquidacion.detalles).joinedload(LiquidacionDetalle.concepto),
            )
            .get(liquidacion_id)
        )
        if not liq:
            raise ValueError("Liquidacion no encontrada")

        emp = liq.empleado

        # Extraer datos en sesion
        emp_nombre = emp.nombre
        emp_apellido = emp.apellido or ""
        emp_dni = emp.dni or ""
        emp_cuil = emp.cuil or ""
        emp_legajo = emp.legajo or ""
        emp_depto = emp.departamento.nombre if emp.departamento else ""
        emp_cargo = emp.cargo.nombre if emp.cargo else ""
        emp_sucursal = emp.sucursal.nombre if emp.sucursal else ""
        emp_ingreso = emp.fecha_ingreso.strftime("%d/%m/%Y") if emp.fecha_ingreso else ""
        emp_valor_hora = emp.valor_hora or Decimal("0")
        emp_valor_hora_extra = emp.valor_hora_extra or emp_valor_hora
        liq_periodo = liq.periodo
        liq_basico = liq.sueldo_basico
        liq_haberes = liq.total_haberes
        liq_deducciones = liq.total_deducciones
        liq_neto = liq.neto
        liq_fecha = liq.fecha_liquidacion
        detalles_data = [(d.concepto.nombre if d.concepto else "", d.tipo, d.monto) for d in liq.detalles]

    # Calcular detalle de asistencia
    from services.calculo_asistencia_service import calculo_asistencia_service
    calc = calculo_asistencia_service.calcular_bruto_periodo(liq.empleado_id, liq_periodo)

    filename = f"recibo_{emp_legajo}_{emp_apellido}_{emp_nombre}_{liq_periodo}.pdf".replace(" ", "_")
    filepath = str(RECIBOS_DIR / filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=1.2*cm, bottomMargin=1.2*cm)
    styles = getSampleStyleSheet()
    elements = []

    style_title = ParagraphStyle("title_recibo", parent=styles["Heading1"], fontSize=14, alignment=TA_CENTER, textColor=colors.HexColor("#D4AF37"))
    style_subtitle = ParagraphStyle("sub_recibo", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER, textColor=colors.gray)
    style_section = ParagraphStyle("section_recibo", parent=styles["Heading3"], fontSize=10, spaceAfter=3)

    # === HEADER ===
    app_name = empresa_service.obtener("dev_nombre") or settings.APP_NAME
    razon_social = empresa_service.obtener("razon_social") or app_name
    cuit_empresa = empresa_service.obtener("cuit") or ""

    header_data = [
        [razon_social, "", "RECIBO DE SUELDO"],
        [f"CUIT: {cuit_empresa}", "", f"Periodo: {liq_periodo}"],
        ["", "", f"Fecha Liquidacion: {liq_fecha.strftime('%d/%m/%Y') if liq_fecha else ''}"],
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
    elements.append(Spacer(1, 5*mm))

    # === DATOS EMPLEADO ===
    elements.append(Paragraph("Datos del Empleado", style_section))
    emp_data = [
        ["Legajo:", emp_legajo, "Nombre:", f"{emp_nombre} {emp_apellido}"],
        ["DNI:", emp_dni, "CUIL:", emp_cuil],
        ["Departamento:", emp_depto, "Cargo:", emp_cargo],
        ["Sucursal:", emp_sucursal, "Fecha Ingreso:", emp_ingreso],
        ["Valor Hora:", f"$ {emp_valor_hora:,.2f}", "Valor Hora Extra:", f"$ {emp_valor_hora_extra:,.2f}"],
    ]
    t_emp = Table(emp_data, colWidths=[3*cm, 5*cm, 3.5*cm, 5.5*cm])
    t_emp.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#eeeeee")),
    ]))
    elements.append(t_emp)
    elements.append(Spacer(1, 5*mm))

    # === DETALLE DE ASISTENCIA ===
    elements.append(Paragraph("Detalle de Asistencia", style_section))
    asist_data = [
        ["Concepto", "Horas", "Valor", "Multiplicador", "Subtotal"],
        ["Horas Normales", str(calc["hs_normales"]), f"$ {emp_valor_hora:,.2f}", "1.00x", f"$ {calc['monto_normales']:,.2f}"],
        ["Horas Extra", str(calc["hs_extra"]), f"$ {emp_valor_hora_extra:,.2f}", f"{float(calc['mult_extra']):.2f}x", f"$ {calc['monto_extra']:,.2f}"],
        ["Horas Sabado", str(calc["hs_sabado"]), f"$ {emp_valor_hora_extra:,.2f}", f"{float(calc['mult_sabado']):.2f}x", f"$ {calc['monto_sabado']:,.2f}"],
        ["Horas Domingo", str(calc["hs_domingo"]), f"$ {emp_valor_hora_extra:,.2f}", f"{float(calc['mult_domingo']):.2f}x", f"$ {calc['monto_domingo']:,.2f}"],
        ["Horas Feriado", str(calc["hs_feriado"]), f"$ {emp_valor_hora_extra:,.2f}", f"{float(calc['mult_feriado']):.2f}x", f"$ {calc['monto_feriado']:,.2f}"],
        ["", "", "", "BRUTO ASISTENCIA:", f"$ {calc['bruto']:,.2f}"],
    ]
    t_asist = Table(asist_data, colWidths=[4*cm, 2.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
    t_asist.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2D2D2D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -2), 0.3, colors.HexColor("#cccccc")),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (3, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#D4AF37")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_asist)

    # Info dias
    elements.append(Spacer(1, 2*mm))
    elements.append(Paragraph(f"Dias trabajados: {calc['dias_trabajados']}", style_subtitle))
    elements.append(Spacer(1, 4*mm))

    # === CONCEPTOS APLICADOS ===
    if detalles_data:
        elements.append(Paragraph("Conceptos Aplicados", style_section))
        concept_data = [["Concepto", "Tipo", "Monto"]]
        for nombre, tipo, monto in detalles_data:
            concept_data.append([nombre, tipo.capitalize(), f"$ {monto:,.2f}"])

        t_concept = Table(concept_data, colWidths=[8*cm, 4*cm, 5*cm])
        t_concept.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#444444")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(t_concept)
        elements.append(Spacer(1, 5*mm))

    # === TOTALES ===
    elements.append(Paragraph("Resumen", style_section))
    totales_data = [
        ["Total Haberes:", f"$ {liq_haberes:,.2f}"],
        ["Total Deducciones:", f"$ {liq_deducciones:,.2f}"],
        ["NETO A COBRAR:", f"$ {liq_neto:,.2f}"],
    ]
    t_tot = Table(totales_data, colWidths=[8*cm, 9*cm])
    t_tot.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 13),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEABOVE", (0, -1), (-1, -1), 1.5, colors.HexColor("#D4AF37")),
        ("TOPPADDING", (0, -1), (-1, -1), 8),
    ]))
    elements.append(t_tot)
    elements.append(Spacer(1, 12*mm))

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
        f"Generado el {date.today().strftime('%d/%m/%Y')} - {app_name} v{settings.APP_VERSION}",
        style_subtitle
    ))

    doc.build(elements)
    return filepath
