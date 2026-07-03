import sys
import psycopg2

conn = psycopg2.connect(
    host='100.127.184.115', port=5432,
    dbname='agilize_gestion', user='agilize', password='agilize2025'
)
cur = conn.cursor()

conceptos = [
    ('SAL_COMP', 'Salario Complementario', 'haber', 'no_remunerativo', 'fijo', 'basico', None, None, 'empleado', 1),
    ('BONO_GUERRA', 'Bono de Guerra Complementario', 'haber', 'no_remunerativo', 'fijo', 'basico', None, None, 'empleado', 2),
    ('REEMBOLSO', 'Reembolso', 'haber', 'no_remunerativo', 'fijo', 'basico', None, None, 'todos', 3),
    ('TIEMPO_VIAJE', 'Tiempo de Viaje', 'haber', 'no_remunerativo', 'fijo', 'basico', None, None, 'todos', 4),
    ('SSO', 'Seguro Social Obligatorio (SSO)', 'deduccion', 'retencion', 'porcentaje', 'salario_legal', 1.8462, None, 'empleado', 10),
    ('PARO', 'Paro Forzoso', 'deduccion', 'retencion', 'porcentaje', 'salario_legal', 0.4615, None, 'empleado', 11),
    ('FAOV', 'Ahorro Habitacional (FAOV)', 'deduccion', 'retencion', 'porcentaje', 'total_devengado', 1.0000, None, 'todos', 12),
    ('ISLR_EMP', 'I.S.L.R. Empleados', 'deduccion', 'retencion', 'porcentaje', 'total_devengado', 1.3300, None, 'empleado', 13),
    ('ISLR_DIR', 'I.S.L.R. Directivos', 'deduccion', 'retencion', 'porcentaje', 'total_devengado', 2.6300, None, 'directivo', 14),
    ('PREST_1', 'Descuento por Prestamos (1)', 'deduccion', 'retencion', 'fijo', 'basico', None, 0, 'todos', 15),
    ('PREST_2', 'Descuento por Prestamos (2)', 'deduccion', 'retencion', 'fijo', 'basico', None, 0, 'todos', 16),
    ('OTRAS_DED', 'Otras Deducciones', 'deduccion', 'retencion', 'fijo', 'basico', None, 0, 'todos', 17),
]

for c in conceptos:
    cur.execute(
        """INSERT INTO conceptos_nomina 
           (codigo, nombre, tipo, categoria, calculo, base_calculo, porcentaje, monto_fijo, aplica_a, orden, activo)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,true)""", c
    )

conn.commit()
cur.execute('SELECT count(*) FROM conceptos_nomina')
count = cur.fetchone()[0]
conn.close()
print(f"Conceptos creados: {count}")
