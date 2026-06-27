# eComunik2Server — Documentación de Integración API REST

> **Versión:** 0.9.8 · **Arquitectura:** Modular · **Base URL:** `http://<host>:9000`

---

## Tabla de Contenidos

1. [Información General](#1-información-general)
2. [Autenticación](#2-autenticación)
3. [Convenciones](#3-convenciones)
4. [Health Check](#4-health-check)
5. [Clientes](#5-clientes-cliente)
6. [Artículos / Productos](#6-artículos--productos-articulo)
7. [Depósitos](#7-depósitos-deposito)
8. [Pedidos / Órdenes](#8-pedidos--órdenes-orders)
9. [Vendedores](#9-vendedores-vendedor)
10. [Usuarios](#10-usuarios-usuario)
11. [Códigos de Error](#11-códigos-de-error)
12. [Paginación](#12-paginación)

---

## 1. Información General

| Ítem | Detalle |
|---|---|
| **Protocolo** | HTTP (sin SSL nativo; usar proxy reverso para HTTPS) |
| **Puerto por defecto** | `9000` |
| **Formato de datos** | JSON (`Content-Type: application/json`) |
| **Framework** | Horse (Delphi/Object Pascal) |
| **Base de Datos** | DBISAM (basada en archivos) |
| **CORS** | Habilitado via middleware `horse-cors` |

### URL Base

```
http://<IP_o_HOSTNAME>:9000
```

---

## 2. Autenticación

> **Estado actual:** La API **no requiere autenticación** en la mayoría de endpoints en la versión 0.9.8. El módulo `AuthUnit.pas` existe pero la integración de middleware de autenticación está pendiente.

Para integraciones en producción se recomienda proteger la API con un proxy reverso (Nginx, Caddy) que maneje SSL y tokens de autenticación.

---

## 3. Convenciones

### Formato de Request

- Todos los `POST` y `PUT` deben enviar el body como JSON con header:
  ```
  Content-Type: application/json
  ```

### Formato de Response Exitosa

```json
// Objeto único
{ "campo": "valor", ... }

// Lista sin paginación
[ { ... }, { ... } ]

// Lista con paginación
{
  "page": 1,
  "limit": 50,
  "total": 120,
  "total_pages": 3,
  "data": [ { ... } ]
}
```

### Formato de Error

```json
{
  "error": "Descripción del error"
}
```

---

## 4. Health Check

### `GET /`

Verifica el estado del servidor y lista los endpoints disponibles.

**Response 200:**

```json
{
  "status": "online",
  "message": "API REST - Sistema de Inventario y Ventas",
  "version": "0.9.8",
  "architecture": "Modular",
  "database": "Connected: True",
  "config": {
    "depositoPorDefecto": 1
  },
  "endpoints": {
    "clientes": "/cliente",
    "productos": "/articulo",
    "pedidos": "/orders",
    "depositos": "/deposito",
    "vendedores": "/vendedor",
    "usuarios": "/usuario"
  }
}
```

---

## 5. Clientes (`/cliente`)

### 5.1 `GET /cliente` — Listar clientes

Retorna la lista de clientes. Soporta paginación y búsqueda.

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `page` | integer | Número de página (default: 1) |
| `limit` | integer | Registros por página (default: 50, max: 10000) |
| `q` | string | Búsqueda por nombre/RIF |
| `search` | string | Alias de `q` |
| `rif` | string | Filtrar por RIF exacto |
| `activo` | boolean | Filtrar por estado (`true`/`false`) |

**Response 200 sin paginación:**
```json
[
  {
    "id": 1,
    "rif": "J-12345678-9",
    "nombre": "EMPRESA EJEMPLO C.A.",
    "direccion": "Caracas, Venezuela",
    "telefono": "0212-1234567",
    "email": "contacto@empresa.com",
    "activo": true
  }
]
```

**Response 200 con paginación:**
```json
{
  "page": 1,
  "limit": 50,
  "total": 150,
  "total_pages": 3,
  "data": [ { ... } ]
}
```

---

### 5.2 `GET /cliente/:id` — Obtener cliente por ID

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:id` | integer | ID numérico del cliente |

**Response 200:**
```json
{
  "id": 1,
  "rif": "J-12345678-9",
  "nombre": "EMPRESA EJEMPLO C.A.",
  "direccion": "Caracas, Venezuela",
  "telefono": "0212-1234567",
  "email": "contacto@empresa.com",
  "activo": true
}
```

**Response 404:**
```json
{ "error": "Cliente no encontrado" }
```

---

### 5.3 `GET /cliente/items/:cantidad` — Últimos N clientes

Retorna los últimos `:cantidad` clientes registrados.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:cantidad` | integer | Cantidad de registros a retornar |

**Response 200:** Array de objetos cliente.

---

### 5.4 `POST /cliente` — Crear cliente

**Body:**
```json
{
  "rif": "J-98765432-1",
  "nombre": "NUEVO CLIENTE S.A.",
  "direccion": "Av. Principal, Maracaibo",
  "telefono": "0261-9876543",
  "email": "info@nuevocliente.com"
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Cliente creado correctamente",
  "id": 42
}
```

---

### 5.5 `PUT /cliente/:id` — Actualizar cliente

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:id` | integer | ID del cliente a actualizar |

**Body:** (campos a actualizar)
```json
{
  "nombre": "NOMBRE ACTUALIZADO S.A.",
  "telefono": "0212-9999999",
  "email": "nuevo@email.com",
  "direccion": "Nueva dirección",
  "activo": true
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Cliente actualizado correctamente"
}
```

---

## 6. Artículos / Productos (`/articulo`)

### 6.1 `GET /articulo` — Listar artículos

Retorna los artículos del inventario con precios y existencias.

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `page` | integer | Número de página |
| `limit` | integer | Registros por página (default: 50, max: 10000) |
| `deposito` | integer | Código de depósito para existencias (default: `depositoPorDefecto`) |
| `activo` | boolean | Filtrar por estado (`true`/`false`). Sin valor = todos |

**Response 200 sin paginación:** Array de artículos.

**Response 200 con paginación:**
```json
{
  "page": 1,
  "limit": 50,
  "total": 500,
  "total_pages": 10,
  "deposito": 1,
  "data": [
    {
      "codigo": "ART001",
      "descripcion": "Artículo de Ejemplo",
      "categoria": "CAT1",
      "categoriaNombre": "Electrónicos",
      "descripcionDetallada": "Descripción completa del artículo",
      "vendedor": "31",
      "activo": true,
      "unidad": "UND",
      "referencia": "REF-001",
      "marca": "MARCA",
      "moneda": 1,
      "puesto": "",
      "peso": 0.5,
      "garantia": 12.0,
      "fechaCreacion": "2024-01-15",
      "modelo": "MOD-X",
      "subcategoria": "SUB1",
      "id": 1,
      "costo": 10.00,
      "precio1": 15.00,
      "precio2": 14.00,
      "precio3": 13.00,
      "precio4": 12.50,
      "precio5": 12.00,
      "precio6": 11.50,
      "impuestoPorcentaje": 16.0,
      "existencia": 100.0,
      "existenciaDetallada": "",
      "existenciaApartada": 5.0,
      "existenciaPedido": 10.0,
      "existenciaDisponible": 95.0,
      "deposito": 1
    }
  ]
}
```

---

### 6.2 `GET /articulo/:id` — Obtener artículo por ID

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:id` | integer | ID autoincremental del artículo |
| `deposito` | integer (query) | Depósito para existencias |
| `activo` | boolean (query) | Filtro de estado |

**Response 200:** Objeto artículo.

**Response 404:**
```json
{ "error": "Producto no encontrado" }
```

---

### 6.3 `GET /articulo/codigo/:codigo` — Obtener artículo por código

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:codigo` | string | Código del artículo (ej: `ART001`) |
| `deposito` | integer (query) | Depósito para existencias |

**Response 200:** Objeto artículo completo.

---

### 6.4 `GET /articulo/search` — Buscar artículos

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `nombre` o `q` | string | Término de búsqueda en descripción y código |
| `codigo` | string | Búsqueda específica por código |
| `deposito` | integer | Depósito para existencias |
| `activo` | boolean | Filtrar por estado |
| `page` | integer | Paginación |
| `limit` | integer | Registros por página |

> Al menos uno de `nombre`, `q` o `codigo` es **requerido**.

**Response 200 sin paginación:**
```json
{
  "termino_busqueda": "laptop",
  "resultados_encontrados": 5,
  "deposito": 1,
  "articulos": [ { ... } ]
}
```

**Response 200 con paginación:**
```json
{
  "termino_busqueda": "laptop",
  "page": 1,
  "limit": 10,
  "total": 5,
  "total_pages": 1,
  "deposito": 1,
  "data": [ { ... } ]
}
```

---

## 7. Depósitos (`/deposito`)

### 7.1 `GET /deposito` — Listar depósitos activos

**Response 200:**
```json
[
  {
    "codigo": 1,
    "descripcion": "DEPÓSITO PRINCIPAL",
    "activo": true
  },
  {
    "codigo": 2,
    "descripcion": "DEPÓSITO SECUNDARIO",
    "activo": true
  }
]
```

---

### 7.2 `GET /deposito/:codigo` — Obtener depósito por código

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:codigo` | integer | Código numérico del depósito |

**Response 200:**
```json
{
  "codigo": 1,
  "descripcion": "DEPÓSITO PRINCIPAL",
  "activo": true
}
```

**Response 404:**
```json
{ "error": "Depósito no encontrado" }
```

---

## 8. Pedidos / Órdenes (`/orders`)

### 8.1 `GET /orders` — Listar pedidos

Retorna todos los pedidos de tipo 10 (Órdenes de Venta) ordenados por ID descendente.

**Response 200:**
```json
{
  "total": 25,
  "orders": [
    {
      "id": 100,
      "documento": "00000100",
      "tipo": 10,
      "status": 4,
      "visible": true,
      "fechaEmision": "2024-03-15",
      "depositoSource": 1,
      "depositoDestino": 1,
      "totalItems": 3,
      "moneda": 1,
      "factorCambio": 36.50,
      "totalCosto": 150.00,
      "totalBruto": 210.00,
      "totalNeto": 243.60,
      "baseImponible": 210.00,
      "rifCliente": "J-12345678-9",
      "personaContacto": "Juan Pérez",
      "telefonoContacto": "0414-1234567",
      "direccionDespacho": "Av. Principal",
      "vendedorAsignado": "31",
      "impuesto1Monto": 33.60,
      "comentarios": ""
    }
  ]
}
```

---

### 8.2 `GET /orders/:id` — Obtener pedido por ID

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:id` | integer | ID autoincremental del pedido |

**Response 200:** Objeto pedido completo con todos los campos.

**Response 404:**
```json
{ "error": "Pedido no encontrado" }
```

---

### 8.3 `GET /orders/:id/details` — Obtener líneas del pedido

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:id` | integer | ID del pedido |

**Response 200:**
```json
{
  "order_id": "100",
  "total_items": 3,
  "details": [
    {
      "id": 1,
      "codigoProducto": "ART001",
      "descripcionProducto": "Artículo de Ejemplo",
      "unidad": "UND",
      "linea": 1,
      "cantidad": 5.0,
      "costo": 10.00,
      "precioVenta": 15.00,
      "impuesto1": 0.0,
      "descuento": 0.0,
      "detalles": ""
    }
  ]
}
```

---

### 8.4 `GET /orders/:id/full` — Obtener pedido completo con detalles

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:id` | integer | ID del pedido |

**Response 200:** Cabecera del pedido + array `details` con las líneas.

```json
{
  "id": 100,
  "documento": "00000100",
  "...": "...todos los campos de cabecera...",
  "details": [
    {
      "id": 1,
      "codigoProducto": "ART001",
      "cantidad": 5.0,
      "precioVenta": 15.00
    }
  ]
}
```

---

### 8.5 `POST /orders` — Crear pedido

Crea un nuevo pedido con cabecera y líneas de detalle en una sola transacción.

**Body:**
```json
{
  "rifCliente": "J-12345678-9",
  "personaContacto": "Juan Pérez",
  "telefonoContacto": "0414-1234567",
  "direccionDespacho": "Av. Principal, Caracas",
  "vendedorAsignado": "31",
  "moneda": 1,
  "factorCambio": 36.50,
  "depositoSource": 1,
  "depositoDestino": 1,
  "tipoPrecio": 1,
  "impuesto1Porcent": 16.0,
  "comentarios": "Pedido de prueba",
  "details": [
    {
      "codigoProducto": "ART001",
      "cantidad": 5.0,
      "precioVenta": 15.00,
      "costo": 10.00,
      "porcentImpuesto1": 16.0,
      "descuento": 0.0,
      "detalles": "Observación línea 1"
    },
    {
      "codigoProducto": "ART002",
      "cantidad": 2.0,
      "precioVenta": 25.00,
      "costo": 18.00,
      "porcentImpuesto1": 16.0
    }
  ]
}
```

**Campos requeridos del body:**

| Campo | Tipo | Descripción |
|---|---|---|
| `rifCliente` | string | RIF del cliente (**requerido**) |
| `personaContacto` | string | Nombre de contacto (**requerido**) |
| `details` | array | Líneas del pedido, mínimo 1 (**requerido**) |

**Campos requeridos por línea:**

| Campo | Tipo | Descripción |
|---|---|---|
| `codigoProducto` | string | Código del producto (**requerido**) |
| `cantidad` | number | Cantidad > 0 (**requerido**) |
| `precioVenta` | number | Precio de venta > 0 (**requerido**) |

**Campos opcionales del body y sus defaults:**

| Campo | Default | Descripción |
|---|---|---|
| `status` | `4` | Estado del pedido |
| `moneda` | `1` | Moneda |
| `factorCambio` | `1.0` | Factor de cambio |
| `depositoSource` | `depositoPorDefecto` | Depósito origen |
| `depositoDestino` | `depositoPorDefecto` | Depósito destino |
| `tipoPrecio` | `1` | Tipo de precio |
| `impuesto1Porcent` | `16` | % IVA |
| `diasVencimiento` | `15` | Días para vencimiento |
| `vendedorAsignado` | `"31"` | Código del vendedor |
| `zonaventa` | `"01"` | Zona de venta |
| `proposito` | `"PEDIDO ICOMPRAS"` | Propósito |
| `comentarios` | `""` | Comentarios |

**Response 201:**
```json
{
  "success": true,
  "message": "Pedido creado correctamente",
  "order_id": 101,
  "documento": "00000101",
  "depositoSource": 1,
  "depositoDestino": 1,
  "total_items": 2,
  "base_imponible": 125.00,
  "impuesto_monto": 20.00,
  "total_neto": 145.00,
  "fecha_emision": "2024-03-15 14:30:00"
}
```

**Response 400 (validación):**
```json
{ "error": "Productos no encontrado: ART999" }
```

---

## 9. Vendedores (`/vendedor`)

### 9.1 `GET /vendedor` — Listar vendedores

**Response 200:**
```json
[
  {
    "codigo": "31",
    "descripcion": "VENDEDOR PRINCIPAL",
    "direccion": "Caracas",
    "email": "vendedor@empresa.com",
    "activo": true
  }
]
```

---

### 9.2 `GET /vendedor/:codigo` — Obtener vendedor por código

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:codigo` | string | Código del vendedor |

**Response 200:** Objeto vendedor.
**Response 404:** `{ "error": "Vendedor no encontrado" }`

---

### 9.3 `POST /vendedor` — Crear vendedor

**Body:**
```json
{
  "codigo": "32",
  "descripcion": "NUEVO VENDEDOR",
  "direccion": "Valencia, Venezuela",
  "email": "nuevo@vendedor.com",
  "activo": true
}
```

**Campos requeridos:** `codigo`, `descripcion`

**Response 201:**
```json
{
  "success": true,
  "message": "Vendedor creado correctamente",
  "codigo": "32"
}
```

---

### 9.4 `PUT /vendedor/:codigo` — Actualizar vendedor

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:codigo` | string | Código del vendedor |

**Body:**
```json
{
  "descripcion": "NOMBRE ACTUALIZADO",
  "direccion": "Nueva dirección",
  "email": "nuevo@email.com",
  "activo": true
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Vendedor actualizado correctamente"
}
```

---

### 9.5 `DELETE /vendedor/:codigo` — Eliminar vendedor

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:codigo` | string | Código del vendedor |

**Response 200:**
```json
{
  "success": true,
  "message": "Vendedor eliminado correctamente"
}
```

---

## 10. Usuarios (`/usuario`)

### 10.1 `GET /usuario` — Listar usuarios

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `page` | integer | Paginación |
| `limit` | integer | Registros por página |
| `activo` | boolean | Filtrar activos/inactivos |

**Response 200:**
```json
[
  {
    "codigo": 1,
    "nombre": "admin",
    "clave": "***",
    "email": "admin@empresa.com",
    "activo": true
  }
]
```

---

### 10.2 `GET /usuario/:nombre` — Obtener usuario por nombre

| Parámetro | Tipo | Descripción |
|---|---|---|
| `:nombre` | string | Nombre de usuario |

**Response 200:** Objeto usuario.
**Response 404:** `{ "error": "Usuario no encontrado" }`

---

### 10.3 `GET /usuario/search` — Buscar usuarios

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `q` o `nombre` | string | Término de búsqueda |
| `activo` | boolean | Filtrar por estado |

**Response 200:** Array de usuarios coincidentes.

---

## 11. Códigos de Error

| Código HTTP | Significado |
|---|---|
| `200` | OK — Operación exitosa |
| `201` | Created — Recurso creado |
| `400` | Bad Request — Parámetros inválidos o faltantes |
| `404` | Not Found — Recurso no encontrado |
| `500` | Internal Server Error — Error del servidor o base de datos |

---

## 12. Paginación

La paginación se activa automáticamente al proporcionar los parámetros `page` y/o `limit` en la query string.

**Sin paginación** → retorna el array completo.

**Con paginación** → retorna un objeto envolvente:

```
GET /articulo?page=2&limit=25&deposito=1
```

```json
{
  "page": 2,
  "limit": 25,
  "total": 500,
  "total_pages": 20,
  "deposito": 1,
  "data": [ ... ]
}
```

**Valores límite:**
- `page` mínimo: `1`
- `limit` mínimo: `1`, máximo: `10.000`
