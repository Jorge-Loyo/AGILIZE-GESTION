# Sincronización ERP Externo (DBISAM) → Agilize

## Para el Administrador del ERP Externo

### Requisitos
- Acceso a la base de datos DBISAM del ERP
- Permisos para crear tarea programada en Windows

### Paso 1: Crear carpeta compartida

```
1. Crear carpeta: C:\export_erp\
2. Click derecho → Propiedades → Compartir
3. Nombre compartido: export_erp
4. Permisos: Lectura para "Todos" o para el usuario de la VM Ubuntu
```

### Paso 2: Script de exportación

El ERP basado en DBISAM generalmente tiene una de estas opciones:

**Opción A: Si el ERP tiene exportación integrada**
- Buscar en menú: Herramientas → Exportar → CSV
- Configurar exportación automática de las tablas

**Opción B: Si tiene acceso SQL al DBISAM**
Usar el archivo `exportar_dbisam.bat` con DBISAM Command Line o la herramienta
de administración del ERP.

**Opción C: Si el ERP es A2 / Profit / Saint**
Muchos de estos ERPs tienen opción de "Exportar datos" en formato texto.
Configurar para que exporte las 4 tablas a C:\export_erp\

### Paso 3: Tarea programada

1. Abrir "Programador de tareas" de Windows
2. Crear tarea básica:
   - Nombre: "Exportar datos a Agilize"
   - Desencadenador: Repetir cada 10 minutos
   - Acción: Ejecutar `C:\export_erp\exportar.bat`

### Formato esperado de los CSV

Cada archivo debe tener headers en la primera fila, separador `;` o `,`.

**sinventario.csv:**
```
codigo;descripcion;unidad;categoria_id;activo
PROD001;Tornillo 1/4;UN;5;1
PROD002;Tuerca 1/4;UN;5;1
```

**costos_precios.csv:**
```
codigo;costo;precio1;precio2;precio3;precio4
PROD001;0.50;1.00;0.90;0.80;0.75
PROD002;0.30;0.60;0.55;0.50;0.45
```

**existencia_deposito.csv:**
```
codigo;deposito;existencia
PROD001;01;150
PROD001;02;30
PROD002;01;500
```

**categorias.csv:**
```
id;nombre;activo
1;Ferreteria;1
2;Electricidad;1
5;Tornilleria;1
```

### Notas
- Si los nombres de columna son diferentes, informar al equipo de Agilize
- El encoding debe ser UTF-8 o Latin-1 (se detecta automáticamente)
- Los archivos se sobreescriben cada vez (no acumulan)
