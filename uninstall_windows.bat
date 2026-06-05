@echo off
echo ============================================
echo   Agilize Gestion - Desinstalador Windows
echo ============================================
echo.

set APP_NAME=AgilizeGestion
set INSTALL_DIR=%LOCALAPPDATA%\%APP_NAME%

echo ATENCION: Esto eliminara la aplicacion pero NO la base de datos.
echo Los datos se mantienen para una futura reinstalacion.
echo.
echo Directorio: %INSTALL_DIR%
echo.

set /p CONFIRMAR="Deseas continuar? (S/N): "
if /i not "%CONFIRMAR%"=="S" (
    echo Cancelado.
    pause
    exit /b 0
)

echo.
echo [1/3] Eliminando acceso directo...
del "%USERPROFILE%\Desktop\Agilize Gestion.lnk" >nul 2>&1
echo [OK]

echo [2/3] Eliminando archivos de la aplicacion...
if exist "%INSTALL_DIR%" (
    rmdir /S /Q "%INSTALL_DIR%"
    echo [OK] Directorio eliminado.
) else (
    echo [INFO] No se encontro el directorio de instalacion.
)

echo [3/3] Limpieza completada.
echo.
echo ============================================
echo   Desinstalacion completada
echo ============================================
echo.
echo   La base de datos NO fue eliminada.
echo   Si reinstala la aplicacion, los datos
echo   se mantendran automaticamente.
echo.
echo   Para eliminar la BD manualmente:
echo   DROP DATABASE agilize_gestion;
echo.
pause
