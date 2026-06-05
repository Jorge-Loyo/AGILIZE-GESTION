# Plan de Acción — Agilize Gestión

## Sistema Empresarial de Gestión Integral

**Versión:** 1.0  
**Fecha de inicio:** Junio 2025  
**País/Legislación:** Argentina  
**Usuarios iniciales:** 5 (escalable a 10+ en el próximo año)

---

## 1. Visión del Producto

Sistema de escritorio modular para gestión empresarial, comenzando por Empleados y Nómina, con arquitectura preparada para incorporar módulos futuros (Inventario, Facturación, Contabilidad, etc.) sin refactorización mayor.

---

## 2. Stack Tecnológico

| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| UI Desktop | PySide6 | LGPL, profesional, soporte QSS para theming |
| Theming | qt-material + QSS custom | Tema oscuro/claro moderno, no genérico |
| Base de Datos | PostgreSQL 18 | Concurrencia, robustez, escalabilidad |
| ORM | SQLAlchemy 2.0 | Mapeo de modelos, independencia de BD |
| Migraciones | Alembic | Versionado de esquema de BD |
| Hash/Seguridad | bcrypt | Hash de contraseñas seguro |
| Configuración | python-dotenv | Variables de entorno sin hardcodeo |
| Logging | logging (stdlib) | Trazabilidad de operaciones |
| Reportes (futuro) | reportlab / openpyxl | PDF y Excel |

---

## 3. Arquitectura

```
Patrón: MVC + Servicios + RBAC Granular

UI (Views/PySide6)
    ↕ señales/slots
Controllers (por módulo)
    ↕
Services (lógica de negocio pura)
    ↕
Models (SQLAlchemy) → PostgreSQL
```

### Principios:
- **Modularidad**: Cada módulo es independiente (carpeta propia con controller + views).
- **Separación de responsabilidades**: La UI nunca accede directo a la BD.
- **RBAC granular**: Permisos por perfil Y por usuario individual (override).
- **Auditoría**: Todo cambio queda registrado (quién, qué, cuándo).

---

## 4. Sistema de Permisos (RBAC + Override por Usuario)

```
┌─────────┐     ┌──────────┐     ┌──────────────┐
│ Usuario │────→│   Rol    │────→│ Rol_Permiso  │
└─────────┘     └──────────┘     └──────────────┘
     │                                    │
     │          ┌──────────────────┐      │
     └─────────→│ Usuario_Permiso  │      │
                │ (override)       │      │
                └──────────────────┘      │
                                          ↓
                                   ┌──────────┐
                                   │ Permiso  │
                                   │ (módulo + │
                                   │  acción)  │
                                   └──────────┘
```

**Acciones por módulo:** `ver`, `crear`, `editar`, `eliminar`, `exportar`

**Lógica de resolución:**
1. Se consultan permisos del ROL del usuario.
2. Se consultan overrides del USUARIO (pueden agregar o quitar permisos).
3. El override del usuario siempre gana sobre el rol.

---

## 5. Diseño de Base de Datos (Fase 1)

### Tablas Core:

| Tabla | Descripción |
|-------|-------------|
| `usuarios` | Credenciales, estado activo/inactivo, FK a rol |
| `roles` | Nombre, descripción |
| `modulos` | Registro de módulos del sistema |
| `permisos` | Módulo + acción (ej: "empleados.crear") |
| `rol_permisos` | Qué permisos tiene cada rol |
| `usuario_permisos` | Override: permisos extra o denegados por usuario |
| `audit_log` | Usuario, acción, tabla afectada, timestamp, detalle |
| `empresa_config` | Datos de la empresa, configuraciones globales |

### Tablas Módulo Empleados:

| Tabla | Descripción |
|-------|-------------|
| `empleados` | Datos personales, laborales, estado |
| `departamentos` | Áreas de la empresa |
| `cargos` | Puestos de trabajo |
| `documentos_empleado` | Archivos adjuntos (contratos, etc.) |

### Tablas Módulo Nómina (Fase posterior):

| Tabla | Descripción |
|-------|-------------|
| `conceptos_nomina` | Haberes y deducciones configurables |
| `liquidaciones` | Cabecera del recibo |
| `liquidacion_detalle` | Líneas del recibo |
| `periodos_liquidacion` | Meses cerrados |

---

## 6. Interfaz Visual

- **Tema dual**: Oscuro y Claro, switcheable desde configuración.
- **Librería de estilo**: `qt-material` como base + QSS personalizado.
- **Sidebar dinámica**: Se genera según permisos del usuario logueado.
- **Componentes reutilizables**: Tablas con búsqueda/filtro, formularios con validación visual, notificaciones toast.
- **Paleta de colores** (tema oscuro): Fondo #1e1e2e, Acento #7c3aed (violeta), Éxito #10b981, Error #ef4444.

---

## 7. Hitos de Desarrollo

### Hito 0 — Cimientos ✅ (Actual)
- [x] Estructura de carpetas
- [x] Configuración del entorno (requirements.txt, .env, .gitignore)
- [x] Conexión a PostgreSQL con SQLAlchemy
- [x] Configuración de Alembic
- [x] Documento de plan de acción

### Hito 1 — Modelos de BD Core
- [ ] Modelos: usuarios, roles, permisos, módulos, audit_log
- [ ] Migración inicial con Alembic
- [ ] Script seed: crear admin, roles base, permisos iniciales
- [ ] Tests de conexión y queries básicas

### Hito 2 — Autenticación y Login
- [ ] Servicio de autenticación (hash, verificación, sesión)
- [ ] Resolución de permisos (rol + override usuario)
- [ ] UI: Pantalla de Login (PySide6 + tema moderno)
- [ ] Validación funcional del login contra BD

### Hito 3 — Ventana Principal + Navegación Dinámica
- [ ] Main Window con sidebar generada por permisos
- [ ] Switch tema oscuro/claro
- [ ] Sistema de navegación entre módulos
- [ ] Componente reutilizable: DataTable
- [ ] Logging de acciones del usuario

### Hito 4 — Módulo Empleados
- [ ] CRUD completo de empleados
- [ ] Gestión de departamentos y cargos
- [ ] Búsqueda y filtros avanzados
- [ ] Validaciones (CUIL, formato datos)
- [ ] Auditoría de cambios

### Hito 5 — Módulo Nómina
- [ ] Configuración de conceptos (haberes/deducciones)
- [ ] Cálculo de liquidación según legislación Argentina
- [ ] Generación de recibos
- [ ] Historial de liquidaciones
- [ ] Exportación a PDF

### Hito 6 — Administración y Reportes
- [ ] ABM de usuarios y roles desde la UI
- [ ] Panel de asignación de permisos (visual)
- [ ] Reportes exportables (PDF/Excel)
- [ ] Dashboard con métricas básicas

---

## 8. Convenciones de Código

- **Idioma del código**: Inglés para nombres de variables/funciones, Español para strings de UI.
- **Formato**: PEP 8, máximo 100 caracteres por línea.
- **Commits**: Convencional (feat:, fix:, refactor:, docs:).
- **Docstrings**: En funciones públicas de servicios y controllers.

---

## 9. Seguridad

- Contraseñas hasheadas con bcrypt (nunca texto plano).
- Variables sensibles en .env (nunca en el código).
- Sesión con timeout configurable.
- Audit log de toda acción CRUD.
- Prepared statements via SQLAlchemy (prevención SQL injection).

---

## 10. Próximos Módulos (Roadmap Futuro)

| Prioridad | Módulo | Dependencia |
|-----------|--------|-------------|
| Alta | Inventario | - |
| Alta | Facturación (AFIP) | Empleados |
| Media | Contabilidad | Nómina, Facturación |
| Media | Proveedores | - |
| Baja | CRM / Clientes | Facturación |
| Baja | Reportes BI | Todos |

---

*Documento vivo — se actualizará a medida que avance el desarrollo.*
