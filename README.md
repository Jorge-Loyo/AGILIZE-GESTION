# Agilize Gestión

<p align="center">
  <img src="assets/logos/app_icon.ico" width="120" alt="Agilize Logo">
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

### RRHH
- **Gestión de Empleados**: CRUD completo, legajo, importación/exportación Excel, formulario de alta PDF
- **Dos tipos de liquidación**: Por hora (fichado) y Mensual (sin fichado, solo descuento faltas)
- **Control de Asistencia**: Importación de fichadas (reloj XLS/XLSX con mapeo visual), registro manual, calendario
- **Vacaciones**: Cálculo automático por antigüedad (Ley 20.744), solicitud/aprobación
- **Novedades Mensuales**: Faltas, horas extra y feriados trabajados para empleados mensuales
- **Aprobación de Horas Extra**: Workflow de aprobación antes de liquidar
- **Cierres**: Mensual, quincenal, semanal o diario según configuración
- **Liquidación de Sueldos**: Cálculo automático, conceptos configurables, feriados no trabajados
- **Adelantos**: Con cuotas, fecha y período, descuento automático en liquidación
- **SAC (Aguinaldo)**: Cálculo por método legal o promedio
- **Recibo de Sueldo PDF**: Detalle completo de horas, multiplicadores, conceptos
- **Resumen Mensual/Quincenal**: Comparación Q1 vs Q2, vista por período
- **Dashboard dinámico**: Indicadores por período + métricas globales + notificaciones
- **Búsqueda Global**: Ctrl+K desde cualquier pantalla
- **Histórico de Sueldo**: Auditoría de cambios en valor hora/sueldo
- **Manual de Uso**: Integrado en la app por módulo

### Configuración
- **Período de Pago**: Mensual / Quincenal / Semanal / Diario
- **Jornada por Defecto**: Horario de entrada/salida configurable
- **Multiplicadores**: Hora extra, sábado, domingo, feriado trabajado, feriado no trabajado
- **Conceptos de Nómina**: Porcentaje, monto fijo, monto por día
- **Feriados**: ABM por año
- **Roles y Permisos**: Matriz de permisos por módulo/acción
- **Usuarios**: Gestión de accesos
- **Sucursales**: Múltiples ubicaciones
- **Datos de Empresa**: Información legal para recibos
- **Visual**: Logo y nombre personalizable
- **Auditoría**: Log de todas las acciones
- **Actualizaciones**: Desde repositorio Git
- **Tema Oscuro/Claro**: Paleta de marca (#D4AF37 gold)

---

## Descarga

👉 **[Descargar desde GitHub Releases](https://github.com/Jorge-Loyo/AGILIZE-GESTION/releases/latest)**

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

### Instalador gráfico (recomendado)

1. Descargar ZIP desde Releases
2. Descomprimir → Ejecutar `Instalador.exe`
3. Seleccionar **Servidor** o **Cliente**
4. Completar datos de conexión → Listo

### Desde código fuente

```bash
git clone https://github.com/Jorge-Loyo/AGILIZE-GESTION.git
cd AGILIZE-GESTION
py -m venv venv
venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# Editar .env con datos de PostgreSQL
venv\Scripts\alembic upgrade head
venv\Scripts\python -m scripts.seed
venv\Scripts\python main.py
```

---

## Credenciales por defecto

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `master` | `master2025` | Administrador |

---

## Uso

### Empleados
1. **RRHH > Empleados > + Nuevo** o **Importar** desde Excel
2. Configurar: tipo liquidación (hora/mensual), valor hora, jornada, días laborales
3. **Formulario Alta**: genera PDF en blanco para que complete el empleado
4. **Plantilla**: descarga Excel con formato para importación masiva
5. **Exportar**: genera Excel con activos e inactivos en hojas separadas

### Asistencia
1. **Importar Fichadas**: XLS (reloj por legajo) o XLSX (manual con mapeo visual)
2. **Registro Manual**: agregar fichadas individuales
3. **Vacaciones**: solicitar, aprobar, tomar (cálculo por antigüedad)
4. **Novedades Mensuales**: faltas y horas extra para empleados sin fichado

### Liquidación
1. **RRHH > Nómina > + Liquidar**
2. Seleccionar período y empleado ([H] hora / [M] mensual)
3. Checkbox de **feriados no trabajados** para incluir pago (x1 configurable)
4. Seleccionar conceptos → ver detalle en tiempo real → Confirmar
5. **Imprimir Recibo** genera PDF completo

### Configuración
1. **Período de Pago**: elegir frecuencia de liquidación
2. **Multiplicadores**: configurar valores de hora extra, feriados, etc.
3. **Roles**: crear roles y asignar permisos por módulo

---

## Estructura del Proyecto

```
agilize_gestion/
├── main.py                         # Entry point
├── core/                           # Config, BD, auth, logging
├── models/                         # Modelos SQLAlchemy (19 modelos)
├── services/                       # Lógica de negocio (24 servicios)
├── ui/                             # Vistas generales, temas, búsqueda global
├── modulos/
│   ├── rrhh/views/                 # RRHH: empleados, asistencia, nómina, cierres
│   └── configuracion/views/        # Config: empresa, roles, usuarios, auditoría
├── alembic/                        # Migraciones de BD
├── assets/logos/                   # Logos e ícono de la app
├── tests/                          # Tests automatizados (pytest)
├── scripts/                        # Build, instalador, seeds
└── docs/                           # Documentación y testing
```

---

## Tecnologías

- **Python 3.11+** con PySide6
- **PostgreSQL 16+** (portable incluido)
- **SQLAlchemy 2.0** + Alembic
- **ReportLab** (PDF) + **OpenPyXL** (Excel)
- **QtAwesome** (iconos Font Awesome)
- **PyInstaller** (compilación)
- **Pytest** (testing)

---

## Licencia

Uso privado — Agilize Soluciones.

---

## Contacto

Desarrollado por **Agilize Soluciones**  
📧 Configurar en: Configuración > Desarrollador
