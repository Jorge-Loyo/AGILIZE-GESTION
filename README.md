# Agilize Gestión

<p align="center">
  <img src="assets/logos/agilize_dev.jpg" width="120" alt="Agilize Logo">
</p>

<p align="center">
  <strong>Sistema empresarial de gestión integral de RRHH, Nómina y Asistencia</strong><br>
  Desarrollado en Python | Desktop multiplataforma | PostgreSQL
</p>

<p align="center">
  <a href="https://github.com/Jorge-Loyo/AGILIZE-GESTION/releases/latest">⬇️ Descargar última versión</a> •
  <a href="#instalacion">Instalación</a> •
  <a href="#uso">Guía de Uso</a> •
  <a href="#red-local">Red Local</a>
</p>

---

## Características

- **Gestión de Empleados**: CRUD completo, legajo, importación/exportación Excel
- **Control de Asistencia**: Importación de fichadas (reloj XLS/XLSX), registro manual, calendario visual
- **Liquidación de Sueldos**: Cálculo automático desde asistencia real, conceptos configurables
- **Adelantos**: Con cuotas, descuento automático en liquidación
- **SAC (Aguinaldo)**: Cálculo por método legal o promedio
- **Cierres Quincenales**: Rango de fechas flexible, validación de incompletos
- **Recibo de Sueldo PDF**: Detalle completo de horas, multiplicadores, conceptos
- **Sucursales**: Múltiples ubicaciones por empresa
- **Usuarios y Roles**: Control de acceso con auditoría
- **Tema Oscuro/Claro**: Paleta de marca personalizable
- **Actualizaciones Automáticas**: Desde repositorio Git

---

## Descarga

### Última versión estable

👉 **[Descargar desde GitHub Releases](https://github.com/Jorge-Loyo/AGILIZE-GESTION/releases/latest)**

Descargar el archivo `AgilizeGestion-vX.X.X-windows.zip`, descomprimir y ejecutar `Instalador.exe`.

---

## Requisitos

| Componente | Servidor | Cliente |
|-----------|----------|---------|
| Sistema Operativo | Windows 10+ / Linux | Windows 10+ |
| PostgreSQL | Incluido (portable) o instalado | No necesita |
| Python | No necesita (compilado) | No necesita |
| Red | LAN | Acceso al servidor |

---

## Instalación

### Opción 1: Instalador gráfico (recomendado)

1. Descargar el ZIP desde [Releases](https://github.com/Jorge-Loyo/AGILIZE-GESTION/releases/latest)
2. Descomprimir en cualquier carpeta
3. Ejecutar `Instalador.exe`
4. Seleccionar tipo:
   - **Servidor**: Instala la app + descarga PostgreSQL automáticamente
   - **Cliente**: Solo la app, conecta al servidor por red
5. Completar datos de conexión
6. Listo — acceso directo en el escritorio

### Opción 2: Desde código fuente (desarrolladores)

```bash
git clone https://github.com/Jorge-Loyo/AGILIZE-GESTION.git
cd AGILIZE-GESTION
py -m venv venv
venv\Scripts\pip install -r requirements.txt

# Configurar .env
copy .env.example .env
# Editar .env con datos de PostgreSQL

# Crear BD y migrar
# CREATE DATABASE agilize_gestion;
venv\Scripts\alembic upgrade head
venv\Scripts\python -m scripts.seed

# Ejecutar
venv\Scripts\python main.py
```

---

## Credenciales por defecto

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `master` | `master2025` | Administrador |

---

## Uso

### Paso 1: Cargar Empleados

1. Ir a **RRHH > Empleados**
2. Usar **Importar** para cargar desde Excel, o **+ Nuevo** para agregar manualmente
3. Configurar: valor hora, valor hora extra, jornada, días laborales, sucursal
4. Descargar **Plantilla** para ver el formato de importación

### Paso 2: Registrar Asistencia

1. Ir a **RRHH > Asistencia**
2. Usar **Importar Fichadas** para cargar el archivo del reloj (XLS) o planilla manual (XLSX)
3. Revisar registros **Incompletos** (filtro Estado) y completarlos
4. Usar **Calendario** para ver visualmente la asistencia de cada empleado

### Paso 3: Cerrar Quincena

1. Ir a **RRHH > Cierres**
2. Seleccionar rango de fechas (ej: 01/05 al 15/05)
3. Presionar **Cerrar Quincena**
4. Si hay incompletos, no permite cerrar hasta completarlos

### Paso 4: Liquidar Sueldos

1. Ir a **RRHH > Nómina > Liquidaciones**
2. Presionar **+ Liquidar**
3. Seleccionar período cerrado y empleado
4. El sistema calcula automáticamente desde la asistencia:
   - Horas normales × valor hora
   - Horas extra × valor hora extra × multiplicador
   - Sábados, domingos, feriados con sus multiplicadores
5. Seleccionar conceptos adicionales (viáticos, presentismo, deducciones)
6. Ver detalle en tiempo real y confirmar

### Paso 5: Imprimir Recibo

1. En la lista de liquidaciones, seleccionar una
2. Presionar **Imprimir Recibo**
3. Se genera PDF con detalle completo

---

## Configuración

### Conceptos de Nómina (RRHH > Configuración)

| Tipo de Cálculo | Descripción | Ejemplo |
|----------------|-------------|---------|
| Porcentaje sobre bruto | Se aplica % al bruto | Jubilación 11% |
| Monto fijo | Valor fijo por liquidación | Premio $70.000 |
| Monto por día trabajado | Monto × días del período | Viáticos $1.000/día |

### Multiplicadores de Hora Extra

| Concepto | Default | Significado |
|----------|---------|-------------|
| Hora Extra | 1.50x | 50% más sobre valor hora |
| Hora Sábado | 1.50x | 50% más |
| Hora Domingo | 2.00x | 100% más |
| Hora Feriado | 2.00x | 100% más |

---

## Red Local

Para que múltiples PCs accedan a la misma base de datos:

### En el Servidor:
1. Instalar la app como "Servidor"
2. PostgreSQL escucha en todas las interfaces automáticamente

### En cada Cliente:
1. Instalar la app como "Cliente"
2. En la configuración poner la IP del servidor:
   ```
   DB_HOST=192.168.1.100
   DB_PORT=5432
   DB_NAME=agilize_gestion
   DB_USER=postgres
   DB_PASSWORD=agilize2025
   ```

### Verificar conectividad:
- El servidor debe tener el puerto 5432 abierto en el firewall
- Los clientes deben estar en la misma red

---

## Actualizaciones

Desde la app: **Configuración > Actualizar**

1. Presionar "Verificar Actualizaciones"
2. Si hay cambios disponibles, presionar "Actualizar Ahora"
3. Reiniciar la aplicación

---

## Estructura del Proyecto

```
agilize_gestion/
├── main.py                    # Entry point
├── core/                      # Motor: config, BD, auth, logging
├── models/                    # Modelos SQLAlchemy
├── services/                  # Lógica de negocio
├── ui/                        # Vistas generales, temas, componentes
├── modulos/
│   ├── empleados/views/       # RRHH: empleados, asistencia, cierres
│   ├── nomina/views/          # Liquidaciones, adelantos, SAC
│   └── admin/views/           # Configuración global, usuarios
├── alembic/                   # Migraciones de BD
├── assets/logos/              # Logos
├── scripts/                   # Build, instalador, seeds
└── docs/                      # Documentación
```

---

## Tecnologías

- **Python 3.11+** con PySide6
- **PostgreSQL 16+** (portable incluido)
- **SQLAlchemy 2.0** + Alembic
- **ReportLab** (PDF) + **OpenPyXL** (Excel)
- **QtAwesome** (iconos Font Awesome)
- **PyInstaller** (compilación)

---

## Licencia

Uso privado — Agilize Soluciones.

---

## Contacto

Desarrollado por **Agilize Soluciones**  
📧 Configurar en: Configuración > Desarrollador
