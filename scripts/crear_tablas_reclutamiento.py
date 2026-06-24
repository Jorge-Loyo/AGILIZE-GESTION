import psycopg2
conn = psycopg2.connect(host='100.105.199.110', port=5432, dbname='agilize_gestion', user='postgres', password='agilize2025')
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS vacantes (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    departamento_id INTEGER REFERENCES departamentos(id),
    cargo_id INTEGER REFERENCES cargos(id),
    sucursal_id INTEGER REFERENCES sucursales(id),
    cantidad_puestos INTEGER NOT NULL DEFAULT 1,
    tipo_contrato VARCHAR(30) NOT NULL DEFAULT 'indefinido',
    jornada VARCHAR(30) NOT NULL DEFAULT 'completa',
    rango_salarial VARCHAR(100) NOT NULL DEFAULT '',
    descripcion TEXT NOT NULL DEFAULT '',
    requisitos TEXT NOT NULL DEFAULT '',
    fecha_publicacion DATE,
    fecha_cierre DATE,
    estado VARCHAR(20) NOT NULL DEFAULT 'abierta',
    prioridad VARCHAR(20) NOT NULL DEFAULT 'normal',
    responsable_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("vacantes OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS candidatos (
    id SERIAL PRIMARY KEY,
    vacante_id INTEGER NOT NULL REFERENCES vacantes(id) ON DELETE CASCADE,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL DEFAULT '',
    telefono VARCHAR(50) NOT NULL DEFAULT '',
    documento VARCHAR(30) NOT NULL DEFAULT '',
    cv_archivo VARCHAR(250) NOT NULL DEFAULT '',
    experiencia_anios INTEGER NOT NULL DEFAULT 0,
    pretension_salarial VARCHAR(100) NOT NULL DEFAULT '',
    fuente VARCHAR(50) NOT NULL DEFAULT '',
    estado VARCHAR(20) NOT NULL DEFAULT 'postulado',
    fecha_postulacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_entrevista DATE,
    puntaje INTEGER NOT NULL DEFAULT 0,
    notas TEXT NOT NULL DEFAULT '',
    motivo_rechazo VARCHAR(200) NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("candidatos OK")

cur.close()
conn.close()
print("LISTO")
