#!/bin/bash

set -e  # Stoppe le script en cas d'erreur
trap 'echo "❌ Une erreur est survenue. Installation interrompue."' ERR

# === Config personnalisable ===
APP_NAME="Éditeur Exif"
APP_COMMENT="Outil de gestion des métadonnées EXIF"
VERSION="1.0.0"
APP_DIR="$HOME/.exiftools"
APP_FOLDER="$(realpath ./exif-tools-$VERSION)"
APP_REPO_URL="https://github.com/julsql/exif-tools/archive/refs/tags/$VERSION.zip"
EXEC_SRC_PATH="$APP_FOLDER/dist/ExifTools"
EXEC_DEST_PATH="$APP_DIR/ExifTools"
ICON_SRC_PATH="https://github.com/julsql/exif-tools/releases/download/$VERSION/icon.png"
ICON_DEST_PATH="$HOME/.local/share/icons/exiftools.png"
DESKTOP_FILE="$HOME/.local/share/applications/exiftools.desktop"

echo "🔄 Mise à jour des paquets..."
sudo apt update

echo "📦 Installation de python3-pip..."
sudo apt install python3-pip -y

echo "📦 Installation de python3-venv..."
sudo apt install python3-venv -y

echo "📦 (Double vérification) Installation de python3-venv..."
sudo apt install python3-venv -y

echo "📦 Installation de python3-tk..."
sudo apt install python3-tk -y

echo "⬇️ Clonage du dépôt exif-tools..."
if [[ -f "./$VERSION.zip" ]]; then
  rm "./$VERSION.zip"
fi

if [[ -d "$APP_FOLDER" ]]; then
  rm -rf "$APP_FOLDER"
fi
wget $APP_REPO_URL
unzip "./$VERSION.zip"
rm "./$VERSION.zip"
cd "$APP_FOLDER"

echo "🐍 Création de l'environnement virtuel Python..."
python3 -m venv venv

echo "✅ Activation de l'environnement virtuel..."
source venv/bin/activate

echo "📦 Installation des dépendances..."
pip install -r requirements.txt
pip install pyinstaller

echo "⚙️ Compilation de l'application avec PyInstaller..."
pyinstaller --onefile --windowed --name "ExifTools" --hidden-import=piexif --hidden-import=PIL._tkinter_finder --add-data "assets:assets" main.py

echo "🔚 Désactivation de l'environnement virtuel..."
deactivate

# === Création des dossiers ===
echo "📁 Création des dossiers nécessaires..."
mkdir -p "$APP_DIR"
mkdir -p "$HOME/.local/share/icons"
mkdir -p "$HOME/.local/share/applications"

# === Copie de l'exécutable ===
echo "📄 Copie de l'exécutable vers $EXEC_DEST_PATH"
cp "$EXEC_SRC_PATH" "$EXEC_DEST_PATH"
chmod +x "$EXEC_DEST_PATH"

# === Téléchargement de l'icône ===
echo "🖼️ Téléchargement de l'icône..."
wget -O "$ICON_DEST_PATH" "$ICON_SRC_PATH"

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
Categories=Utility;Graphics;Photography;
StartupWMClass=$APP_NAME
EOF

# === Rafraîchir les applications ===
echo "🔁 Mise à jour du menu d'applications..."
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

# === Nettoyage ===
echo "🧹 Nettoyage du dépôt temporaire..."
cd ..
rm -rf "$APP_FOLDER"

echo "✅🎉 Installation terminée avec succès !"
echo "➡ Tu peux maintenant lancer '$APP_NAME' depuis ton menu d'applications."
