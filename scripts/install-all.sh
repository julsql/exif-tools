#!/bin/bash

set -e  # Stoppe le script en cas d'erreur
trap 'echo "❌ Une erreur est survenue. Installation interrompue."' ERR

VERSION="2.0.5"

# === Config personnalisable ===
APP_NAME="Éditeur Exif"
APP_COMMENT="Outil de gestion des métadonnées EXIF"

APP_DIR="$HOME/.exiftools"
APP_FOLDER="$PWD/exif-tools-$VERSION"
APP_REPO_URL="https://github.com/julsql/exif-tools/archive/refs/tags/$VERSION.zip"
EXEC_SRC_PATH="$APP_FOLDER/dist/ExifTools"
EXEC_DEST_PATH="$APP_DIR/ExifTools"
ICON_SRC_PATH="https://raw.githubusercontent.com/julsql/exif-tools/$VERSION/assets/icon.png"
ICON_DEST_PATH="$HOME/.local/share/icons/exiftools.png"
DESKTOP_FILE="$HOME/.local/share/applications/exiftools.desktop"
MODEL_DIR="$APP_DIR/models"
MODEL_NAME="vit_reg4_m16_rms_avg_i-jepa-inat21.pt"
MODEL_PATH="$MODEL_DIR/$MODEL_NAME"
MODEL_URL="https://huggingface.co/birder-project/vit_reg4_m16_rms_avg_i-jepa-inat21/resolve/main/vit_reg4_m16_rms_avg_i-jepa-inat21.pt?download=true"

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

if [ -n "$APP_FOLDER" ] \
   && [ "$APP_FOLDER" != "/" ] \
   && [ "$APP_FOLDER" != "." ] \
   && [ "$APP_FOLDER" != "./" ] \
   && [ -d "$APP_FOLDER" ]; then
  rm -rf "$APP_FOLDER"
fi

if [ -n "$EXEC_DEST_PATH" ] \
   && [ "$EXEC_DEST_PATH" != "/" ] \
   && [ "$EXEC_DEST_PATH" != "." ] \
   && [ "$EXEC_DEST_PATH" != "./" ] \
   && [ -d "$EXEC_DEST_PATH" ]; then
    rm -rf "$EXEC_DEST_PATH"
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
pyinstaller --noconfirm --clean ExifTools.spec

echo "🔚 Désactivation de l'environnement virtuel..."
deactivate

# === Création des dossiers ===
echo "📁 Création des dossiers nécessaires..."
mkdir -p "$APP_DIR"
mkdir -p "$MODEL_DIR"
mkdir -p "$HOME/.local/share/icons"
mkdir -p "$HOME/.local/share/applications"

# === Téléchargement du modèle ===
if [[ ! -f "$MODEL_PATH" ]]; then
  echo "⬇️ Téléchargement du modèle iNaturalist (peut prendre du temps)..."
  wget -O "$MODEL_PATH" "$MODEL_URL"
else
  echo "✅ Modèle déjà présent"
fi

# === Copie de l'exécutable ===
echo "📄 Copie de l'exécutable vers $EXEC_DEST_PATH"
cp -r "$EXEC_SRC_PATH" "$EXEC_DEST_PATH"
chmod +x "$EXEC_DEST_PATH/ExifTools"

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
cd ~
rm -rf "$APP_FOLDER"

echo "✅🎉 Installation terminée avec succès !"
echo "➡ Tu peux maintenant lancer '$APP_NAME' depuis ton menu d'applications."
