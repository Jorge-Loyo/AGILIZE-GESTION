@echo off
REM ============================================================
REM Exportar tablas DBISAM a CSV para sincronizacion con Agilize
REM Ejecutar cada 10 minutos via Tarea Programada
REM ============================================================

set DESTINO=C:\export_erp
set TIMESTAMP=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%

REM Crear directorio si no existe
if not exist "%DESTINO%" mkdir "%DESTINO%"

REM ============================================================
REM OPCION 1: Si el ERP tiene herramienta CLI de exportacion
REM Descomentar y ajustar segun el ERP:
REM
REM "C:\Program Files\ERP\dbexport.exe" -table SInventario -format csv -output "%DESTINO%\sinventario.csv"
REM "C:\Program Files\ERP\dbexport.exe" -table a2InvCostosPrecio -format csv -output "%DESTINO%\costos_precios.csv"
REM "C:\Program Files\ERP\dbexport.exe" -table SInvDep -format csv -output "%DESTINO%\existencia_deposito.csv"
REM "C:\Program Files\ERP\dbexport.exe" -table SCategorias -format csv -output "%DESTINO%\categorias.csv"
REM ============================================================

REM ============================================================
REM OPCION 2: Si el ERP tiene ODBC configurado
REM Usar bcp o sqlcmd con ODBC
REM
REM bcp "SELECT * FROM SInventario" queryout "%DESTINO%\sinventario.csv" -c -t";" -S "DBISAM_DSN"
REM ============================================================

REM ============================================================
REM OPCION 3: Copiar archivos .dat de DBISAM directamente
REM (requiere que el script Python los parsee - opcion avanzada)
REM
REM copy "D:\ERP\Data\SInventario.dat" "%DESTINO%\SInventario.dat"
REM ============================================================

REM Escribir timestamp de ultima ejecucion
echo %date% %time% > "%DESTINO%\ultima_sync.txt"

echo Exportacion completada: %date% %time%
