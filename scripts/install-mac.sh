#!/bin/bash

set -e  # Stoppe le script en cas d'erreur
trap 'echo "❌ Une erreur est survenue. Installation interrompue."' ERR

# === Config personnalisable ===
APP_NAME="Éditeur Exif"

VERSION="1.0.9"

PYTHON="/usr/local/bin/python3.9"
APP_FOLDER="$PWD/exif-tools-$VERSION"
APP_REPO_URL="https://github.com/julsql/exif-tools/archive/refs/tags/$VERSION.zip"
EXEC_SRC_PATH="$APP_FOLDER/dist/ExifTools.app"
EXEC_DEST_PATH="/Applications/ExifTools.app"
ICON_SRC_PATH="https://raw.githubusercontent.com/julsql/exif-tools/$VERSION/assets/icon.icns"
ICON_DEST_PATH="$EXEC_DEST_PATH/Contents/Resources/icon-windowed.icns"

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
pyinstaller --clean --onefile --windowed --name "ExifTools" --hidden-import=piexif --hidden-import=PIL._tkinter_finder --add-data "assets:assets" main.py

echo "🔚 Désactivation de l'environnement virtuel..."
deactivate

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
