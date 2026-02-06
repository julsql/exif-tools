# python
import re
import sys

import requests
from packaging import version
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox

from editor import resource_path
from editor.main_window import MainWindow

VERSION = "1.2.0"
GITHUB_REPO = "julsql/exif-tools"


def check_update_qt(parent=None) -> None:
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        latest_release = response.json()
        latest_version = latest_release["tag_name"].lstrip("v")
        changelog = re.sub(
            r" \([0-9a-f]{40}( & [0-9a-f]{40})*\)",
            "",
            (latest_release.get("body", "") or ""),
        )

        if version.parse(latest_version) > version.parse(VERSION):
            QMessageBox.information(
                parent,
                "Mise à jour disponible",
                "Une nouvelle version est disponible.\n\n" + changelog,
            )

    except requests.RequestException as e:
        print(f"Erreur lors de la vérification de mise à jour : {e}")


def main_qt() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("ExifTools")

    icon_path = resource_path("assets/icon.png")
    app.setWindowIcon(QIcon(icon_path))

    win = MainWindow(app)
    win.show()

    check_update_qt(win)

    raise SystemExit(app.exec())
