import re
from tkinter import messagebox

import requests
from packaging import version
from tkinterdnd2 import TkinterDnD

from editor.editor_app import ExifEditorApp

VERSION = '1.1.1'
GITHUB_REPO = "julsql/exif-tools"


def check_update():
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        latest_release = response.json()
        latest_version = latest_release['tag_name'].lstrip('v')
        changelog = re.sub(r" \([0-9a-f]{40}( & [0-9a-f]{40})*\)", "", latest_release['body'])

        if version.parse(latest_version) > version.parse(VERSION):
            messagebox.showinfo(
                "Mise à jour disponible",
                "Une nouvelle version est disponible.\n\n" +
                changelog
            )

    except requests.RequestException as e:
        print(f"Erreur lors de la vérification de mise à jour : {e}")


def main():
    check_update()

    root = TkinterDnD.Tk()
    ExifEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
