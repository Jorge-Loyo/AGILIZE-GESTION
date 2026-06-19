# Plan de Despliegue: Servidor Centralizado con Tailscale

## Resumen

Arquitectura donde PostgreSQL corre en un servidor central y los clientes se conectan remotamente a traves de Tailscale (VPN mesh). Los usuarios instalan la app localmente (rapido, nativo) y solo la base de datos esta centralizada.

```
┌─────────────────────────────────────────────────────────┐
│                    SERVIDOR CENTRAL                       │
│  (PC fisica, VM, o VPS)                                  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ PostgreSQL   │  │  Tailscale   │  │  Firewall    │  │
│  │ puerto 5432  │  │  100.x.y.z   │  │  solo 5432   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
            │                    │
            │   Red Tailscale (encriptada)
            │                    │
     ┌──────┴──────┐     ┌──────┴──────┐
     │  CLIENTE 1  │     │  CLIENTE 2  │
     │  App local  │     │  App local  │
     │  Tailscale  │     │  Tailscale  │
     │  .env →     │     │  .env →     │
     │  100.x.y.z  │     │  100.x.y.z  │
     └─────────────┘     └─────────────┘
```

## Ventajas

- App corre nativa en cada PC (rapida, sin lag)
- BD centralizada (un solo lugar para backups)
- Acceso desde cualquier lugar (no solo LAN)
- Sin abrir puertos al internet publico
- Encriptacion end-to-end (Tailscale usa WireGuard)
- Gratis hasta 100 dispositivos (plan personal Tailscale)
- Sin necesidad de IP publica ni configurar router

## Requisitos

### Servidor
| Componente | Minimo | Recomendado |
|-----------|--------|-------------|
| OS | Windows 10+ / Ubuntu 22.04+ | Ubuntu Server 24.04 |
| RAM | 2 GB | 4 GB |
| Disco | 20 GB | 50 GB SSD |
| CPU | 2 cores | 4 cores |
| Red | Conexion a internet estable | Ethernet cableado |

### Clientes
| Componente | Requisito |
|-----------|-----------|
| OS | Windows 10+ |
| RAM | 2 GB libres |
| Red | Conexion a internet |
| Software | Tailscale + Agilize Gestion (modo Cliente) |

---

## Paso 1: Preparar el Servidor

### Opcion A: Servidor Windows (mas simple)

1. Usar una PC dedicada o una VM con Windows 10/11
2. Instalar Agilize Gestion con el Setup como **Servidor**
3. PostgreSQL queda corriendo automaticamente

### Opcion B: Servidor Ubuntu (recomendado para produccion)

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Iniciar y habilitar servicio
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Configurar password del usuario postgres
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'agilize2025';"

# Crear base de datos
sudo -u postgres createdb agilize_gestion

# Configurar para aceptar conexiones remotas
sudo nano /etc/postgresql/16/main/postgresql.conf
# Cambiar: listen_addresses = '*'

sudo nano /etc/postgresql/16/main/pg_hba.conf
# Agregar al final:
# host all all 100.64.0.0/10 md5
# (esto permite solo IPs de Tailscale)

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

---

## Paso 2: Instalar Tailscale en el Servidor

### Windows
```
Descargar de: https://tailscale.com/download/windows
Instalar → Iniciar sesion con Google/Microsoft/GitHub
Anotar la IP asignada (ej: 100.85.123.45)
```

### Ubuntu
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Seguir el link para autenticar
# Anotar la IP: tailscale ip -4
```

### Verificar
```bash
tailscale status
# Debe mostrar el dispositivo conectado con su IP 100.x.y.z
```

---

## Paso 3: Configurar Firewall del Servidor

### Ubuntu (UFW)
```bash
# Permitir PostgreSQL solo desde red Tailscale
sudo ufw allow in on tailscale0 to any port 5432
sudo ufw enable
```

### Windows
```
El instalador de Agilize ya crea la regla de firewall.
Si no, ejecutar como admin:
netsh advfirewall firewall add rule name="PostgreSQL-Tailscale" dir=in action=allow protocol=TCP localport=5432
```

---

## Paso 4: Configurar Clientes

### En cada PC cliente:

1. **Instalar Tailscale**
   - Descargar: https://tailscale.com/download/windows
   - Iniciar sesion con la **misma cuenta** que el servidor

2. **Verificar conexion**
   ```
   ping 100.85.123.45  (la IP Tailscale del servidor)
   ```

3. **Instalar Agilize Gestion**
   - Ejecutar Setup como **Cliente**
   - En el campo Host poner la **IP Tailscale del servidor** (ej: `100.85.123.45`)
   - Puerto: `5432`
   - Password: `agilize2025`

4. **O editar .env manualmente** (si ya esta instalada)
   ```env
   DB_HOST=100.85.123.45
   DB_PORT=5432
   DB_NAME=agilize_gestion
   DB_USER=postgres
   DB_PASSWORD=agilize2025
   ```

---

## Paso 5: Verificar Funcionamiento

1. En el servidor, verificar que PostgreSQL escucha:
   ```bash
   # Ubuntu
   sudo ss -tlnp | grep 5432

   # Windows
   netstat -an | findstr 5432
   ```

2. Desde un cliente, probar conexion:
   ```
   telnet 100.85.123.45 5432
   ```
   (Si conecta, esta todo bien)

3. Abrir Agilize Gestion → Login con `master` / `master2025`

---

## Paso 6: Backups Automaticos (Servidor Ubuntu)

Crear script de backup diario:

```bash
sudo nano /opt/backup_agilize.sh
```

Contenido:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/agilize"
mkdir -p $BACKUP_DIR
FECHA=$(date +%Y%m%d_%H%M)
pg_dump -U postgres agilize_gestion > "$BACKUP_DIR/backup_$FECHA.sql"
# Mantener solo ultimos 30 backups
ls -t $BACKUP_DIR/backup_*.sql | tail -n +31 | xargs -r rm
```

Programar con cron:
```bash
sudo chmod +x /opt/backup_agilize.sh
sudo crontab -e
# Agregar:
0 3 * * * /opt/backup_agilize.sh
```

---

## Paso 7: Tailscale - Funciones Utiles

### Compartir acceso sin cuenta
Si un usuario no quiere crear cuenta Tailscale, podes generar un link de invitacion:
```
Panel de Tailscale → Settings → Sharing → Invite
```

### Deshabilitar acceso a un usuario
```
Panel de Tailscale → Machines → Click en el dispositivo → Remove
```

### ACLs (Control de Acceso)
En el panel de Tailscale (https://login.tailscale.com/admin/acls) podes definir que solo ciertos dispositivos accedan al puerto 5432:

```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["group:agilize-users"],
      "dst": ["tag:server:5432"]
    }
  ]
}
```

---

## Costos

| Componente | Costo |
|-----------|-------|
| Tailscale (hasta 100 dispositivos) | Gratis |
| Ubuntu Server | Gratis |
| PostgreSQL | Gratis |
| Agilize Gestion | Licencia privada |
| Servidor fisico / VM | Segun proveedor |

### Opciones de servidor

| Opcion | Costo aprox | Nota |
|--------|-------------|------|
| PC vieja reciclada | $0 | Suficiente para 5-10 usuarios |
| VPS (Contabo/Hetzner) | $5-10 USD/mes | 4GB RAM, buena opcion remota |
| Raspberry Pi 4/5 | $80-120 USD unica vez | Bajo consumo, silencioso |
| VM en tu PC actual | $0 | Funciona mientras la PC este encendida |

---

## Troubleshooting

### Cliente no conecta al servidor
1. Verificar que ambos estan en la misma red Tailscale: `tailscale status`
2. Hacer ping a la IP Tailscale del servidor
3. Verificar que PostgreSQL escucha en el puerto 5432
4. Verificar `pg_hba.conf` permite la red 100.64.0.0/10

### Conexion lenta
- Tailscale usa conexion directa (peer-to-peer) cuando puede
- Si ambos estan detras de NAT estricto, puede usar relay (mas lento)
- Verificar: `tailscale netcheck`

### PostgreSQL no acepta conexiones remotas
```bash
# Verificar listen_addresses
sudo grep listen_addresses /etc/postgresql/16/main/postgresql.conf
# Debe ser: listen_addresses = '*'

# Verificar pg_hba.conf
sudo grep 100.64 /etc/postgresql/16/main/pg_hba.conf
# Debe tener: host all all 100.64.0.0/10 md5
```

### Multiples usuarios simultaneos
PostgreSQL soporta cientos de conexiones simultaneas sin problema.
Cada instancia de Agilize Gestion usa ~2-3 conexiones.
Con 10 usuarios concurrentes necesitas ~30 conexiones (el default de PG es 100).

---

## Resumen de Pasos Rapido

```
SERVIDOR:
1. Instalar PostgreSQL (o usar Setup como Servidor)
2. Instalar Tailscale → anotar IP (100.x.y.z)
3. Configurar PG para red remota

CLIENTES:
1. Instalar Tailscale (misma cuenta)
2. Instalar Agilize Gestion (modo Cliente, host = IP Tailscale)
3. Listo
```
