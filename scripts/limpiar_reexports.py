"""
Paso 1: Actualizar todos los imports de services.X_service -> services.CARPETA.X_service
Paso 2: Borrar los re-exports de la raiz
"""
import os
import re

BASE = r"c:\Desarrollo\Agilize-Gestion"

# Mapeo: modulo viejo -> modulo nuevo
MAPA = {
    "services.auth_service": "services.core.auth_service",
    "services.audit_service": "services.core.audit_service",
    "services.empresa_service": "services.core.empresa_service",
    "services.dashboard_service": "services.core.dashboard_service",
    "services.backup_service": "services.core.backup_service",
    "services.update_service": "services.core.update_service",
    "services.reset_service": "services.core.reset_service",
    "services.logo_service": "services.core.logo_service",
    "services.empleado_service": "services.rrhh.empleado_service",
    "services.asistencia_service": "services.rrhh.asistencia_service",
    "services.calculo_asistencia_service": "services.rrhh.calculo_asistencia_service",
    "services.import_fichadas_service": "services.rrhh.import_fichadas_service",
    "services.nomina_service": "services.rrhh.nomina_service",
    "services.config_nomina_service": "services.rrhh.config_nomina_service",
    "services.liquidacion_pendiente_service": "services.rrhh.liquidacion_pendiente_service",
    "services.recibo_pdf_service": "services.rrhh.recibo_pdf_service",
    "services.sac_service": "services.rrhh.sac_service",
    "services.vacaciones_service": "services.rrhh.vacaciones_service",
    "services.permiso_ausencia_service": "services.rrhh.permiso_ausencia_service",
    "services.aprobacion_extras_service": "services.rrhh.aprobacion_extras_service",
    "services.adelanto_service": "services.rrhh.adelanto_service",
    "services.cierre_service": "services.rrhh.cierre_service",
    "services.periodo_service": "services.rrhh.periodo_service",
    "services.formulario_alta_service": "services.rrhh.formulario_alta_service",
    "services.compras_service": "services.compras.compras_service",
    "services.ventas_service": "services.ventas.ventas_service",
    "services.reportes_venta_service": "services.ventas.reportes_venta_service",
    "services.riesgo_venta_service": "services.ventas.riesgo_venta_service",
    "services.finanzas_service": "services.finanzas.finanzas_service",
    "services.cuentas_service": "services.finanzas.cuentas_service",
    "services.estado_cuenta_service": "services.finanzas.estado_cuenta_service",
    "services.etiquetas_service": "services.herramientas.etiquetas_service",
    "services.limpiador_service": "services.herramientas.limpiador_service",
    "services.cotizacion_service": "services.herramientas.cotizacion_service",
    "services.export_service": "services.herramientas.export_service",
    "services.import_service": "services.herramientas.import_service",
    "services.reportes_service": "services.herramientas.reportes_service",
    "services.datos_service": "services.datos.datos_service",
    "services.admin_service": "services.datos.admin_service",
    "services.facturador_config_service": "services.datos.facturador_config_service",
}

# NO tocar estos (ya son paquetes con fachada propia)
NO_TOCAR = {
    "services.inventario_service",
    "services.cliente_service",
    "services.precios_venta_service",
}


def actualizar_imports():
    """Paso 1: Reemplazar imports en todos los .py del proyecto."""
    archivos_modificados = 0
    lineas_cambiadas = 0

    for root, dirs, files in os.walk(BASE):
        if '__pycache__' in root or 'venv' in root or '.git' in root:
            continue
        for f in files:
            if not f.endswith('.py'):
                continue
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                contenido = fh.read()

            nuevo = contenido
            for viejo, nuevo_mod in MAPA.items():
                # Reemplazar "from services.X_service" -> "from services.CARPETA.X_service"
                # Pero NO reemplazar dentro de los propios archivos de la carpeta destino
                if f"from {viejo}" in nuevo:
                    # No reemplazar en el re-export ni en el archivo destino mismo
                    if path.endswith(os.path.join("services", viejo.split(".")[-1] + ".py")):
                        continue
                    nuevo = nuevo.replace(f"from {viejo}", f"from {nuevo_mod}")

            if nuevo != contenido:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(nuevo)
                cambios = sum(1 for a, b in zip(contenido.splitlines(), nuevo.splitlines()) if a != b)
                archivos_modificados += 1
                lineas_cambiadas += cambios
                print(f"  {os.path.relpath(path, BASE)} ({cambios} cambios)")

    print(f"\n{archivos_modificados} archivos modificados, {lineas_cambiadas} lineas cambiadas")
    return archivos_modificados


def borrar_reexports():
    """Paso 2: Borrar los archivos re-export de la raiz."""
    borrados = 0
    raiz = os.path.join(BASE, "services")
    for viejo in MAPA:
        archivo = viejo.split(".")[-1] + ".py"
        path = os.path.join(raiz, archivo)
        if os.path.exists(path):
            os.remove(path)
            borrados += 1
            print(f"  DEL {archivo}")
    print(f"\n{borrados} re-exports borrados")


if __name__ == "__main__":
    print("=" * 60)
    print("PASO 1: Actualizar imports")
    print("=" * 60)
    actualizar_imports()

    print("\n" + "=" * 60)
    print("PASO 2: Borrar re-exports de raiz")
    print("=" * 60)
    borrar_reexports()

    print("\n" + "=" * 60)
    print("LISTO - Ejecutar tests para verificar")
    print("=" * 60)
