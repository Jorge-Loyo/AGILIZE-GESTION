# Agilize Gestión

Sistema empresarial modular de escritorio desarrollado en Python.

## Requisitos

- Python 3.11+
- PostgreSQL 18

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Copiar .env.example a .env y editar con tus datos
copy .env.example .env

# Crear la base de datos en PostgreSQL
# CREATE DATABASE agilize_gestion;

# Ejecutar migraciones
alembic upgrade head

# Poblar datos iniciales
python -m scripts.seed
```

## Ejecución

```bash
python main.py
```

## Estructura

Ver `docs/PLAN_DE_ACCION.md` para el plan completo del proyecto.
