# Guia de Desarrollo Local

Como correr Agilize Gestion desde el codigo fuente en tu PC de desarrollo.

## Requisitos

- **Python 3.11+** (recomendado 3.13)
- **PostgreSQL 14+** corriendo en localhost
- **Git**
- **Windows 10+**

## 1. Clonar el repositorio

```bash
git clone https://github.com/Jorge-Loyo/AGILIZE-GESTION.git
cd AGILIZE-GESTION
```

## 2. Crear entorno virtual

**Windows (cmd o PowerShell):**

```bash
py -m venv venv
venv\Scripts\activate
```

**Windows (Git Bash / MINGW64):**

```bash
py -m venv venv
source venv/Scripts/activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

# Usar servidor remoto

cp .env.server .env

# Usar local

cp .env.local .env

> **Nota:** En Windows el comando es `py` (no `python3`). Si `py` no funciona, usa la ruta completa: `C:\Users\TU_USUARIO\AppData\Local\Programs\Python\Python313\python.exe`

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
pip install qtawesome openpyxl reportlab Pillow
```

## 4. Configurar PostgreSQL

Asegurate de tener PostgreSQL corriendo. Luego crea la base de datos:

**Si tenes psql en PATH:**

```bash
psql -U postgres -c "CREATE DATABASE agilize_gestion;"
```

**Si NO tenes psql en PATH (Windows):**

```bash
"C:/Program Files/PostgreSQL/16/bin/psql.exe" -U postgres -c "CREATE DATABASE agilize_gestion;"
```

**Alternativa:** Crear desde pgAdmin o DBeaver la base de datos `agilize_gestion` con encoding UTF-8.

> **Nota:** Si no creas la BD manualmente, la app la necesita existente. El instalador (Setup.exe) la crea automaticamente, pero en desarrollo local necesitas crearla vos o usar el script: `py scripts/setup_postgres.py`

## 5. Configurar .env

Copiar el ejemplo y editar con tus datos:

**Windows:**

```bash
copy .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Editar `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agilize_gestion
DB_USER=postgres
DB_PASSWORD=tu_password_de_postgres

APP_NAME=Agilize Gestion
APP_VERSION=2.1.0
SESSION_TIMEOUT_MINUTES=30

SECRET_KEY=dev_key_local
BCRYPT_ROUNDS=12
```

## 6. Ejecutar migraciones

**Windows (cmd o PowerShell):**

```bash
venv\Scripts\alembic upgrade head
```

**Windows (Git Bash / MINGW64):**

```bash
venv/Scripts/alembic upgrade head
```

**Linux/macOS:**

```bash
venv/bin/alembic upgrade head
```

Si falla, la app creara las tablas automaticamente al iniciar.

## 7. Cargar datos iniciales (seed)

**Windows (cmd o PowerShell):**

```bash
venv\Scripts\python -m scripts.seed
```

**Windows (Git Bash / MINGW64):**

```bash
venv/Scripts/python -m scripts.seed
```

**Linux/macOS:**

```bash
venv/bin/python -m scripts.seed
```

Esto crea:

- Rol Administrador con todos los permisos
- Usuario `admin` / `admin123`

## 8. Ejecutar la aplicacion

**Windows (cmd o PowerShell):**

```bash
venv\Scripts\python main.py
```

**Windows (Git Bash / MINGW64):**

```bash
venv/Scripts/python main.py
```

**Linux/macOS:**

```bash
venv/bin/python main.py
```

La app se abre y podes loguearte con `admin` / `admin123`.

## Credenciales

| Usuario | Password   | Nota                                   |
| ------- | ---------- | -------------------------------------- |
| admin   | admin123   | Creado por seed                        |
| master  | master2025 | Creado por instalador (solo en builds) |

## Estructura del proyecto

```
├── main.py                 # Entry point
├── core/                   # Config, BD, auth, logging
├── models/                 # Modelos SQLAlchemy
├── services/               # Logica de negocio
├── ui/                     # Vistas generales, temas
├── modulos/
│   ├── rrhh/views/         # RRHH: empleados, asistencia, nomina
│   └── configuracion/views/ # Config: empresa, roles, usuarios
├── alembic/                # Migraciones de BD
├── scripts/                # Build, instalador, seeds
├── assets/                 # Logos e iconos
└── tests/                  # Tests (pytest)
```

## Comandos utiles

### Crear nueva migracion

**Windows (cmd):**

```bash
venv\Scripts\alembic revision --autogenerate -m "descripcion del cambio"
venv\Scripts\alembic upgrade head
```

**Windows (Git Bash):**

```bash
venv/Scripts/alembic revision --autogenerate -m "descripcion del cambio"
venv/Scripts/alembic upgrade head
```

**Linux/macOS:**

```bash
venv/bin/alembic revision --autogenerate -m "descripcion del cambio"
venv/bin/alembic upgrade head
```

### Correr tests

**Windows (cmd):**

```bash
venv\Scripts\pytest tests/ -v
```

**Windows (Git Bash):**

```bash
venv/Scripts/pytest tests/ -v
```

**Linux/macOS:**

```bash
venv/bin/pytest tests/ -v
```

### Compilar ejecutable (solo Windows)

```bash
venv\Scripts\pyinstaller AgilizeGestion.spec --noconfirm
```

El resultado queda en `dist/AgilizeGestion/`.

### Compilar instalador (solo Windows, Inno Setup 6)

Requiere Inno Setup 6 instalado y PostgreSQL portable en `dist/pgsql/`:

```bash
iscc scripts\inno\setup.iss
```

Genera `dist/Setup_AgilizeGestion_v2.1.0.exe`.

## Notas

- La app usa PySide6 (Qt6). Si tenes problemas con la UI, asegurate de tener los drivers de video actualizados.
- El `.env` NO se commitea. Esta en `.gitignore`.
- Los logs se guardan en `logs/` dentro del directorio de la app.
- Para desarrollo, el tema oscuro se activa por defecto. Podes cambiarlo desde Configuracion > Cambiar modo.
