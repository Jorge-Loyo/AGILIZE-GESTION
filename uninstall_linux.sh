#!/bin/bash
echo "============================================"
echo "  Agilize Gestion - Desinstalador Linux"
echo "============================================"
echo ""

APP_NAME="AgilizeGestion"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"

echo "ATENCION: Esto eliminara la aplicacion pero NO la base de datos."
echo "Los datos se mantienen para una futura reinstalacion."
echo ""
echo "Directorio: $INSTALL_DIR"
echo ""

read -p "Deseas continuar? (s/n): " CONFIRMAR
if [ "$CONFIRMAR" != "s" ] && [ "$CONFIRMAR" != "S" ]; then
    echo "Cancelado."
    exit 0
fi

echo ""
echo "[1/3] Eliminando acceso directo..."
rm -f "$HOME/.local/share/applications/agilize-gestion.desktop"
echo "[OK]"

echo "[2/3] Eliminando archivos..."
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "[OK] Directorio eliminado."
else
    echo "[INFO] No se encontro el directorio."
fi

echo "[3/3] Limpieza completada."
echo ""
echo "============================================"
echo "  Desinstalacion completada"
echo "============================================"
echo ""
echo "  La base de datos NO fue eliminada."
echo "  Si reinstala, los datos se mantienen."
echo ""
echo "  Para eliminar la BD manualmente:"
echo "  sudo -u postgres psql -c 'DROP DATABASE agilize_gestion;'"
echo ""
