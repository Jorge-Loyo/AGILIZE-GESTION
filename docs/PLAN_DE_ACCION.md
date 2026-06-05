# Plan de Acción — Agilize Gestión

## Sistema Empresarial de Gestión Integral

**Versión:** 1.2.0  
**Fecha de inicio:** Junio 2025  
**País/Legislación:** Argentina  
**Usuarios iniciales:** 5 (escalable a 10+)

---

## Estado del Proyecto: EN PRODUCCIÓN

---

## Módulos Implementados

### 1. RRHH (Recursos Humanos)

#### Dashboard
- Métricas en tiempo real: empleados activos, horas del mes, liquidaciones, adelantos, gasto nómina

#### Empleados
- CRUD completo con validaciones (DNI, CUIL, email, edad mínima 17)
- Legajo único por empleado
- Jornada configurable: hora entrada/salida, días laborales, valor hora, valor hora extra
- Sueldo mensual con cálculo automático bidireccional (hora↔mensual)
- Departamentos, Cargos y Sucursales
- Importación masiva desde Excel (flexible: soporta nombre completo, legajo numérico)
- Exportación a Excel
- Plantilla descargable
- Detalle en modal, ordenamiento por legajo/nombre/apellido
- Baja lógica (no elimina datos)

#### Asistencia
- Importación de fichadas desde XLS (reloj fichador) y XLSX (manual)
- Vinculación por legajo (No)
- Detección de registros incompletos (entrada sin salida) con alerta
- Registro manual con validación de duplicados por día
- Edición de registros en modal
- Eliminación de registros
- Normalización de hora de entrada al horario configurado
- Filtros: empleado, período, estado (todos/incompletos/completos), ordenamiento
- Contador de registros
- Vista Calendario por empleado (presente verde, ausente rojo, incompleto amarillo)
- Exportación a Excel
- Permisos / Licencias (tipos configurables, con/sin goce, días máx)
- Ausencias (justificadas/injustificadas)

#### Cierres
- Cierre por quincena con rango de fechas flexible (el usuario decide cuándo)
- Validación de solapamiento entre cierres
- No permite cerrar si hay registros incompletos
- Editar y eliminar cierres
- Reabrir con alerta si hay liquidaciones

#### Nómina
- **Liquidaciones**: Cálculo desde asistencia real (horas normales, extras, sábado, domingo, feriado)
- Valor hora extra independiente por empleado
- Multiplicadores configurables (extra, sábado, domingo, feriado)
- Conceptos de nómina: porcentaje sobre bruto, monto fijo, monto por día trabajado
- Edición de conceptos
- Descuento automático de adelantos (por cuotas)
- Combo de períodos cerrados para liquidar
- Empleados pendientes por período
- Verificar estado del período
- Detalle del recibo en tiempo real con desglose completo
- Recibo PDF profesional (datos empresa, empleado, asistencia, conceptos, totales, firmas)
- Filtros: año, mes, empleado
- Exportación a Excel
- **Resumen Mensual**: Vista consolidada con todos los empleados, días, horas, bruto, estado
- **Adelantos**: Con cuotas fraccionadas, info de horas trabajadas y saldo
- **SAC (Aguinaldo)**: Cálculo por método legal o promedio, acumulación automática

#### Configuración RRHH
- Valor hora extra (multiplicadores)
- Método SAC
- Conceptos de nómina (crear, editar, 3 tipos de cálculo)
- Tipos de permiso/licencia

### 2. Configuración (Global)

#### Datos de Empresa
- Razón social, CUIT, dirección, teléfono, actividad, convenio colectivo
- Sucursales (crear, listar)

#### Visual
- Nombre comercial (sobrenombre)
- Logo de la empresa

#### Desarrollador
- Datos del desarrollador (nombre, email, web, teléfono)
- Logo del desarrollador (icono de la app)
- Botón resetear aplicación (limpia datos operativos)

#### Usuarios
- CRUD de usuarios con roles
- Activar/desactivar
- Crear roles

#### Auditoría
- Log de acciones: login, crear, editar, eliminar, liquidar, cierres

#### Actualizar
- Conecta al repositorio Git (Deploy-Ferrelum)
- Verifica actualizaciones disponibles
- Descarga y aplica cambios

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| UI Desktop | PySide6 + QSS custom + qtawesome |
| Base de Datos | PostgreSQL 18 (portable incluido) |
| ORM | SQLAlchemy 2.0 |
| Migraciones | Alembic (auto-migración al iniciar) |
| Hash/Seguridad | bcrypt |
| Configuración | python-dotenv |
| Logging | loguru |
| Reportes | reportlab (PDF) + openpyxl (Excel) |
| Iconos | qtawesome (Font Awesome) |
| Build | PyInstaller |
| Distribución | GitHub Releases |

---

## Infraestructura

- Tema oscuro/claro con paleta de marca (dorado #D4AF37)
- Logo y nombre configurable desde BD
- Instalador gráfico (tkinter)
- PostgreSQL portable embebido
- Auto-migración de BD al iniciar
- Acceso directo en escritorio
- Soporte red local (servidor + clientes)
- Actualización desde repositorio Git

---

## Credenciales por defecto

- Usuario: `master`
- Password: `master2025`

---

## Repositorio

- URL: https://github.com/Jorge-Loyo/AGILIZE-GESTION.git
- Rama desarrollo: `main`
- Rama deploy: `Deploy-Ferrelum`

---

## Roadmap Futuro

| Prioridad | Módulo | Estado |
|-----------|--------|--------|
| Alta | Inventario | Pendiente |
| Alta | Facturación (AFIP) | Pendiente |
| Media | Contabilidad | Pendiente |
| Media | Proveedores | Pendiente |
| Baja | CRM / Clientes | Pendiente |
| Baja | Reportes BI | Pendiente |

---

*Documento actualizado: Junio 2026*
