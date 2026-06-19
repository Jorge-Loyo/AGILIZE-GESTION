#!/bin/bash
# ============================================
# Agilize Gestion - Setup Servidor
# Instala PostgreSQL + Tailscale + Firewall + Backups
# Ejecutar como root: sudo bash setup_servidor.sh
# ============================================

set -e

echo "============================================"
echo "  AGILIZE GESTION - Setup Servidor"
echo "============================================"
echo ""

# Variables
DB_PASSWORD="${1:-agilize2025}"
DB_NAME="agilize_gestion"
DB_USER="postgres"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[INFO]${NC} $1"; }

# ============================================
# 1. Actualizar sistema
# ============================================
echo ""
warn "Paso 1/5: Actualizando sistema..."
apt-get update -qq
apt-get upgrade -y -qq
log "Sistema actualizado"

# ============================================
# 2. Instalar PostgreSQL
# ============================================
echo ""
warn "Paso 2/5: Instalando PostgreSQL..."
apt-get install -y -qq postgresql postgresql-contrib

# Iniciar y habilitar
systemctl enable postgresql
systemctl start postgresql

# Configurar password
sudo -u postgres psql -c "ALTER USER postgres PASSWORD '$DB_PASSWORD';" 2>/dev/null
log "Password de PostgreSQL configurado"

# Crear base de datos
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    sudo -u postgres createdb $DB_NAME
log "Base de datos '$DB_NAME' lista"

# Configurar para aceptar conexiones remotas
PG_VERSION=$(ls /etc/postgresql/ | sort -V | tail -1)
PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

# listen_addresses
if grep -q "^listen_addresses" $PG_CONF; then
    sed -i "s/^listen_addresses.*/listen_addresses = '*'/" $PG_CONF
else
    echo "listen_addresses = '*'" >> $PG_CONF
fi

# pg_hba.conf - permitir red Tailscale
if ! grep -q "100.64.0.0/10" $PG_HBA; then
    echo "" >> $PG_HBA
    echo "# Agilize Gestion - Red Tailscale" >> $PG_HBA
    echo "host all all 100.64.0.0/10 md5" >> $PG_HBA
    echo "# Red local" >> $PG_HBA
    echo "host all all 192.168.0.0/16 md5" >> $PG_HBA
    echo "host all all 10.0.0.0/8 md5" >> $PG_HBA
fi

# Reiniciar PostgreSQL
systemctl restart postgresql
log "PostgreSQL configurado para conexiones remotas"

# ============================================
# 3. Instalar Tailscale
# ============================================
echo ""
warn "Paso 3/5: Instalando Tailscale..."
if ! command -v tailscale &> /dev/null; then
    curl -fsSL https://tailscale.com/install.sh | sh
    log "Tailscale instalado"
else
    log "Tailscale ya estaba instalado"
fi

echo ""
echo "============================================"
echo "  IMPORTANTE: Autenticar Tailscale"
echo "============================================"
echo ""
echo "Ejecuta este comando y segui el link:"
echo ""
echo "  sudo tailscale up"
echo ""
echo "Despues de autenticar, ejecuta:"
echo ""
echo "  tailscale ip -4"
echo ""
echo "Esa IP (100.x.y.z) es la que usan los clientes."
echo "============================================"
echo ""

# ============================================
# 4. Configurar Firewall
# ============================================
warn "Paso 4/5: Configurando firewall..."
apt-get install -y -qq ufw

# Permitir SSH
ufw allow ssh 2>/dev/null || true

# Permitir PostgreSQL desde Tailscale
ufw allow in on tailscale0 to any port 5432 2>/dev/null || true

# Permitir PostgreSQL desde red local
ufw allow from 192.168.0.0/16 to any port 5432 2>/dev/null || true
ufw allow from 10.0.0.0/8 to any port 5432 2>/dev/null || true

# Activar firewall
echo "y" | ufw enable 2>/dev/null || true
log "Firewall configurado (SSH + PostgreSQL)"

# ============================================
# 5. Backup automatico
# ============================================
warn "Paso 5/5: Configurando backups automaticos..."

mkdir -p /opt/backups/agilize

cat > /opt/backup_agilize.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/agilize"
mkdir -p $BACKUP_DIR
FECHA=$(date +%Y%m%d_%H%M)
sudo -u postgres pg_dump agilize_gestion > "$BACKUP_DIR/backup_$FECHA.sql" 2>/dev/null
# Mantener ultimos 30 backups
ls -t $BACKUP_DIR/backup_*.sql 2>/dev/null | tail -n +31 | xargs -r rm
EOF

chmod +x /opt/backup_agilize.sh

# Agregar a cron (3 AM todos los dias)
(crontab -l 2>/dev/null | grep -v backup_agilize; echo "0 3 * * * /opt/backup_agilize.sh") | crontab -
log "Backup diario configurado (3:00 AM)"

# ============================================
# Resumen
# ============================================
echo ""
echo "============================================"
echo "  INSTALACION COMPLETADA"
echo "============================================"
echo ""
echo "  PostgreSQL:"
echo "    Puerto: 5432"
echo "    Usuario: postgres"
echo "    Password: $DB_PASSWORD"
echo "    Base de datos: $DB_NAME"
echo ""
echo "  Backups:"
echo "    Ubicacion: /opt/backups/agilize/"
echo "    Frecuencia: Diario a las 3:00 AM"
echo ""
echo "  SIGUIENTE PASO:"
echo "    1. Ejecutar: sudo tailscale up"
echo "    2. Autenticar en el link que aparece"
echo "    3. Obtener IP: tailscale ip -4"
echo "    4. En los clientes, usar esa IP como DB_HOST"
echo ""
echo "  CONFIGURACION DEL CLIENTE (.env):"
echo "    DB_HOST=<IP_TAILSCALE>"
echo "    DB_PORT=5432"
echo "    DB_NAME=agilize_gestion"
echo "    DB_USER=postgres"
echo "    DB_PASSWORD=$DB_PASSWORD"
echo ""
echo "============================================"
