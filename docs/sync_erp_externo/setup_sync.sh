#!/bin/bash
# ============================================================
# Setup de sincronizacion ERP externo en Ubuntu Server
# Ejecutar como root: sudo bash setup_sync.sh
# ============================================================

echo "=== Configurar sincronizacion con ERP externo ==="

# Variables (ajustar)
VM_WINDOWS_IP="192.168.1.100"  # IP de la VM Windows con DBISAM
SHARE_NAME="export_erp"
MOUNT_POINT="/mnt/export_erp"
SMB_USER="usuario"             # Usuario Windows con acceso al share
SMB_PASS="password"            # Password (se guarda en archivo seguro)
APP_DIR="/opt/agilize"

# 1. Instalar cifs-utils
echo "[1/5] Instalando cifs-utils..."
apt-get install -y cifs-utils

# 2. Crear punto de montaje
echo "[2/5] Creando punto de montaje..."
mkdir -p $MOUNT_POINT

# 3. Crear archivo de credenciales (seguro)
echo "[3/5] Configurando credenciales SMB..."
cat > /etc/samba/credentials_erp <<EOF
username=$SMB_USER
password=$SMB_PASS
EOF
chmod 600 /etc/samba/credentials_erp

# 4. Agregar a fstab para montaje automatico
echo "[4/5] Configurando montaje automatico..."
FSTAB_LINE="//$VM_WINDOWS_IP/$SHARE_NAME $MOUNT_POINT cifs credentials=/etc/samba/credentials_erp,uid=1000,gid=1000,iocharset=utf8,vers=3.0 0 0"

if ! grep -q "$SHARE_NAME" /etc/fstab; then
    echo "$FSTAB_LINE" >> /etc/fstab
    echo "  Agregado a /etc/fstab"
fi

# Montar ahora
mount $MOUNT_POINT
echo "  Montado: $MOUNT_POINT"

# 5. Configurar cron cada 10 minutos
echo "[5/5] Configurando cron..."
CRON_LINE="*/10 * * * * cd $APP_DIR && SYNC_CSV_PATH=$MOUNT_POINT venv/bin/python -m services.sync.sync_erp_externo >> logs/sync_erp.log 2>&1"

# Crear directorio de logs
mkdir -p $APP_DIR/logs

(crontab -l 2>/dev/null | grep -v "sync_erp_externo"; echo "$CRON_LINE") | crontab -
echo "  Cron configurado: cada 10 minutos"

echo ""
echo "=== LISTO ==="
echo ""
echo "Verificar montaje: ls $MOUNT_POINT"
echo "Test manual: cd $APP_DIR && SYNC_CSV_PATH=$MOUNT_POINT venv/bin/python -m services.sync.sync_erp_externo"
echo "Ver logs: tail -f $APP_DIR/logs/sync_erp.log"
echo ""
echo "IMPORTANTE: Ajustar las variables al inicio del script:"
echo "  VM_WINDOWS_IP=$VM_WINDOWS_IP"
echo "  SMB_USER=$SMB_USER"
echo "  SMB_PASS=****"
