#!/bin/bash

set -e  # Stoppe le script en cas d'erreur
trap 'echo "❌ Une erreur est survenue pendant la désinstallation."' ERR

echo "🗑️ Lancement de la désinstallation de l'application ExifTools..."

APP_DIR="$HOME/.exiftools"
EXEC_DEST_PATH="$APP_DIR/ExifTools"
CONFIG_DEST_PATH="$APP_DIR/window_config.json"
ICON_DEST_PATH="$HOME/.local/share/icons/exiftools.png"
DESKTOP_FILE="$HOME/.local/share/applications/exiftools.desktop"

# === Suppression du fichier .desktop ===
if [[ -f "$DESKTOP_FILE" ]]; then
  echo "🧽 Suppression du raccourci d'application..."
  rm "$DESKTOP_FILE"
else
  echo "ℹ️ Aucun fichier .desktop trouvé."
fi

# === Suppression de l'icône ===
if [[ -f "$ICON_DEST_PATH" ]]; then
  echo "🧽 Suppression de l'icône..."
  rm "$ICON_DEST_PATH"
else
  echo "ℹ️ Aucune icône trouvée."
fi

# === Suppression de l'exécutable ===
if [[ -f "$EXEC_DEST_PATH" ]]; then
  echo "🧽 Suppression de l'exécutable..."
  rm "$EXEC_DEST_PATH"
else
  echo "ℹ️ Aucun exécutable trouvé."
fi

# === Suppression de la configuration ===
if [[ -f "$CONFIG_DEST_PATH" ]]; then
  echo "🧽 Suppression de la configuration..."
  rm "$CONFIG_DEST_PATH"
else
  echo "ℹ️ Aucune configuration trouvée."
fi

# === Suppression du dossier exiftools s’il est vide ===
if [[ -d "$APP_DIR" && -z "$(ls -A "$APP_DIR")" ]]; then
  echo "🧹 Dossier '$APP_DIR' vide, suppression..."
  rmdir "$APP_DIR"
fi

# === Mise à jour du menu d'applications ===
echo "🔁 Mise à jour du menu d'applications..."
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo "✅ Désinstallation terminée avec succès."
