import tkinter as tk
from tkinter import PhotoImage

from editor.config_manager import ConfigManager
from editor.image_widget import ImageWidget
from editor.menu import MenuBar
from editor.metadata_widget import MetadataWidget
from editor.shared_data import ImageData, StyleData, MetadataData


class ExifEditorApp:
    def __init__(self, root):
        self.default_height = 800
        self.default_width = 1200
        self.default_geometry = f"{self.default_width}x{self.default_height}"

        self.root = root
        icon = PhotoImage(file="./assets/icon.png")

        root.iconphoto(True, icon)

        self.config = ConfigManager()
        self.config.load()

        # Restauration de la géométrie de la fenêtre
        geometry = self.config.get("geometry")
        if geometry:
            root.geometry(geometry)
        else:
            root.geometry(self.default_geometry)

        root.title("Éditeur Exif")

        self.main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        self.image_data = ImageData()
        self.metadata_data = MetadataData()
        self.style_data = StyleData()

        self.left_pane = tk.PanedWindow(self.main_pane, orient=tk.VERTICAL)
        self.main_pane.add(self.left_pane)

        self.image_content = ImageWidget(self.left_pane, self.image_data, self.metadata_data, self.style_data)
        self.left_pane.add(self.image_content)

        self.metadata_content = MetadataWidget(self.left_pane, self.image_data, self.metadata_data, self.style_data)
        self.left_pane.add(self.metadata_content)

        self.right = tk.Frame(self.main_pane, bg="lightgray")
        self.main_pane.add(self.right)

        self.main_pane.bind("<Double-Button-1>", self.reset_main_split)
        self.left_pane.bind("<Double-Button-1>", self.reset_left_split)

        tk.Label(self.right, text="Carte").pack(padx=10, pady=10)

        self.menu_bar = MenuBar(root,
                                self.reset_window,
                                self.image_content.open_file_dialog,
                                self.image_content.close_image,
                                self.metadata_content.reset_all)

        self.resize_after_id = None
        root.bind("<Configure>", self.on_resize)

        root.after(100, self.restore_split)
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def reset_main_split(self, event):
        self.main_pane.sash_place(0, self.vertical_default_ratio(), 0)

    def on_resize(self, event):
        if self.resize_after_id is not None:
            self.root.after_cancel(self.resize_after_id)

        self.resize_after_id = self.root.after(10, self.handle_resize)

    def handle_resize(self):
        self.image_content.reset_image()

    def reset_left_split(self, event):
        self.left_pane.sash_place(0, 0, self.horizontal_default_ratio())

    def reset_window(self):
        self.root.geometry(self.default_geometry)

        self.main_pane.sash_place(0, self.vertical_default_ratio(self.default_width), 0)
        self.left_pane.sash_place(0, 0, self.horizontal_default_ratio(self.default_height))

        # Supprime la config sauvegardée pour que ça redémarre proprement
        self.config.set("main_split", self.vertical_default_ratio())
        self.config.set("left_split", self.horizontal_default_ratio())
        self.config.set("geometry", self.default_geometry)
        self.config.save()

    def restore_split(self):
        main_x = self.config.get("main_split", self.vertical_default_ratio(self.default_width))
        left_y = self.config.get("left_split", self.horizontal_default_ratio(self.default_height))

        self.left_pane.sash_place(0, 0, left_y)
        self.main_pane.sash_place(0, main_x, 0)

    def on_close(self):
        self.config.set("left_split", self.left_pane.sash_coord(0)[1])
        self.config.set("main_split", self.main_pane.sash_coord(0)[0])
        self.config.set("geometry", self.root.geometry())
        self.config.save()
        self.root.destroy()

    def vertical_default_ratio(self, total_width=None):
        if total_width is None:
            total_width = self.root.winfo_width()
        return total_width // 3

    def horizontal_default_ratio(self, total_height=None):
        if total_height is None:
            total_height = self.left_pane.winfo_height()
        return total_height // 2
