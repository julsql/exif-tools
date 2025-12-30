import platform
import tkinter as tk
from tkinter import messagebox

from editor.config_manager import ConfigManager
from editor.event_bus import EventBus
from editor.shared_data import StyleData


class MenuBar:
    OS_CTRL = 'Command' if platform.system() == 'Darwin' else 'Control'

    def __init__(self, root, reset_callback, open_image_callback, close_image_callback, next_image, prev_image, reset_values, save, save_as, style_data: StyleData, event_bus: EventBus, config: ConfigManager):
        self.root = root
        self.style_data = style_data
        self.event_bus = event_bus
        self.config = config

        # Barre de menus
        menu_bar = tk.Menu(root)

        # Menu Outils
        outils_menu = tk.Menu(menu_bar, tearoff=0)
        outils_menu.add_command(label="Réinitialiser la fenêtre", command=reset_callback,
                                accelerator=self._format_accel("R"))
        outils_menu.add_command(label="Réinitialiser les valeurs", command=reset_values,
                                accelerator=self._format_accel("Shift+R"))

        if self.config.get('map', self.style_data.DEFAULT_MAP) == self.style_data.DEFAULT_MAP:
            switch_map_label = "Utiliser une carte internationale"
        else:
            switch_map_label = "Utiliser une carte française"

        outils_menu.add_command(label=switch_map_label, command=self.switch_map)
        self.outils_menu = outils_menu
        menu_bar.add_cascade(label="Fenêtre", menu=outils_menu)

        # Menu Fichier
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Enregistrer", command=save, accelerator=self._format_accel("S"))
        file_menu.add_command(label="Enregistrer sous", command=save_as, accelerator=self._format_accel("Shift+S"))
        file_menu.add_command(label="Ouvrir une image", command=open_image_callback,
                              accelerator=self._format_accel("O"))
        file_menu.add_command(label="Fermer l'image", command=close_image_callback, accelerator=self._format_accel("W"))
        file_menu.add_command(label="Image suivante", command=next_image, accelerator="Right")
        file_menu.add_command(label="Image précédente", command=prev_image, accelerator="Left")
        menu_bar.add_cascade(label="Fichier", menu=file_menu)

        # Menu Aide
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="À propos", command=self.show_about)
        help_menu.add_command(label="Mettre à jour", command=self.update)
        menu_bar.add_cascade(label="Aide", menu=help_menu)

        # Ajouter la barre de menu à la fenêtre principale
        root.config(menu=menu_bar)

        root.bind_all(f'<{self.OS_CTRL}-s>', save)
        root.bind_all(f'<{self.OS_CTRL}-Shift-S>', save_as)
        root.bind_all(f'<{self.OS_CTRL}-o>', open_image_callback)
        root.bind_all(f'<{self.OS_CTRL}-w>', close_image_callback)
        root.bind_all("<Left>", prev_image)
        root.bind_all("<Right>", next_image)
        root.bind_all(f'<{self.OS_CTRL}-r>', reset_callback)
        root.bind_all(f'<{self.OS_CTRL}-Shift-R>', reset_values)

    def _format_accel(self, keys):
        """Formate le raccourci selon l'OS"""
        return f"{self.OS_CTRL}+{keys}"

    def show_about(self):
        """Affiche une popup À propos"""
        messagebox.showinfo("À propos", "Éditeur Exif\nVersion 1.1.1\n© 2025 Jul SQL")

    def update(self):
        """Affiche une popup À propos"""
        messagebox.showinfo("Mise à jour", "Pour mettre à jour, téléchargez la nouvelle version sur GitHub.\n\n https://github.com/julsql/exif-tools/releases/latest\n\nSinon, modifiez le fichier install.sh avec la nouvelle version (Version 1.1.1) et lancez le script dans un terminal.")

    def switch_map(self):
        old_map_tiles = self.config.get('map', self.style_data.DEFAULT_MAP)
        print(old_map_tiles)
        if old_map_tiles == "french":
            self.config.set("map", "international")
        else:
            self.config.set("map", "french")
        self.event_bus.publish("metadata_updated", "update-map")

        label = self.style_data.MAPS_SWITCH_LABEL[old_map_tiles]
        self.outils_menu.entryconfig(2, label=label)
