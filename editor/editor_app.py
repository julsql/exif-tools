import os
import queue
import tkinter as tk
import webbrowser

import requests
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES

from detect_specie.inference_worker import InferenceWorker
from editor import resource_path
from editor.config_manager import ConfigManager
from editor.event_bus import EventBus
from editor.image_widget import ImageWidget
from editor.map_widget import MapWidget
from editor.menu import MenuBar
from editor.metadata_widget import MetadataWidget
from detect_specie.model_loader import ModelLoaderThread
from detect_specie.model_service import ModelService
from editor.shared_data import ImageData, StyleData, MetadataData


class ExifEditorApp:
    DEFAULT_HEIGHT = 800
    DEFAULT_WIDTH = 1200
    DEFAULT_GEOMETRY = f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}"

    DEFAULT_APP_TITLE = "Éditeur Exif"

    def __init__(self, root):
        self.root = root
        self.image_data = ImageData()
        self.metadata_data = MetadataData()
        self.style_data = StyleData()

        self.root.configure(bg=self.style_data.BG_COLOR)

        icon_path = resource_path("assets/icon.png")
        img = Image.open(icon_path)
        icon = ImageTk.PhotoImage(img)
        root.iconphoto(True, icon)

        self.config = ConfigManager()
        self.config.load()

        # Restauration de la géométrie de la fenêtre
        geometry = self.config.get("geometry")
        if geometry:
            root.geometry(geometry)
        else:
            root.geometry(self.DEFAULT_GEOMETRY)

        root.title(self.DEFAULT_APP_TITLE)

        self.main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg=self.style_data.BORDER_COLOR)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        self.event_bus = EventBus()

        self.left_pane = tk.PanedWindow(self.main_pane, orient=tk.VERTICAL, bg=self.style_data.BORDER_COLOR)
        self.main_pane.add(self.left_pane)
        self.right_pane = MapWidget(self.main_pane, self.event_bus, self.image_data, self.metadata_data,
                                    self.style_data, self.config)
        self.main_pane.add(self.right_pane)

        self.image_content = ImageWidget(self.left_pane, self.root, self.event_bus, self.image_data, self.metadata_data,
                                         self.style_data, self.right_pane)
        self.left_pane.add(self.image_content)

        self.metadata_content = MetadataWidget(self.left_pane, self.event_bus, self.image_data, self.metadata_data,
                                               self.style_data, self.config)
        self.left_pane.add(self.metadata_content)

        self.main_pane.bind("<Double-Button-1>", self.reset_main_split)
        self.left_pane.bind("<Double-Button-1>", self.reset_left_split)

        self.menu_bar = MenuBar(root,
                                self.reset_window,
                                self.image_content.open_file_dialog,
                                self.image_content.close_image,
                                self.right_pane.add_marker_center_of_map,
                                self.image_content.find_specie,
                                self.image_content.next_image,
                                self.image_content.prev_image,
                                self.metadata_content.reset_all,
                                self.image_content.save,
                                self.image_content.save_as,
                                self.style_data,
                                self.event_bus,
                                self.config)

        self.resize_after_id = None
        root.bind("<Configure>", self.on_resize)

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.image_content.drag_and_drop)

        self.root.bind_all("<Button-1>", self.clear_focus, add="+")

        self.event_bus.subscribe("image_open", self.image_open)
        self.event_bus.subscribe("image_close", self.image_close)
        self.event_bus.subscribe("specie_recognition", self.get_specie)

        root.after(100, self.restore_split)
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.model_queue = queue.Queue()
        self.model_service = ModelService()
        self.class_mapping = None
        self.transform = None

        # Lancer le chargement du modèle
        loader = ModelLoaderThread(self.model_service, self.model_queue)
        loader.start()

        # Démarrer l’écoute
        self.root.after(200, self.check_model_queue)

    def image_open(self, event):
        basename = os.path.basename(self.image_data.image_path)
        self.root.title(basename)

    def image_close(self, event):
        self.root.title(self.DEFAULT_APP_TITLE)

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

    def reset_window(self, event=None):
        self.root.geometry(self.DEFAULT_GEOMETRY)

        self.main_pane.sash_place(0, self.vertical_default_ratio(self.DEFAULT_WIDTH), 0)
        self.left_pane.sash_place(0, 0, self.horizontal_default_ratio(self.DEFAULT_HEIGHT))
        self.right_pane.reset_position(MapWidget.COORDINATES_PARIS, MapWidget.DEFAULT_ZOOM)

        # Supprime la config sauvegardée pour que ça redémarre proprement
        self.config.set("main_split", self.vertical_default_ratio())
        self.config.set("left_split", self.horizontal_default_ratio())
        self.config.set("geometry", self.DEFAULT_GEOMETRY)
        self.config.set("position", MapWidget.COORDINATES_PARIS)
        self.config.set("zoom", MapWidget.DEFAULT_ZOOM)
        self.config.save()

    def restore_split(self):
        main_x = self.config.get("main_split", self.vertical_default_ratio(self.DEFAULT_WIDTH))
        left_y = self.config.get("left_split", self.horizontal_default_ratio(self.DEFAULT_HEIGHT))

        self.left_pane.sash_place(0, 0, left_y)
        self.main_pane.sash_place(0, main_x, 0)

    def on_close(self):
        self.config.set("left_split", self.left_pane.sash_coord(0)[1])
        self.config.set("main_split", self.main_pane.sash_coord(0)[0])
        self.config.set("geometry", self.root.geometry())
        self.config.set("position", self.right_pane.map.get_position())
        self.config.set("zoom", self.right_pane.map.zoom)
        self.config.save()
        self.root.destroy()

    def clear_focus(self, event=None):
        widget = event.widget
        if not isinstance(widget, tk.Entry):
            self.root.focus_set()

    def vertical_default_ratio(self, total_width=None):
        if total_width is None:
            total_width = self.root.winfo_width()
        return total_width // 3

    def horizontal_default_ratio(self, total_height=None):
        if total_height is None:
            total_height = self.left_pane.winfo_height()
        return total_height // 2

    def get_specie(self, data):
        can_get_specie = self.config.get('recognition', self.style_data.DEFAULT_SPECIE)
        self.config.set("recognition", can_get_specie)
        if self.image_data.image_open and can_get_specie and not has_specie(self.metadata_data.entries['nom'].get()):
            latitude, longitude = (self.metadata_data.entries['latitude'].get(),
                                   self.metadata_data.entries['longitude'].get())

            worker = InferenceWorker(
                self.model_service,
                self.image_data.image_path,
                latitude,
                longitude,
                self.model_queue,
                self.class_mapping,
                self.transform
            )
            worker.start()

    def check_model_queue(self):
        while not self.model_queue.empty():
            event, payload = self.model_queue.get()

            if event == "model_ready":
                import birder

                self.class_mapping = {v: k for k, v in self.model_service.model_info.class_to_idx.items()}

                size = birder.get_size_from_signature(self.model_service.model_info.signature)
                self.transform = birder.classification_transform(
                    size, self.model_service.model_info.rgb_stats
                )

            elif event == "inference_done":
                self.on_specie_detected(payload)

        self.root.after(200, self.check_model_queue)

    def on_specie_detected(self, specie):
        if specie:
            url = get_inat_taxon_link(specie)
            self.show_species_popup(specie, url)

    def show_species_popup(self, specie, url):
        # Nouvelle fenêtre
        win = tk.Toplevel()
        win.configure(bg="white")
        win.title("Espèce détectée")
        if url is None:
            tk.Label(win, bg="white", fg="black", text=f"L'espèce {specie} a été reconnue.").pack(pady=10)
        else:
            # Message
            tk.Label(win, bg="white", fg="black",
                     text=f"L'espèce {specie} a été reconnue.\nCliquez sur le lien pour plus d'infos :").pack(pady=10)

            # Lien cliquable
            link = tk.Label(win, bg="white", text=url, fg="blue", cursor="hand2")
            link.pack()
            link.bind("<Button-1>", lambda e: webbrowser.open_new(url))

        # Boutons OK / Annuler
        def on_ok():
            entry = self.metadata_data.entries['nom']
            new_name = f"{specie} {entry.get()}"
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, new_name)
            entry.config(state="readonly")
            win.destroy()

        def on_cancel():
            win.destroy()

        btn_frame = tk.Frame(win, bg="white")
        btn_frame.pack(pady=10)

        btn_ok = tk.Label(btn_frame, bg="white", text="OK", fg="black", cursor="hand2")
        btn_ok.pack(side=tk.LEFT, padx=5)
        btn_ok.bind("<Button-1>", lambda e: on_ok())

        btn_cancel = tk.Label(btn_frame, bg="white", text="Annuler", fg="black", cursor="hand2")
        btn_cancel.pack(side=tk.LEFT, padx=5)
        btn_cancel.bind("<Button-1>", lambda e: on_cancel())


def has_specie(name):
    names = name.split(" ")
    return len(names) > 2 and names[0][0].isupper() and names[1][0].islower()


def get_inat_taxon_id(scientific_name):
    url = "https://api.inaturalist.org/v1/taxa"
    params = {"q": scientific_name, "rank": "species"}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    results = resp.json()["results"]
    if results:
        return results[0]["id"]
    return None


def get_inat_taxon_link(scientific_name):
    taxon_id = get_inat_taxon_id(scientific_name)
    if taxon_id:
        return f"https://www.inaturalist.org/taxa/{taxon_id}"
    return None
