import tkinter as tk
import platform


class MenuBar:
    OS_CTRL = 'Command' if platform.system() == 'Darwin' else 'Control'

    def __init__(self, root, reset_callback, open_image_callback, close_image_callback, reset_values, save, save_as):
        self.root = root

        # Barre de menus
        menu_bar = tk.Menu(root)

        # Menu Outils
        outils_menu = tk.Menu(menu_bar, tearoff=0)
        outils_menu.add_command(label="Réinitialiser la fenêtre", command=reset_callback, accelerator=self._format_accel("R"))
        outils_menu.add_command(label="Réinitialiser les valeurs", command=reset_values, accelerator=self._format_accel("Shift+R"))
        menu_bar.add_cascade(label="Fenêtre", menu=outils_menu)

        # Menu Fichier
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Enregistrer", command=save, accelerator=self._format_accel("S"))
        file_menu.add_command(label="Enregistrer sous", command=save_as, accelerator=self._format_accel("Shift+S"))
        file_menu.add_command(label="Ouvrir une image", command=open_image_callback, accelerator=self._format_accel("O"))
        file_menu.add_command(label="Fermer l'image", command=close_image_callback, accelerator=self._format_accel("W"))
        menu_bar.add_cascade(label="Fichier", menu=file_menu)

        # Ajouter la barre de menu à la fenêtre principale
        root.config(menu=menu_bar)

        root.bind_all(f'<{self.OS_CTRL}-s>', save)
        root.bind_all(f'<{self.OS_CTRL}-Shift-S>', save_as)
        root.bind_all(f'<{self.OS_CTRL}-o>', open_image_callback)
        root.bind_all(f'<{self.OS_CTRL}-w>', close_image_callback)
        root.bind_all(f'<{self.OS_CTRL}-r>', reset_callback)
        root.bind_all(f'<{self.OS_CTRL}-Shift-R>', reset_values)

    def _format_accel(self, keys):
        """Formate le raccourci selon l'OS"""
        return f"{self.OS_CTRL}+{keys}"
