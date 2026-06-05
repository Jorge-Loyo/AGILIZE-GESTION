@echo off
echo ============================================
echo   Agilize Gestion - Instalador Windows
echo ============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python no encontrado. Instala Python 3.11+ desde python.org
        pause
        exit /b 1
    )
    set PYTHON=py
) else (
    set PYTHON=python
)

echo [1/5] Creando entorno virtual...
%PYTHON% -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

echo [2/5] Instalando dependencias...
venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo [3/5] Instalando PyInstaller...
venv\Scripts\pip install pyinstaller

echo [4/5] Configuracion...
if not exist .env (
    copy .env.example .env
    echo [INFO] Archivo .env creado. Edita con tus datos de PostgreSQL.
)

echo [5/5] Verificando base de datos...
echo [INFO] Asegurate de tener PostgreSQL corriendo y la base de datos creada.
echo [INFO] Luego ejecuta: venv\Scripts\alembic upgrade head
echo [INFO] Y despues: venv\Scripts\python -m scripts.seed

echo.
echo ============================================
echo   Instalacion completada!
echo ============================================
echo.
echo Para ejecutar: venv\Scripts\python main.py
echo Para generar .exe: venv\Scripts\python scripts\build.py
echo.
pause
