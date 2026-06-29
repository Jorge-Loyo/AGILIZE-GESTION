# Gestión de Clientes - Branches, Servidores y Configuración

## Arquitectura de Branches

```
main (desarrollo general - mejoras para todos)
│
├── deploy/casa-dulce (versión Casa Dulce)
│
└── deploy/apinter (versión Apinter)
```

### Reglas de uso

| Qué hago | Dónde lo hago |
|---|---|
| Nueva funcionalidad para todos | `main` |
| Fix de bug general | `main` |
| Logo/nombre/config específica de 1 cliente | `deploy/cliente-x` |
| Módulo personalizado para 1 solo cliente | `deploy/cliente-x` |
| Aplicar mejora de main a un cliente | `git checkout deploy/cliente-x && git merge main` |

### Comandos frecuentes

```bash
# Desarrollar en main
git checkout main
# ...trabajar...
git add -A && git commit -m "feat: mejora X"
git push origin main

# Aplicar mejora a TODOS los clientes
git checkout deploy/casa-dulce && git merge main && git push origin deploy/casa-dulce
git checkout deploy/apinter && git merge main && git push origin deploy/apinter
git checkout main

# Personalización solo para 1 cliente
git checkout deploy/casa-dulce
# ...cambio específico...
git commit -m "custom: [Casa Dulce] cambio X"
git push origin deploy/casa-dulce
git checkout main

# Ver en qué branch estoy
git branch

# Ver todas las branches
git branch -a
```

---

## Clientes

### Cliente 1: Casa Dulce

| Campo | Valor |
|---|---|
| **Branch** | `deploy/casa-dulce` |
| **Rubro** | Distribuidora / Comercio |
| **País** | Venezuela |
| **IVA** | 16% |
| **Moneda** | USD / VES |

#### Servidor

| Campo | Valor |
|---|---|
| **VM** | Ubuntu Server 26 (VirtualBox en servidor físico del cliente) |
| **IP Local** | `192.168.0.232` |
| **IP Tailscale** | `100.110.38.117` |
| **SSH** | `ssh agilize@192.168.0.232` o `ssh agilize@100.110.38.117` |
| **User SSH** | `agilize` |
| **App Path** | `/opt/agilize` |

#### Base de Datos

| Campo | Valor |
|---|---|
| **Motor** | PostgreSQL 18 |
| **Host (local)** | `localhost:5432` |
| **Host (remoto Tailscale)** | `100.110.38.117:5432` |
| **Host (red local)** | `192.168.0.232:5432` |
| **Database** | `agilize_gestion` |
| **User** | `agilize` |
| **Password** | `agilize2025` |

#### PC Cliente (Punto de uso)

| Campo | Valor |
|---|---|
| **OS** | Windows |
| **App** | `Agilize.exe` (compilado PyInstaller) |
| **.env** | `DB_HOST=192.168.0.232` |
| **Login** | `master` / `master2025` |

#### ERP Externo (Sincronización pendiente)

| Campo | Valor |
|---|---|
| **Sistema** | eComunik2Server (DBISAM/Delphi) |
| **API** | `http://192.168.0.104:9000` |
| **Sync** | Cada 10 min via cron (pendiente activar) |
| **Datos** | Productos, precios, existencia, clientes |

#### Actualizar servidor Casa Dulce

```bash
ssh agilize@100.110.38.117
cd /opt/agilize
git pull origin deploy/casa-dulce
# Si hay cambios en modelos:
venv/bin/python -c "
from sqlalchemy import create_engine
from models.base import Base
from models import empleado, sucursal, usuario, rol, permiso, asistencia, nomina
from models import inventario, comercial, comercial_precios, compras, datos
from models import caja_pos, reclutamiento, facturador
from models import permiso_empleado, adelanto, aprobacion_extras, cierre
from models import vacaciones, sac, historico_sueldo, empresa, audit_log
from models import config_nomina, cuentas
engine = create_engine('postgresql://agilize:agilize2025@localhost:5432/agilize_gestion')
Base.metadata.create_all(engine)
print('Tablas actualizadas')
"
```

#### Recompilar .exe para Casa Dulce

```bash
# Desde PC de desarrollo, branch del cliente
git checkout deploy/casa-dulce
./venv/Scripts/pyinstaller --onefile --windowed --name "Agilize" --icon assets/logos/app_icon.ico --add-data "assets;assets" --add-data "ui/styles;ui/styles" main.py
# Copiar dist/Agilize.exe a la PC del cliente
git checkout main
```

---

### Cliente 2: Apinter

| Campo | Valor |
|---|---|
| **Branch** | `deploy/apinter` |
| **Rubro** | (por definir) |
| **País** | (por definir) |
| **IVA** | (por definir) |

#### Servidor

| Campo | Valor |
|---|---|
| **VM** | (pendiente configurar) |
| **IP Local** | (pendiente) |
| **IP Tailscale** | (pendiente) |
| **SSH** | (pendiente) |
| **App Path** | `/opt/agilize` |

#### Base de Datos

| Campo | Valor |
|---|---|
| **Motor** | PostgreSQL 18 |
| **Database** | `agilize_gestion` |
| **User** | `agilize` |
| **Password** | (por definir) |

#### Notas
- Pendiente: instalar VM, configurar BD, compilar .exe
- Branch lista: `deploy/apinter` (idéntica a main actualmente)

---

## Procedimiento: Agregar nuevo cliente

1. **Crear branch:**
   ```bash
   git checkout main
   git checkout -b deploy/nombre-cliente
   git push origin deploy/nombre-cliente
   git checkout main
   ```

2. **Configurar VM Ubuntu:**
   - Instalar Ubuntu Server
   - Instalar PostgreSQL
   - Configurar usuario + BD
   - Instalar Tailscale (opcional, para acceso remoto)
   - Clonar repo + branch del cliente
   - Configurar .env local

3. **Compilar .exe:**
   ```bash
   git checkout deploy/nombre-cliente
   # compilar con PyInstaller
   git checkout main
   ```

4. **Entregar al cliente:**
   - Copiar .exe + .env a PC del cliente
   - Crear acceso directo
   - Capacitar usuario

5. **Actualizar este documento** con los datos del nuevo cliente

---

## Procedimiento: Desplegar actualización

### Para TODOS los clientes:
```bash
# 1. Desarrollar en main
git checkout main
git add -A && git commit -m "feat: mejora"
git push origin main

# 2. Merge a cada cliente
git checkout deploy/casa-dulce && git merge main && git push origin deploy/casa-dulce
git checkout deploy/apinter && git merge main && git push origin deploy/apinter
git checkout main

# 3. En cada servidor:
ssh agilize@IP_SERVIDOR
cd /opt/agilize && git pull origin deploy/BRANCH

# 4. Si cambió la UI, recompilar .exe y distribuir
```

### Para UN solo cliente:
```bash
git checkout deploy/cliente-x
# hacer cambio
git commit && git push
# actualizar servidor de ese cliente
```

---

## Dependencias del sistema

### Servidor (Ubuntu)
- Python 3.11+
- PostgreSQL 16+
- Tailscale (acceso remoto)
- Git

### Cliente (Windows)
- `Agilize.exe` (incluye todo, no necesita instalar nada)
- `.env` con conexión a BD
- Red local con acceso al servidor

### Desarrollo (tu PC)
- Python 3.11+
- Git
- PyInstaller (para compilar)
- VSCode + Amazon Q
- Tailscale (para acceso remoto a servidores)
