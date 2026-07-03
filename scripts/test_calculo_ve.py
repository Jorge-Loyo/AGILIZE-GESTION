"""Test: Verificar que el motor reproduce los numeros del Excel de Casa Dulce."""
from decimal import Decimal

# Simular _calcular_monto_concepto sin BD
def calcular(calculo, base_calculo, porcentaje, monto_fijo, salario_legal, total_devengado):
    if calculo == "porcentaje" and porcentaje:
        if base_calculo == "salario_legal":
            base = salario_legal
        elif base_calculo == "total_devengado":
            base = total_devengado
        else:
            base = salario_legal
        return (base * porcentaje / Decimal("100")).quantize(Decimal("0.01"))
    if calculo == "fijo" and monto_fijo and monto_fijo > 0:
        return monto_fijo
    return Decimal("0")


# === EMPLEADO 1: Dairilys ===
print("=== EMPLEADO 1 (Dairilys) ===")
salario_mensual = Decimal("1300")  # salario legal
sal_comp = Decimal("63325.496")
bono_guerra = Decimal("8442.384")

total_devengado = salario_mensual + sal_comp + bono_guerra
print(f"Total devengado: {total_devengado} (esperado: 73067.88)")

# Deducciones
sso = calcular("porcentaje", "salario_legal", Decimal("1.8462"), None, salario_mensual, total_devengado)
paro = calcular("porcentaje", "salario_legal", Decimal("0.4615"), None, salario_mensual, total_devengado)
faov = calcular("porcentaje", "total_devengado", Decimal("1.0000"), None, salario_mensual, total_devengado)
islr = calcular("porcentaje", "total_devengado", Decimal("1.3300"), None, salario_mensual, total_devengado)

print(f"SSO: {sso} (esperado: ~24.00)")
print(f"Paro: {paro} (esperado: ~6.00)")
print(f"FAOV: {faov} (esperado: ~730.68)")
print(f"ISLR: {islr} (esperado: ~971.80)")

total_ded = sso + paro + faov + islr
neto = total_devengado - total_ded
print(f"Total deducciones: {total_ded} (esperado: ~1732.48)")
print(f"Neto: {neto} (esperado: ~71335.40)")

# === DIRECTIVO D-1: Elias ===
print("\n=== DIRECTIVO D-1 (Elias) ===")
salario_dir = Decimal("146135.76")
total_dev_dir = salario_dir  # sin bonos

islr_dir = calcular("porcentaje", "total_devengado", Decimal("2.6300"), None, salario_dir, total_dev_dir)
print(f"ISLR directivo: {islr_dir} (esperado: ~3843.37)")
neto_dir = total_dev_dir - islr_dir
print(f"Neto: {neto_dir} (esperado: ~142292.39)")
