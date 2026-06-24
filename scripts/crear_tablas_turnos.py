import psycopg2
conn = psycopg2.connect(host='100.105.199.110', port=5432, dbname='agilize_gestion', user='postgres', password='agilize2025')
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS turnos_laborales (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    hora_entrada TIME NOT NULL,
    hora_salida TIME NOT NULL,
    tolerancia_entrada INTEGER NOT NULL DEFAULT 10,
    tolerancia_salida INTEGER NOT NULL DEFAULT 5,
    es_nocturno BOOLEAN NOT NULL DEFAULT FALSE,
    horas_jornada NUMERIC(4,2) NOT NULL DEFAULT 8,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("turnos_laborales OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS fichajes_pin (
    id SERIAL PRIMARY KEY,
    empleado_id INTEGER NOT NULL REFERENCES empleados(id),
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    tipo VARCHAR(10) NOT NULL,
    metodo VARCHAR(20) NOT NULL DEFAULT 'pin',
    dispositivo VARCHAR(50) NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("fichajes_pin OK")

# Agregar campos de novedades a asistencias
cols = [
    ("tardanza_minutos", "INTEGER NOT NULL DEFAULT 0"),
    ("salida_anticipada_minutos", "INTEGER NOT NULL DEFAULT 0"),
    ("tipo_extra", "VARCHAR(20) NOT NULL DEFAULT ''"),
    ("turno_id", "INTEGER REFERENCES turnos_laborales(id)"),
]
for col, tipo in cols:
    try:
        cur.execute(f"ALTER TABLE asistencias ADD COLUMN {col} {tipo}")
        print(f"+ asistencias.{col}")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        conn.autocommit = True

# Seed turnos basicos
cur.execute("""
INSERT INTO turnos_laborales (codigo, nombre, hora_entrada, hora_salida, es_nocturno, horas_jornada) VALUES
    ('TM', 'Turno Manana', '06:00', '14:00', FALSE, 8),
    ('TT', 'Turno Tarde', '14:00', '22:00', FALSE, 8),
    ('TN', 'Turno Noche', '22:00', '06:00', TRUE, 8),
    ('TC', 'Turno Comercial', '08:00', '17:00', FALSE, 9),
    ('TP', 'Turno Part-Time', '08:00', '12:00', FALSE, 4)
ON CONFLICT (codigo) DO NOTHING
""")
print("seed turnos OK")

cur.close()
conn.close()
print("LISTO")
