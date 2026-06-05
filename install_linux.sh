#!/bin/bash
echo "============================================"
echo "  Agilize Gestion - Instalador Linux"
echo "============================================"
echo ""

# Configuracion
APP_NAME="AgilizeGestion"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
DB_NAME="agilize_gestion"
DB_USER="postgres"
DB_PORT="5432"
DB_HOST="localhost"

# Pedir password
read -sp "Ingresa la contrasena de PostgreSQL (usuario postgres): " DB_PASSWORD
echo ""
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 no encontrado."
    echo "Instala con: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
echo "[OK] Python3 encontrado"

# Verificar PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "[ERROR] PostgreSQL no encontrado."
    echo "Instala con: sudo apt install postgresql postgresql-client"
    exit 1
fi
echo "[OK] PostgreSQL encontrado"

# Crear directorio
echo ""
echo "[1/7] Creando directorio de instalacion..."
mkdir -p "$INSTALL_DIR"
cp -r . "$INSTALL_DIR/"
echo "[OK] Archivos copiados a $INSTALL_DIR"

cd "$INSTALL_DIR"

# Entorno virtual
echo "[2/7] Creando entorno virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudo crear el entorno virtual."
    echo "Instala: sudo apt install python3-venv"
    exit 1
fi

# Dependencias
echo "[3/7] Instalando dependencias..."
venv/bin/pip install --quiet -r requirements.txt

# Configurar .env
echo "[4/7] Configurando conexion..."
cat > .env << EOF
# Base de Datos
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# Aplicacion
APP_NAME=Agilize Gestion
APP_VERSION=1.0.0
SESSION_TIMEOUT_MINUTES=30

# Seguridad
SECRET_KEY=agilize_$(date +%s%N | md5sum | head -c 16)
BCRYPT_ROUNDS=12
EOF

# Crear BD si no existe
echo "[5/7] Verificando base de datos..."
export PGPASSWORD=$DB_PASSWORD
DB_EXISTS=$(psql -U $DB_USER -h $DB_HOST -p $DB_PORT -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null | tr -d ' ')
if [ "$DB_EXISTS" != "1" ]; then
    echo "[INFO] Creando base de datos..."
    psql -U $DB_USER -h $DB_HOST -p $DB_PORT -c "CREATE DATABASE $DB_NAME;" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudo crear la BD. Verifica la contrasena."
        exit 1
    fi
    echo "[OK] Base de datos creada."
else
    echo "[OK] Base de datos ya existe, se mantienen los datos."
fi

# Migraciones
echo "[6/7] Ejecutando migraciones..."
venv/bin/alembic upgrade head

# Seed
echo "[7/7] Verificando datos iniciales..."
USER_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME -tc "SELECT COUNT(*) FROM usuarios" 2>/dev/null | tr -d ' ')
if [ "$USER_COUNT" = "0" ]; then
    echo "[INFO] Creando usuario inicial..."
    venv/bin/python -m scripts.seed
else
    echo "[OK] Ya existen usuarios."
fi

# Acceso directo
echo ""
echo "Creando acceso directo..."
cat > "$HOME/.local/share/applications/agilize-gestion.desktop" << EOF
[Desktop Entry]
Name=Agilize Gestion
Exec=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/main.py
Path=$INSTALL_DIR
Icon=$INSTALL_DIR/assets/logos/agilize_dev.jpg
Type=Application
Categories=Office;
EOF

echo ""
echo "============================================"
echo "  Instalacion completada!"
echo "============================================"
echo ""
echo "  Ubicacion: $INSTALL_DIR"
echo "  Usuario: master"
echo "  Contrasena: master2025"
echo ""
echo "  Ejecuta desde el menu de aplicaciones"
echo "  o con: $INSTALL_DIR/venv/bin/python $INSTALL_DIR/main.py"
echo ""
