"""Reorganizar services/ en carpetas por modulo con re-exports automaticos."""
import os
import shutil

BASE = r"c:\Desarrollo\Agilize-Gestion\services"

# Mapeo: archivo -> carpeta destino
MAPA = {
    # CORE
    "auth_service.py": "core",
    "audit_service.py": "core",
    "empresa_service.py": "core",
    "dashboard_service.py": "core",
    "backup_service.py": "core",
    "update_service.py": "core",
    "reset_service.py": "core",
    "logo_service.py": "core",
    # RRHH
    "empleado_service.py": "rrhh",
    "asistencia_service.py": "rrhh",
    "calculo_asistencia_service.py": "rrhh",
    "import_fichadas_service.py": "rrhh",
    "nomina_service.py": "rrhh",
    "config_nomina_service.py": "rrhh",
    "liquidacion_pendiente_service.py": "rrhh",
    "recibo_pdf_service.py": "rrhh",
    "sac_service.py": "rrhh",
    "vacaciones_service.py": "rrhh",
    "permiso_ausencia_service.py": "rrhh",
    "aprobacion_extras_service.py": "rrhh",
    "adelanto_service.py": "rrhh",
    "cierre_service.py": "rrhh",
    "periodo_service.py": "rrhh",
    "formulario_alta_service.py": "rrhh",
    # COMPRAS
    "compras_service.py": "compras",
    # VENTAS
    "ventas_service.py": "ventas",
    "reportes_venta_service.py": "ventas",
    "riesgo_venta_service.py": "ventas",
    # FINANZAS
    "finanzas_service.py": "finanzas",
    "cuentas_service.py": "finanzas",
    "estado_cuenta_service.py": "finanzas",
    # HERRAMIENTAS
    "etiquetas_service.py": "herramientas",
    "limpiador_service.py": "herramientas",
    "cotizacion_service.py": "herramientas",
    "export_service.py": "herramientas",
    "import_service.py": "herramientas",
    # DATOS
    "datos_service.py": "datos",
    "admin_service.py": "datos",
    "facturador_config_service.py": "datos",
    # RE-EXPORTS (no mover)
    "inventario_service.py": None,
    "cliente_service.py": None,
    "precios_venta_service.py": None,
    "reportes_service.py": "herramientas",
}

movidos = 0
for archivo, carpeta in MAPA.items():
    if carpeta is None:
        continue
    origen = os.path.join(BASE, archivo)
    if not os.path.exists(origen):
        print(f"  SKIP {archivo} (no existe)")
        continue
    destino_dir = os.path.join(BASE, carpeta)
    os.makedirs(destino_dir, exist_ok=True)
    destino = os.path.join(destino_dir, archivo)
    # Copiar a carpeta
    shutil.copy2(origen, destino)
    # Reemplazar original con re-export
    modulo = archivo.replace(".py", "")
    with open(origen, "w", encoding="utf-8") as f:
        f.write(f'"""Re-export: services.{carpeta}.{modulo}"""\n')
        f.write(f'from services.{carpeta}.{modulo} import *  # noqa: F401,F403\n')
    # Crear __init__.py en carpeta si no existe
    init_path = os.path.join(destino_dir, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(f'"""Paquete services.{carpeta}"""\n')
    movidos += 1
    print(f"  OK {archivo} -> {carpeta}/")

print(f"\n{movidos} servicios organizados.")
