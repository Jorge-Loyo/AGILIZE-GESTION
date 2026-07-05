"""Test end-to-end de liquidación dual."""
from decimal import Decimal
from datetime import date
from core.database import get_db
from models.empleado import Empleado
from models.historial_dolar import HistorialDolar
from services.rrhh.nomina_ve_service import nomina_ve_service
from services.rrhh.recibo_real_ve_service import generar_recibo_real_usd

# Crear empleado dual
with get_db() as db:
    emp = Empleado(
        legajo='CD02', nombre='Carlos', apellido='Perez',
        dni='V-87654321', cuil='J-87654321-0',
        fecha_ingreso=date(2023, 3, 1),
        tipo_liquidacion='mensual',
        sueldo_mensual=Decimal('1300'),
        pago_total_usd=Decimal('240'),
        canasta_usd=Decimal('40'),
        bono_empresa_usd=Decimal('70'),
    )
    db.add(emp)
    # Tasa BCV
    existente = db.query(HistorialDolar).filter_by(fecha=date(2026, 7, 3), pais='venezuela').first()
    if not existente:
        tasa = HistorialDolar(fecha=date(2026, 7, 3), valor=Decimal('670.00'), fuente='BCV', pais='venezuela')
        db.add(tasa)
    db.commit()
    emp_id = emp.id
    print(f"Empleado creado: ID={emp_id}")

# Verificar detección dual
print(f"Es dual: {nomina_ve_service.es_dual(emp_id)}")

# Preview
preview = nomina_ve_service.calcular_preview(emp_id, Decimal('670.00'), faltas=1)
print(f"Preview: Neto nomina={preview['neto_nomina_usd']} | Total={preview['neto_total_usd']}")

# Liquidar
dual = nomina_ve_service.liquidar_dual(emp_id, '2026-07', date(2026, 7, 3), Decimal('670.00'), faltas=1)
print(f"Liquidación dual ID={dual.id}")
print(f"  Sueldo legal USD: {dual.sueldo_legal_usd}")
print(f"  Complemento: {dual.complemento_usd}")
print(f"  Bono: {dual.bono_empresa_usd}")
print(f"  Descuento faltas: {dual.descuento_faltas_usd}")
print(f"  Neto nómina USD: {dual.neto_nomina_usd}")
print(f"  Neto total USD: {dual.neto_total_usd}")
print(f"  Neto total Bs: {dual.neto_total_bs}")

# Generar PDF
path = generar_recibo_real_usd(dual.id)
print(f"PDF generado: {path}")
