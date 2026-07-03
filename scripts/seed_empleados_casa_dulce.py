"""Importar empleados de Casa Dulce Oriente desde datos del Excel de nomina."""
import sys
import psycopg2
from datetime import date

conn = psycopg2.connect(
    host='100.127.184.115', port=5432,
    dbname='agilize_gestion', user='agilize', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

# Crear departamentos
deptos = ['ADMINISTRACION', 'OPERACIONES', 'ATENCION AL CLIENTE', 'PRESIDENCIA']
for d in deptos:
    cur.execute("INSERT INTO departamentos (nombre, activo) VALUES (%s, true) ON CONFLICT (nombre) DO NOTHING", (d,))

# Crear cargos
cargos = ['ENCARGADA DE TIENDA', 'LOGISTICA', 'ASESORA DE VENTAS', 'CAJERA', 'PRESIDENTE', 'VICEPRESIDENTE']
for c in cargos:
    cur.execute("INSERT INTO cargos (nombre, activo) VALUES (%s, true) ON CONFLICT (nombre) DO NOTHING", (c,))

# Obtener IDs
cur.execute("SELECT id, nombre FROM departamentos")
depto_map = {r[1]: r[0] for r in cur.fetchall()}
cur.execute("SELECT id, nombre FROM cargos")
cargo_map = {r[1]: r[0] for r in cur.fetchall()}

# Empleados del Excel
empleados = [
    # (legajo, nombre, apellido, dni, cuil(RIF), fecha_ingreso, cargo, depto, sueldo_mensual, categoria)
    ('1', 'DAIRILYS DEL CARMEN', 'GUAREGUA CHAGUAN', '16067033', 'V-16067033-5', '2023-03-16', 'ENCARGADA DE TIENDA', 'ADMINISTRACION', 1300.00, 'empleado'),
    ('2', 'EMILIO JOSE', 'PINTO DOMIGUEZ', '8326409', 'V-08326409-4', '2023-03-16', 'LOGISTICA', 'OPERACIONES', 1300.00, 'empleado'),
    ('3', 'JESUS RAFAEL', 'ARAY CAGUANA', '8234036', 'V-08234036-6', '2023-10-19', 'LOGISTICA', 'OPERACIONES', 1300.00, 'empleado'),
    ('4', 'THEISY DEL CARMEN', 'NADALES LOPEZ', '19316663', 'V-19316663-2', '2025-07-01', 'ASESORA DE VENTAS', 'ATENCION AL CLIENTE', 1300.00, 'empleado'),
    ('5', 'MARIA VICTORIA', 'GUAITA CANELON', '31311552', 'V-31311552-2', '2025-07-01', 'CAJERA', 'ATENCION AL CLIENTE', 1300.00, 'empleado'),
    ('D-1', 'ELIAS ANTONIO', 'NAYATI VARGAS', '15514275', 'V-15514275-4', '2023-10-20', 'PRESIDENTE', 'PRESIDENCIA', 146135.76, 'directivo'),
    ('D-2', 'KARELIS ADREINA', 'ESPLUGUEZ SARMIENTO', '16489561', 'V-16489561-7', '2023-10-20', 'VICEPRESIDENTE', 'PRESIDENCIA', 146135.76, 'directivo'),
]

for emp in empleados:
    legajo, nombre, apellido, dni, rif, ingreso, cargo, depto, sueldo, categoria = emp
    cur.execute("""
        INSERT INTO empleados (
            legajo, nombre, apellido, dni, cuil, fecha_ingreso,
            cargo_id, departamento_id, sueldo_mensual,
            tipo_liquidacion, categoria_nomina, activo,
            horas_jornada, dias_laborales, hora_entrada, hora_salida,
            sexo, estado_civil, nacionalidad, email, telefono, celular,
            direccion, ciudad, codigo_postal, valor_hora, valor_hora_extra,
            emergencia_nombre, emergencia_telefono, emergencia_parentesco,
            grupo_sanguineo, obra_social, nro_afiliado, alergias,
            tipo_contrato, motivo_egreso, banco, tipo_cuenta, numero_cuenta,
            cbu_clabe, observaciones
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,'mensual',%s,true,8,
            'lun,mar,mie,jue,vie,sab','08:00','17:00',
            '','','venezolana','','','',
            '','','',0,0,
            '','','',
            '','','','',
            'indefinido','','','','',
            '',''
        )
    """, (
        legajo, nombre, apellido, dni, rif, ingreso,
        cargo_map[cargo], depto_map[depto], sueldo, categoria
    ))

cur.execute("SELECT count(*) FROM empleados")
count = cur.fetchone()[0]
conn.close()
print(f"Empleados importados: {count}")
