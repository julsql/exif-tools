# Exif tools

Version : 1.0.9

Application pour visualiser et modifier les exif d'un photo.

- Ouvrir la photo et la visualiser
- Visualiser ses métadonnées (nom, format, poids, dimensions, date de prise de vue/modification, coordonnées gps)
- Modifier les métadonnées : Date de création et coordonnées géographiques
- Visualiser les coordonnées sur une carte (uniquement en ligne)
- Modifier les coordonnées via la carte

Pour lancer l'application, lancer dans un terminal :

```bash
pip install -r requirements.txt
python3 main.py
```

Pour incrémenter de version, modifier le fichier `version.txt`et lancer

```shell
python3 bump_version.py
```

## Build l'application pour la déployer

### Faire l'exécutable linux

Dans une machine linux (ou VM)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "ExifTools" --hidden-import=piexif --hidden-import=PIL._tkinter_finder --add-data "assets:assets" main.py
```

### Faire l'application linux

Armature 64

```bash
chmod +x ./install-arm64.sh
./install-arm64.sh
```

Autre

```bash
chmod +x ./install-all.sh
./install-all.sh
```

Désinstaller

```bash
chmod +x ./uninstall.sh
./uninstall.sh
```
