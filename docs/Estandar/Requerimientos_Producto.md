# Requerimientos de Producto — Agilize Gestion

## Modulos del sistema

| # | Modulo | Descripcion |
|---|--------|-------------|
| 1 | RRHH | Empleados, asistencia, nomina, vacaciones, SAC |
| 2 | Ventas | Clientes, presupuestos, pedidos, facturadores |
| 3 | Compras | Proveedores, ordenes de compra, orden sugerida |
| 4 | Facturador | POS con scanner/busqueda, cobro rapido |
| 5 | Inventario | Productos, depositos, movimientos, stock |
| 6 | Cuentas | Debe/haber clientes y proveedores, estado de cuenta |
| 7 | Finanzas | Contabilidad, facturacion, bancos, caja |
| 8 | Reportes | Dashboard BI, KPIs, top clientes, ventas por mes |
| 9 | Herramientas | Limpiador productos, cotizaciones, etiquetas |
| 10 | Conexiones | BD externas, APIs/JSON, e-commerce (proximamente) |
| 11 | Configuracion | Empresa, pais, visual, roles, usuarios, backup |

## Funcionalidades base obligatorias

### Login
- Pantalla con usuario + password
- Verificacion bcrypt contra BD
- Mensajes de error claros y copiables

### Dashboard
- Grid de modulos con iconos (2 filas)
- Solo muestra modulos con permiso
- Toggle tema oscuro/claro
- Boton cerrar sesion

### Roles y permisos
- Roles: Administrador (acceso total)
- Permisos por modulo: ver, crear, editar, eliminar, exportar
- Matriz de permisos editable

### Configuracion
- Datos empresa (razon social, CUIT, direccion)
- Pais (Venezuela/Argentina) — determina IVA y facturacion
- Sucursales
- Visual (nombre comercial, logo)
- Usuarios y roles
- Auditoria
- Desarrollador (backup, reset, password)

### Facturador
- Codigo de facturador configurable (F01, F02, etc.)
- Cada facturador tiene sucursal y depositos asignados
- Scanner de codigo de barras / busqueda por nombre
- Si producto en multiples depositos → pedir al cajero que elija
- Descuenta stock al cobrar
- Genera factura automatica

### Orden sugerida inteligente
- Analiza stock actual vs minimo
- Calcula velocidad de venta (salidas/dia)
- Estima dias de cobertura
- Sugiere cantidad a comprar
- Genera orden de compra automatica

### Notificaciones de cobro
- Estado de cuenta PDF por cliente
- Envio por WhatsApp (abre wa.me con mensaje)
- Envio por email (abre mailto con asunto y cuerpo)

## Navegacion

```
Login → Dashboard → Modulo → Submodulos
                  → Config → Empresa / Visual / Roles / Usuarios / Dev
                  → Cerrar sesion
```

## Estructura del proyecto

```
agilize_gestion/
├── main.py
├── core/               # config, database, auth, logging
├── models/             # SQLAlchemy models
├── services/           # Logica de negocio
├── ui/                 # Dashboard, login, temas, busqueda
├── modulos/
│   ├── rrhh/
│   ├── ventas/
│   ├── compras/
│   ├── facturador/
│   ├── inventario/
│   ├── cuentas/
│   ├── finanzas/
│   ├── reportes/
│   ├── herramientas/
│   ├── conexiones/
│   ├── datos/
│   └── configuracion/
├── scripts/            # build, instalador, seed, setup
├── tests/              # pytest
├── assets/             # logos, iconos
├── alembic/            # migraciones
└── docs/               # documentacion
```
