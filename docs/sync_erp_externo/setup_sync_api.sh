#!/bin/bash
# ============================================================
# Setup sincronizacion ERP externo via API REST
# Ejecutar como root: sudo bash setup_sync_api.sh
# ============================================================

APP_DIR="/opt/agilize"
ERP_API_URL="http://192.168.1.100:9000"  # Ajustar IP de la VM Windows
ERP_DEPOSITO="1"

echo "=== Configurar sincronizacion API ERP externo ==="
echo "    API: $ERP_API_URL"
echo ""

# 1. Crear directorio de logs
mkdir -p $APP_DIR/logs
echo "[1/3] Directorio logs OK"

# 2. Crear archivo de variables de entorno para el sync
cat > $APP_DIR/.env.sync <<EOF
ERP_API_URL=$ERP_API_URL
ERP_DEPOSITO=$ERP_DEPOSITO
EOF
chmod 600 $APP_DIR/.env.sync
echo "[2/3] Variables de entorno configuradas"

# 3. Configurar cron cada 10 minutos
CRON_LINE="*/10 * * * * cd $APP_DIR && ERP_API_URL=$ERP_API_URL ERP_DEPOSITO=$ERP_DEPOSITO venv/bin/python -m services.sync.sync_erp_externo >> logs/sync_erp.log 2>&1"
(crontab -l 2>/dev/null | grep -v "sync_erp_externo"; echo "$CRON_LINE") | crontab -
echo "[3/3] Cron configurado: cada 10 minutos"

echo ""
echo "=== LISTO ==="
echo ""
echo "Test manual:"
echo "  cd $APP_DIR && ERP_API_URL=$ERP_API_URL venv/bin/python -m services.sync.sync_erp_externo"
echo ""
echo "Ver logs:"
echo "  tail -f $APP_DIR/logs/sync_erp.log"
echo ""
echo "Verificar API:"
echo "  curl $ERP_API_URL"
