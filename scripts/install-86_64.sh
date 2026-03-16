#!/bin/bash

set -e  # Stoppe le script en cas d'erreur
trap 'echo "❌ Une erreur est survenue. Installation interrompue."' ERR

echo "🚀 Lancement de l'installation de l'application (version arm64)..."

VERSION="2.0.4"

# === Variables personnalisables ===
APP_NAME="Éditeur Exif"
APP_COMMENT="Outil de gestion des métadonnées EXIF"

APP_DIR="$HOME/.exiftools"
EXEC_NAME="ExifTools-$VERSION-linux-x86_64"
EXEC_DEST_PATH="$HOME/.exiftools"
EXEC_SRC_PATH="https://github.com/julsql/exif-tools/releases/download/$VERSION/$EXEC_NAME.tar.gz"
ICON_DEST_PATH="$HOME/.local/share/icons/exiftools.png"
DESKTOP_FILE="$HOME/.local/share/applications/exiftools.desktop"
MODEL_DIR="$APP_DIR/models"
MODEL_NAME="vit_reg4_m16_rms_avg_i-jepa-inat21.pt"
MODEL_PATH="$MODEL_DIR/$MODEL_NAME"
MODEL_URL="https://huggingface.co/birder-project/vit_reg4_m16_rms_avg_i-jepa-inat21/resolve/main/vit_reg4_m16_rms_avg_i-jepa-inat21.pt?download=true"

# === Création des dossiers nécessaires ===
echo "📁 Création des dossiers nécessaires..."
mkdir -p "$APP_DIR"
mkdir -p "$MODEL_DIR"
mkdir -p "$HOME/.local/share/icons"
mkdir -p "$HOME/.local/share/applications"
mkdir -p "$EXEC_DEST_PATH"
mkdir -p "$EXEC_DEST_PATH/$EXEC_NAME"

# === Téléchargement de l'exécutable ===
echo "⬇️ Téléchargement de l'exécutable vers $EXEC_DEST_PATH"
wget -O "$EXEC_DEST_PATH/$EXEC_NAME.tar.gz" "$EXEC_SRC_PATH"
tar -xf "$EXEC_DEST_PATH/$EXEC_NAME.tar.gz" -C "$EXEC_DEST_PATH/$EXEC_NAME"
mv "$EXEC_DEST_PATH/$EXEC_NAME/ExifTools/ExifTools" "$APP_DIR/ExifTools"
chmod +x "$APP_DIR/ExifTools"

# === Téléchargement du modèle ===
if [[ ! -f "$MODEL_PATH" ]]; then
  echo "⬇️ Téléchargement du modèle iNaturalist (peut prendre du temps)..."
  wget -O "$MODEL_PATH" "$MODEL_URL"
else
  echo "✅ Modèle déjà présent"
fi

# === Déplacement de l'icône ===
echo "🖼️ Téléchargement de l'icône vers $ICON_DEST_PATH"
mv "$EXEC_DEST_PATH/$EXEC_NAME/exiftools.png" "$ICON_DEST_PATH"

rm "$EXEC_DEST_PATH/$EXEC_NAME.tar.gz"
rmdir "$EXEC_DEST_PATH/$EXEC_NAME/ExifTools"
rmdir "$EXEC_DEST_PATH/$EXEC_NAME"

# === Création du fichier .desktop ===
echo "📝 Création du fichier .desktop pour l'application..."
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=$APP_NAME
Comment=$APP_COMMENT
Exec=$EXEC_DEST_PATH
Icon=$ICON_DEST_PATH
Terminal=false
Type=Application
Categories=Utility;
EOF

# === Rafraîchissement du menu d'applications ===
echo "🔁 Mise à jour du menu d'applications..."
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo "✅🎉 Installation terminée avec succès !"
echo "➡ Tu peux maintenant lancer '$APP_NAME' depuis ton menu d'applications."
