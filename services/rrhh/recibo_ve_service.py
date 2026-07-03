"""Recibo de pago formato Venezuela - Comprobante de Pago LOTTT."""
import os
from datetime import date
from decimal import Decimal
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from core.config import settings, BASE_DIR
from core.database import get_db
from services.core.empresa_service import empresa_service
from sqlalchemy.orm import joinedload
from models.nomina import Liquidacion, LiquidacionDetalle
from models.empleado import Empleado

RECIBOS_DIR = BASE_DIR / "recibos"
RECIBOS_DIR.mkdir(exist_ok=True)

GOLD = colors.HexColor("#D4AF37")
DARK = colors.HexColor("#2D2D2D")


def generar_recibo_ve(liquidacion_id: int) -> str:
    """Genera PDF de comprobante de pago formato Venezuela."""
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
        data = {
            "nombre": f"{emp.nombre} {emp.apellido}".strip(),
            "cedula": emp.dni or "",
            "rif": emp.cuil or "",  # usamos cuil para RIF en VE
            "cargo": emp.cargo.nombre if emp.cargo else "",
            "depto": emp.departamento.nombre if emp.departamento else "",
            "ingreso": emp.fecha_ingreso.strftime("%d/%m/%Y") if emp.fecha_ingreso else "",
            "legajo": emp.legajo or "",
            "categoria": getattr(emp, 'categoria_nomina', 'empleado') or 'empleado',
            "sueldo_mensual": emp.sueldo_mensual or Decimal("0"),
        }
        liq_data = {
            "periodo": liq.periodo,
            "fecha": liq.fecha_liquidacion,
            "basico": liq.sueldo_basico,
            "haberes": liq.total_haberes,
            "deducciones": liq.total_deducciones,
            "neto": liq.neto,
            "tasa": liq.tasa_cambio,
        }
        # Separar detalles por tipo
        haberes = []
        deducciones = []
        for d in liq.detalles:
            item = {"nombre": d.concepto.nombre if d.concepto else "", "codigo": d.concepto.codigo if d.concepto else "", "monto": d.monto}
            if d.tipo == "haber":
                haberes.append(item)
            else:
                deducciones.append(item)

    # Calcular salario diario
    salario_mensual = liq_data["basico"]
    salario_diario = (salario_mensual / Decimal("30")).quantize(Decimal("0.01")) if salario_mensual else Decimal("0")

    # Periodo texto
    year, month = liq_data["periodo"].split("-")
    meses = ["", "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
             "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    mes_nombre = meses[int(month)]
    import calendar
    ultimo_dia = calendar.monthrange(int(year), int(month))[1]
    periodo_texto = f"DESDE EL 01/{month} AL {ultimo_dia}/{month}/{year}"

    # Generar PDF
    filename = f"comprobante_{data['legajo']}_{data['nombre']}_{liq_data['periodo']}.pdf".replace(" ", "_")
    filepath = str(RECIBOS_DIR / filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=1.5*cm, bottomMargin=1.5*cm,
                            leftMargin=1.5*cm, rightMargin=1.5*cm)
    styles = getSampleStyleSheet()
    elements = []

    s_normal = ParagraphStyle("n", parent=styles["Normal"], fontSize=9)
    s_bold = ParagraphStyle("b", parent=styles["Normal"], fontSize=9, fontName="Helvetica-Bold")
    s_center = ParagraphStyle("c", parent=styles["Normal"], fontSize=10, alignment=TA_CENTER, fontName="Helvetica-Bold")
    s_small = ParagraphStyle("sm", parent=styles["Normal"], fontSize=8)
    s_title = ParagraphStyle("t", parent=styles["Normal"], fontSize=12, alignment=TA_CENTER, fontName="Helvetica-Bold")

    # === HEADER ===
    razon_social = empresa_service.obtener("razon_social") or "EMPRESA"
    elements.append(Paragraph(razon_social, s_title))
    elements.append(Paragraph("COMPROBANTE DE PAGO", s_center))
    elements.append(Paragraph(periodo_texto, s_center))
    elements.append(Spacer(1, 4*mm))

    # Nro recibo
    nro = data["legajo"] if data["categoria"] == "empleado" else f"D-{data['legajo']}"
    elements.append(Paragraph(f"Nº {nro}", ParagraphStyle("r", parent=s_bold, alignment=TA_RIGHT)))
    elements.append(Spacer(1, 3*mm))

    # === DATOS EMPLEADO ===
    emp_table = [
        [Paragraph("<b>NOMBRES Y APELLIDOS:</b>", s_small), Paragraph(data["nombre"], s_small),
         Paragraph("<b>C.I.:</b>", s_small), Paragraph(data["cedula"], s_small)],
        [Paragraph("<b>FECHA DE INGRESO:</b>", s_small), Paragraph(data["ingreso"], s_small),
         Paragraph("<b>CARGO:</b>", s_small), Paragraph(data["cargo"], s_small)],
        [Paragraph("<b>DPTO:</b>", s_small), Paragraph(data["depto"], s_small),
         "", ""],
    ]
    t = Table(emp_table, colWidths=[3.8*cm, 6*cm, 2.5*cm, 5.5*cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 4*mm))

    # === DEVENGADO ===
    elements.append(Paragraph("TOTAL DEVENGADO:", s_bold))
    elements.append(Spacer(1, 2*mm))

    # Salario base
    dev_rows = [
        ["DIAS", "30", "SALARIO DIARIO:", f"{salario_diario:,.2f}",
         "Bs.", f"{salario_mensual:,.2f}", "SALARIO MENSUAL:", f"{salario_mensual:,.2f}"],
    ]

    # Horas extras (por ahora en 0, se llenará cuando haya fichadas)
    extras = [
        ("H. EXTRAS DIURNAS", "0"),
        ("H. EXTRAS NOCTURNAS", "0"),
        ("SABADO", "0"),
        ("RECARGO DOMINGO", "0"),
        ("FERIADO", "0"),
    ]
    for nombre, horas in extras:
        dev_rows.append([nombre, "", "Nº HORAS", horas, "Bs.", "0.00", "", ""])

    # Reembolso
    reemb = next((h["monto"] for h in haberes if h["codigo"] == "REEMBOLSO"), Decimal("0"))
    dev_rows.append(["REEMBOLSO", "", "", "", "Bs.", f"{reemb:,.2f}", "", ""])

    # Tiempo de viaje
    tv = next((h["monto"] for h in haberes if h["codigo"] == "TIEMPO_VIAJE"), Decimal("0"))
    dev_rows.append(["TIEMPO DE VIAJE", "", "0", "HORAS", "Bs.", f"{tv:,.2f}", "", ""])

    # Bono complementario (solo empleados)
    bono_comp = Decimal("0")
    for h in haberes:
        if h["codigo"] in ("SAL_COMP", "BONO_GUERRA"):
            bono_comp += h["monto"]
    dev_rows.append(["BONO COMPLEMENTARIO", "", "", "", "Bs.", f"{bono_comp:,.2f}", "", ""])

    # Total devengado
    dev_rows.append(["", "", "", "TOTAL DEVENGADO", "Bs.", f"{liq_data['haberes']:,.2f}", "", ""])

    t_dev = Table(dev_rows, colWidths=[3.5*cm, 1.2*cm, 2.2*cm, 2*cm, 1*cm, 3*cm, 2.8*cm, 3*cm])
    t_dev.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTNAME", (3, -1), (5, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 0.5, colors.black),
        ("ALIGN", (4, 0), (5, -1), "RIGHT"),
    ]))
    elements.append(t_dev)
    elements.append(Spacer(1, 4*mm))

    # === DEDUCCIONES ===
    elements.append(Paragraph("TOTAL DEDUCCIONES:", s_bold))
    elements.append(Spacer(1, 2*mm))

    # Mapeo de codigos a nombres del recibo
    ded_nombres = {
        "SSO": "S.S.O.",
        "ISLR_EMP": "I.S.L.R.",
        "ISLR_DIR": "I.S.L.R.",
        "FAOV": "AHORRO HABITACIONAL",
        "PARO": "PARO FORZOSO",
        "PREST_1": "DESC. POR PRESTAMOS",
        "PREST_2": "DESC. POR PRESTAMOS (2)",
        "OTRAS_DED": "OTRAS",
    }

    ded_rows = []
    for d in deducciones:
        nombre_ded = ded_nombres.get(d["codigo"], d["nombre"])
        ded_rows.append([nombre_ded, "BsS.", f"{d['monto']:,.2f}"])

    # Total deducciones + Total recibido
    ded_rows.append(["TOTAL DEDUCCIONES", "BsS.", f"{liq_data['deducciones']:,.2f}"])

    t_ded = Table(ded_rows, colWidths=[5*cm, 1.5*cm, 3.5*cm])
    t_ded.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(t_ded)
    elements.append(Spacer(1, 3*mm))

    # === TOTAL RECIBIDO ===
    total_row = [["", "", "", "TOTAL RECIBIDO Bs.", f"{liq_data['neto']:,.2f}"]]
    t_total = Table(total_row, colWidths=[3*cm, 3*cm, 3*cm, 4*cm, 4*cm])
    t_total.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
        ("LINEABOVE", (3, 0), (-1, 0), 1.5, GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_total)
    elements.append(Spacer(1, 15*mm))

    # === FIRMA ===
    firma_data = [
        ["", "_________________________"],
        ["", "FIRMA"],
    ]
    t_firma = Table(firma_data, colWidths=[10*cm, 7*cm])
    t_firma.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(t_firma)

    # Tasa de cambio si existe
    if liq_data["tasa"]:
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph(f"Tasa BCV: {liq_data['tasa']:,.4f} Bs/USD", s_small))

    doc.build(elements)
    return filepath
