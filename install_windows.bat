@echo off
setlocal enabledelayedexpansion
echo ============================================
echo   Agilize Gestion - Instalador Windows
echo ============================================
echo.

:: Configuracion
set APP_NAME=AgilizeGestion
set INSTALL_DIR=%LOCALAPPDATA%\%APP_NAME%
set DB_NAME=agilize_gestion
set DB_USER=postgres
set DB_PORT=5432
set DB_HOST=localhost

:: Pedir password de PostgreSQL
echo Ingresa la contrasena de PostgreSQL (usuario postgres):
set /p DB_PASSWORD="> "
echo.

:: Verificar Python
set PYTHON=
where py >nul 2>&1
if %errorlevel% equ 0 (set PYTHON=py& goto :python_ok)
where python >nul 2>&1
if %errorlevel% equ 0 (set PYTHON=python& goto :python_ok)
echo [ERROR] Python no encontrado. Instala Python 3.11+ desde python.org
pause
exit /b 1
:python_ok
echo [OK] Python: %PYTHON%

:: Verificar PostgreSQL
set PSQL=
if exist "C:\Program Files\PostgreSQL\18\bin\psql.exe" (
    set "PSQL=C:\Program Files\PostgreSQL\18\bin\psql.exe"
    goto :pg_ok
)
if exist "C:\Program Files\PostgreSQL\17\bin\psql.exe" (
    set "PSQL=C:\Program Files\PostgreSQL\17\bin\psql.exe"
    goto :pg_ok
)
if exist "C:\Program Files\PostgreSQL\16\bin\psql.exe" (
    set "PSQL=C:\Program Files\PostgreSQL\16\bin\psql.exe"
    goto :pg_ok
)
where psql >nul 2>&1
if %errorlevel% equ 0 (set PSQL=psql& goto :pg_ok)
echo [ERROR] PostgreSQL no encontrado. Instala PostgreSQL 16+ desde postgresql.org
pause
exit /b 1
:pg_ok
echo [OK] PostgreSQL encontrado

:: Crear directorio de instalacion
echo.
echo [1/7] Creando directorio de instalacion...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
robocopy . "%INSTALL_DIR%" /E /NFL /NDL /NJH /NJS /NC /NS /NP /XD venv .git __pycache__ logs exports recibos >nul 2>&1
echo [OK] Archivos copiados a %INSTALL_DIR%

:: Crear entorno virtual
echo [2/7] Creando entorno virtual...
cd /d "%INSTALL_DIR%"
%PYTHON% -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

:: Instalar dependencias
echo [3/7] Instalando dependencias (esto puede tardar)...
venv\Scripts\pip install --quiet -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

:: Configurar .env
echo [4/7] Configurando conexion a base de datos...
(
echo # Base de Datos
echo DB_HOST=%DB_HOST%
echo DB_PORT=%DB_PORT%
echo DB_NAME=%DB_NAME%
echo DB_USER=%DB_USER%
echo DB_PASSWORD=%DB_PASSWORD%
echo.
echo # Aplicacion
echo APP_NAME=Agilize Gestion
echo APP_VERSION=1.0.0
echo SESSION_TIMEOUT_MINUTES=30
echo.
echo # Seguridad
echo SECRET_KEY=agilize_%RANDOM%%RANDOM%
echo BCRYPT_ROUNDS=12
) > .env

:: Crear base de datos si no existe
echo [5/7] Verificando base de datos...
set PGPASSWORD=%DB_PASSWORD%
"%PSQL%" -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -tc "SELECT 1 FROM pg_database WHERE datname='%DB_NAME%'" | findstr "1" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Creando base de datos %DB_NAME%...
    "%PSQL%" -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -c "CREATE DATABASE %DB_NAME%;"
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear la base de datos. Verifica la contrasena.
        pause
        exit /b 1
    )
    echo [OK] Base de datos creada.
) else (
    echo [OK] Base de datos ya existe, se mantienen los datos.
)

:: Ejecutar migraciones
echo [6/7] Ejecutando migraciones...
venv\Scripts\alembic upgrade head
if %errorlevel% neq 0 (
    echo [ERROR] Error en migraciones.
    pause
    exit /b 1
)

:: Seed solo si no hay usuarios
echo [7/7] Verificando datos iniciales...
set PGPASSWORD=%DB_PASSWORD%
"%PSQL%" -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -tc "SELECT COUNT(*) FROM usuarios" | findstr "0" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Creando usuario inicial...
    venv\Scripts\python -m scripts.seed
) else (
    echo [OK] Ya existen usuarios, no se sobreescriben.
)

:: Crear acceso directo en escritorio
echo.
echo Creando acceso directo en escritorio...
set SHORTCUT=%USERPROFILE%\Desktop\Agilize Gestion.lnk
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%INSTALL_DIR%\venv\Scripts\pythonw.exe'; $s.Arguments = 'main.py'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Save()" >nul 2>&1
if exist "%SHORTCUT%" (
    echo [OK] Acceso directo creado en el escritorio.
) else (
    echo [INFO] No se pudo crear el acceso directo. Ejecuta manualmente.
)

echo.
echo ============================================
echo   Instalacion completada exitosamente!
echo ============================================
echo.
echo   Ubicacion: %INSTALL_DIR%
echo   Usuario: master
echo   Contrasena: master2025
echo.
echo   Ejecuta desde el acceso directo en el escritorio.
echo.
pause
