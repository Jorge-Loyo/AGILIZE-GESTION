# Guía de Implementación - Sincronización ERP Externo

## Resumen

Tu app (Agilize) consume datos del ERP externo (eComunik2Server) via API REST.
Cada 10 minutos se sincronizan: productos, precios, existencia, depósitos y clientes.

## Arquitectura

```
┌────────────────────────────────────────────────────────────┐
│                    SERVIDOR FISICO                           │
│                                                            │
│  ┌─────────────────────┐       ┌────────────────────────┐  │
│  │ VM Windows          │       │ VM Ubuntu Server       │  │
│  │                     │       │                        │  │
│  │ ERP + eComunik2     │ HTTP  │ Agilize + PostgreSQL   │  │
│  │ API REST :9000      │◄──────│ Cron cada 10 min       │  │
│  │                     │       │                        │  │
│  │ IP: 192.168.X.X     │       │ IP: 192.168.X.X       │  │
│  └─────────────────────┘       └────────────────────────┘  │
│                                                            │
│  Comunicacion: Red interna del host (bridge o host-only)    │
└────────────────────────────────────────────────────────────┘
```

---

## PREREQUISITOS

1. VM Windows con eComunik2Server corriendo en puerto 9000
2. VM Ubuntu con Agilize instalado y PostgreSQL funcionando
3. Ambas VM deben poder verse en red (ping entre ellas)

---

## PASO 1: Verificar API del ERP externo

Desde la VM Ubuntu (o cualquier PC en la misma red):

```bash
curl http://<IP_VM_WINDOWS>:9000
```

Debe responder:
```json
{"status": "online", "version": "0.9.8", "database": "Connected: True", ...}
```

Si no responde:
- Verificar que eComunik2Server esté corriendo en la VM Windows
- Verificar firewall de Windows permita puerto 9000
- Verificar red entre VMs (ping)

---

## PASO 2: Configurar variable de entorno

En la VM Ubuntu, editar el `.env` de Agilize:

```bash
cd /opt/agilize
nano .env
```

Agregar al final:
```
ERP_API_URL=http://192.168.X.X:9000
ERP_DEPOSITO=1
```

(Reemplazar `192.168.X.X` con la IP real de la VM Windows)

---

## PASO 3: Crear indexes en PostgreSQL

Ejecutar una sola vez:

```bash
cd /opt/agilize
venv/bin/python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, dbname='agilize_gestion', user='postgres', password='agilize2025')
conn.autocommit = True
cur = conn.cursor()
cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS uq_stock_prod_dep ON stock_deposito (producto_id, deposito_id) WHERE ubicacion_id IS NULL')
cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS uq_lista_precio_item ON lista_precio_venta_items (lista_id, producto_id)')
print('Indexes creados')
cur.close()
conn.close()
"
```

---

## PASO 4: Test manual de sincronización

```bash
cd /opt/agilize
ERP_API_URL=http://192.168.X.X:9000 venv/bin/python -m services.sync.sync_erp_externo
```

Debe mostrar algo como:
```
2026-06-27 [SYNC] INFO: === Sync iniciada | API: http://192.168.X.X:9000 ===
2026-06-27 [SYNC] INFO: API conectada: v0.9.8 - DB: Connected: True
2026-06-27 [SYNC] INFO:   Depositos: 3
2026-06-27 [SYNC] INFO:   Productos: 1250 | Precios: 5840 | Stock: 1250
2026-06-27 [SYNC] INFO:   Clientes: 380
2026-06-27 [SYNC] INFO: === Sync completada ===
```

---

## PASO 5: Configurar Cron (cada 10 minutos)

```bash
crontab -e
```

Agregar la línea:
```
*/10 * * * * cd /opt/agilize && ERP_API_URL=http://192.168.X.X:9000 ERP_DEPOSITO=1 venv/bin/python -m services.sync.sync_erp_externo >> logs/sync_erp.log 2>&1
```

Crear directorio de logs:
```bash
mkdir -p /opt/agilize/logs
```

---

## PASO 6: Verificar que funciona

```bash
# Ver logs en tiempo real
tail -f /opt/agilize/logs/sync_erp.log

# Ver última sync
cat /opt/agilize/logs/sync_erp.log | tail -20
```

---

## TROUBLESHOOTING

| Problema | Solución |
|---|---|
| "API no disponible" | Verificar IP, puerto 9000, firewall Windows |
| "Connection timed out" | Las VMs no se ven en red. Verificar bridge/NAT |
| "Producto no insertado" | Verificar que el codigo no esté vacío en el ERP |
| "Permission denied" en logs | `chmod 755 /opt/agilize/logs` |
| Cron no ejecuta | `systemctl status cron`, verificar con `crontab -l` |

---

## SOBRE SSH

Si querés ejecutar comandos en la VM Ubuntu desde esta PC:

```bash
ssh usuario@<IP_VM_UBUNTU>
cd /opt/agilize
# ejecutar lo que necesites
```

O si usás Tailscale (ya configurado según el historial):
```bash
ssh usuario@100.105.199.110
```

No hace falta SSH para la sincronización - el cron corre solo en la VM Ubuntu.
SSH es solo para configuración inicial y monitoreo.

---

## QUÉ SE SINCRONIZA

| Origen (API ERP) | Destino (PostgreSQL Agilize) |
|---|---|
| `/deposito` → codigo, descripcion | `depositos` → id, nombre |
| `/articulo` → codigo, descripcion, unidad, costo | `productos` → codigo, nombre, unidad_medida, precio_costo |
| `/articulo` → precio1 | `productos` → precio_venta |
| `/articulo` → precio1-5 | `lista_precio_venta_items` (5 listas) |
| `/articulo` → existencia | `stock_deposito` → cantidad |
| `/articulo` → categoriaNombre | `categorias_producto` (auto-crea) |
| `/cliente` → nombre, rif, direccion | `clientes` → razon_social, cuit_rif, direccion |
