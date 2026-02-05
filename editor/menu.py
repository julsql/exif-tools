import platform
import threading
import tkinter as tk
from tkinter import messagebox

from detect_specie.main import find_specie
from editor.config_manager import ConfigManager
from editor.event_bus import EventBus
from editor.metadata_widget import get_coordinates
from editor.shared_data import StyleData


class MenuBar:
    OS_CTRL = 'Command' if platform.system() == 'Darwin' else 'Control'

    def __init__(self, root, reset_callback, open_image_callback, close_image_callback, recenter_callback, next_image, prev_image, reset_values, save, save_as, style_data: StyleData, event_bus: EventBus, config: ConfigManager):
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

        switch_map_label = self.style_data.MAPS_SWITCH_LABEL[self.config.get('map', self.style_data.DEFAULT_MAP)]
        switch_specie_recognition = self.style_data.SPECIE_SWITCH_LABEL[self.config.get('recognition', self.style_data.DEFAULT_SPECIE)]

        outils_menu.add_command(label=switch_map_label, command=self.switch_map)
        outils_menu.add_command(label=switch_specie_recognition, command=self.switch_specie_recognition)
        self.outils_menu = outils_menu
        menu_bar.add_cascade(label="Fenêtre", menu=outils_menu)

        # Menu Fichier
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Enregistrer", command=save, accelerator=self._format_accel("S"))
        file_menu.add_command(label="Enregistrer sous", command=save_as, accelerator=self._format_accel("Shift+S"))
        file_menu.add_command(label="Ouvrir une image", command=open_image_callback,
                              accelerator=self._format_accel("O"))
        file_menu.add_command(label="Fermer l'image", command=close_image_callback, accelerator=self._format_accel("W"))
        file_menu.add_command(label="Ajouter un marqueur centré", command=recenter_callback, accelerator=self._format_accel("D"))
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
        root.bind_all(f'<{self.OS_CTRL}-d>', recenter_callback)
        root.bind_all("<Left>", prev_image)
        root.bind_all("<Right>", next_image)
        root.bind_all(f'<{self.OS_CTRL}-r>', reset_callback)
        root.bind_all(f'<{self.OS_CTRL}-Shift-R>', reset_values)

    def _format_accel(self, keys):
        """Formate le raccourci selon l'OS"""
        return f"{self.OS_CTRL}+{keys}"

    def show_about(self):
        """Affiche une popup À propos"""
        messagebox.showinfo("À propos", "Éditeur Exif\nVersion 1.2.0\n© 2025 Jul SQL")

    def update(self):
        """Affiche une popup À propos"""
        messagebox.showinfo("Mise à jour", "Pour mettre à jour, téléchargez la nouvelle version sur GitHub.\n\n https://github.com/julsql/exif-tools/releases/latest\n\nSinon, modifiez le fichier install.sh avec la nouvelle version (Version 1.2.0) et lancez le script dans un terminal.")

    def switch_map(self):
        old_map_tiles = self.config.get('map', self.style_data.DEFAULT_MAP)
        if old_map_tiles == "french":
            self.config.set("map", "international")
        else:
            self.config.set("map", "french")
        self.event_bus.publish("map_updated")

        label = self.style_data.MAPS_SWITCH_LABEL[old_map_tiles]
        self.outils_menu.entryconfig(2, label=label)

    def switch_specie_recognition(self):
        recognition_activate = self.config.get('recognition', self.style_data.DEFAULT_SPECIE)
        if recognition_activate:
            self.config.set("recognition", False)
        else:
            self.config.set("recognition", True)

        label = self.style_data.SPECIE_SWITCH_LABEL[not recognition_activate]
        self.outils_menu.entryconfig(3, label=label)
        threading.Thread(target=self.event_bus.publish, args=("specie_recognition",)).start()
