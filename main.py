import requests
from tkinter import messagebox

from tkinterdnd2 import TkinterDnD

from editor.editor_app import ExifEditorApp

VERSION = '1.0.1'
GITHUB_REPO = "julsql/exif-tools"

def check_update():
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        latest_release = response.json()
        latest_version = latest_release['tag_name'].lstrip('v')

        if latest_version != VERSION:
            messagebox.showinfo(
                "Mise à jour disponible",
                f"Une nouvelle version {latest_version} est disponible."
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
