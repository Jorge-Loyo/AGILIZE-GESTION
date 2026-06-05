# Agilize Gestion

Sistema empresarial modular de escritorio desarrollado en Python.

## Requisitos

- Python 3.11+
- PostgreSQL 18
- Git (para actualizaciones automaticas)

## Instalacion Rapida

### Windows
```bat
# Ejecutar el instalador
install_windows.bat
```

### Linux
```bash
# Dar permisos y ejecutar
chmod +x install_linux.sh
./install_linux.sh
```

## Instalacion Manual

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate
# Activar (Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Copiar .env.example a .env y editar con tus datos
# Windows: copy .env.example .env
# Linux: cp .env.example .env

# Crear la base de datos en PostgreSQL
# CREATE DATABASE agilize_gestion;

# Ejecutar migraciones
alembic upgrade head

# Poblar datos iniciales
python -m scripts.seed
```

## Ejecucion

```bash
# Windows
venv\Scripts\python main.py

# Linux
venv/bin/python main.py
```

## Generar Ejecutable

```bash
# Instalar PyInstaller
pip install pyinstaller

# Generar ejecutable
python scripts/build.py

# O usar el spec directamente
pyinstaller agilize.spec
```

El ejecutable se genera en `dist/AgilizeGestion/`

## Configuracion de Red Local

La aplicacion se conecta a PostgreSQL por red. Para que multiples PCs accedan:

1. **Servidor**: Instalar PostgreSQL y la app en el servidor
2. **Clientes**: Solo instalar la app en cada PC cliente
3. **Configurar .env** en cada cliente apuntando a la IP del servidor:
   ```
   DB_HOST=192.168.1.100  # IP del servidor
   DB_PORT=5432
   DB_NAME=agilize_gestion
   DB_USER=postgres
   DB_PASSWORD=tu_password
   ```
4. **PostgreSQL**: Configurar `pg_hba.conf` para aceptar conexiones remotas:
   ```
   host all all 192.168.1.0/24 md5
   ```
5. **PostgreSQL**: En `postgresql.conf` cambiar:
   ```
   listen_addresses = '*'
   ```

## Actualizaciones

La app se actualiza desde el repositorio Git:
- Configuracion > Actualizar > Verificar Actualizaciones

## Credenciales por defecto

- Usuario: `master`
- Password: `master2025`

## Estructura

Ver `docs/PLAN_DE_ACCION.md` para el plan completo del proyecto.
