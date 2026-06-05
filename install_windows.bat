@echo off
echo ============================================
echo   Agilize Gestion - Instalador Windows
echo ============================================
echo.

:: Verificar Python con diferentes comandos
set PYTHON=
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=py
    goto :found
)
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python
    goto :found
)
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python3
    goto :found
)

echo [ERROR] Python no encontrado. Instala Python 3.11+ desde python.org
pause
exit /b 1

:found
echo [OK] Python encontrado: %PYTHON%
%PYTHON% --version
echo.

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
echo.
echo ============================================
echo   Instalacion completada!
echo ============================================
echo.
echo Pasos siguientes:
echo   1. Edita .env con tus datos de PostgreSQL
echo   2. Crea la BD: CREATE DATABASE agilize_gestion;
echo   3. Ejecuta: venv\Scripts\alembic upgrade head
echo   4. Ejecuta: venv\Scripts\python -m scripts.seed
echo.
echo Para ejecutar: venv\Scripts\python main.py
echo Para generar .exe: venv\Scripts\python scripts\build.py
echo.
pause
