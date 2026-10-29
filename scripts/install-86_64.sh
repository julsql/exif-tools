#!/bin/bash

set -e  # Stoppe le script en cas d'erreur
trap 'echo "❌ Une erreur est survenue. Installation interrompue."' ERR

echo "🚀 Lancement de l'installation de l'application (version arm64)..."

VERSION="2.0.6"
# Édition : "lite" (sans IA) ou "full" (reconnaissance d'espèce). Ex : EDITION=full ./install-86_64.sh
EDITION="${EDITION:-lite}"
if [[ "$EDITION" != "lite" && "$EDITION" != "full" ]]; then
  echo "❌ EDITION doit valoir 'lite' ou 'full' (reçu : $EDITION)"
  exit 1
fi

# === Variables personnalisables ===
APP_NAME="Éditeur Exif"
APP_COMMENT="Outil de gestion des métadonnées EXIF"

APP_DIR="$HOME/.exiftools"
EXEC_NAME="ExifTools-$VERSION-$EDITION-linux-x86_64"
EXEC_DEST_PATH="$HOME/.exiftools"
# Build PyInstaller "onedir" : exécutable + dossier _internal
APP_INSTALL_DIR="$APP_DIR/app"
APP_EXEC="$APP_INSTALL_DIR/ExifTools"
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
# Nettoyage d'une installation précédente (dont l'ancien exécutable seul)
rm -rf "$APP_INSTALL_DIR"
if [[ -f "$APP_DIR/ExifTools" ]]; then
  rm "$APP_DIR/ExifTools"
fi
mv "$EXEC_DEST_PATH/$EXEC_NAME/ExifTools" "$APP_INSTALL_DIR"
chmod +x "$APP_EXEC"

# === Téléchargement du modèle ===
if [[ "$EDITION" == "lite" ]]; then
  echo "⏭️ Édition lite : pas de modèle à télécharger"
elif [[ ! -f "$MODEL_PATH" ]]; then
  echo "⬇️ Téléchargement du modèle iNaturalist (peut prendre du temps)..."
  wget -O "$MODEL_PATH" "$MODEL_URL"
else
  echo "✅ Modèle déjà présent"
fi

# === Déplacement de l'icône ===
echo "🖼️ Téléchargement de l'icône vers $ICON_DEST_PATH"
mv "$EXEC_DEST_PATH/$EXEC_NAME/exiftools.png" "$ICON_DEST_PATH"

rm "$EXEC_DEST_PATH/$EXEC_NAME.tar.gz"
rmdir "$EXEC_DEST_PATH/$EXEC_NAME"

# === Création du fichier .desktop ===
echo "📝 Création du fichier .desktop pour l'application..."
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=$APP_NAME
Comment=$APP_COMMENT
Exec=$APP_EXEC
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
