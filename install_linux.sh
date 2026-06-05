#!/bin/bash
echo "============================================"
echo "  Agilize Gestion - Instalador Linux"
echo "============================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 no encontrado. Instala con: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

echo "[1/5] Creando entorno virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudo crear el entorno virtual."
    echo "[INFO] Instala: sudo apt install python3-venv"
    exit 1
fi

echo "[2/5] Instalando dependencias..."
venv/bin/pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudieron instalar las dependencias."
    exit 1
fi

echo "[3/5] Instalando PyInstaller..."
venv/bin/pip install pyinstaller

echo "[4/5] Configuracion..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[INFO] Archivo .env creado. Edita con tus datos de PostgreSQL."
fi

echo "[5/5] Permisos..."
chmod +x scripts/build.py

echo ""
echo "============================================"
echo "  Instalacion completada!"
echo "============================================"
echo ""
echo "Para ejecutar: venv/bin/python main.py"
echo "Para generar ejecutable: venv/bin/python scripts/build.py"
echo ""
echo "Asegurate de:"
echo "  1. Tener PostgreSQL corriendo"
echo "  2. Crear la BD: CREATE DATABASE agilize_gestion;"
echo "  3. Editar .env con tus datos"
echo "  4. Ejecutar: venv/bin/alembic upgrade head"
echo "  5. Ejecutar: venv/bin/python -m scripts.seed"
