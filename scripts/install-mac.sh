#!/bin/bash

set -e  # Stoppe le script en cas d'erreur
trap 'echo "❌ Une erreur est survenue. Installation interrompue."' ERR

VERSION="2.0.4"

# === Config personnalisable ===
APP_NAME="Éditeur Exif"

APP_DIR="$HOME/.exiftools"
PYTHON="/usr/local/bin/python3.9"
APP_FOLDER="$PWD/exif-tools-$VERSION"
APP_REPO_URL="https://github.com/julsql/exif-tools/archive/refs/tags/$VERSION.zip"
EXEC_SRC_PATH="$APP_FOLDER/dist/ExifTools.app"
EXEC_DEST_PATH="/Applications/ExifTools.app"
ICON_SRC_PATH="https://raw.githubusercontent.com/julsql/exif-tools/$VERSION/assets/icon.icns"
ICON_DEST_PATH="$EXEC_DEST_PATH/Contents/Resources/icon-windowed.icns"
MODEL_DIR="$APP_DIR/models"
MODEL_NAME="vit_reg4_m16_rms_avg_i-jepa-inat21.pt"
MODEL_PATH="$MODEL_DIR/$MODEL_NAME"
MODEL_URL="https://huggingface.co/birder-project/vit_reg4_m16_rms_avg_i-jepa-inat21/resolve/main/vit_reg4_m16_rms_avg_i-jepa-inat21.pt?download=true"

echo "📦 Installation de python3.9..."
brew install python@3.9

echo "⬇️ Clonage du dépôt exif-tools..."
if [[ -f "./$VERSION.zip" ]]; then
  rm "./$VERSION.zip"
fi

if [[ -d "$APP_FOLDER" ]]; then
  rm -rf "$APP_FOLDER"
fi
curl -L -o ./$VERSION.zip $APP_REPO_URL
unzip "./$VERSION.zip"
rm "./$VERSION.zip"
cd "$APP_FOLDER"

echo "🐍 Création de l'environnement virtuel Python..."
$PYTHON -m venv venv

echo "✅ Activation de l'environnement virtuel..."
source venv/bin/activate

echo "📦 Installation des dépendances..."
pip install -r requirements.txt
pip install pyinstaller

echo "⚙️ Compilation de l'application avec PyInstaller..."
pyinstaller --noconfirm --clean ExifTools.spec

echo "🔚 Désactivation de l'environnement virtuel..."
deactivate

# === Création des dossiers ===
echo "📁 Création des dossiers nécessaires..."
mkdir -p "$APP_DIR"
mkdir -p "$MODEL_DIR"

# === Téléchargement du modèle ===
if [[ ! -f "$MODEL_PATH" ]]; then
  echo "⬇️ Téléchargement du modèle iNaturalist (peut prendre du temps)..."
  wget -O "$MODEL_PATH" "$MODEL_URL"
else
  echo "✅ Modèle déjà présent"
fi

# === Copie de l'app ===
echo "📄 Copie de l'app vers $EXEC_DEST_PATH"
cp -r "$EXEC_SRC_PATH" "$EXEC_DEST_PATH"

# === Téléchargement de l'icône ===
echo "🖼️ Téléchargement de l'icône..."
curl -L -o "$ICON_DEST_PATH" "$ICON_SRC_PATH"

# === Nettoyage ===
echo "🧹 Nettoyage du dépôt temporaire..."
cd ~
rm -rf "$APP_FOLDER"

echo "✅🎉 Installation terminée avec succès !"
echo "➡ Tu peux maintenant lancer '$APP_NAME' depuis ton menu d'applications."
