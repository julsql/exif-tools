import threading
import tkinter as tk
from tkinter import messagebox

import tkintermapview
from PIL import Image, ImageTk

from detect_specie.main import find_specie
from editor import resource_path
from editor.config_manager import ConfigManager
from editor.metadata_widget import get_coordinates
from editor.shared_data import MetadataData, StyleData, ImageData
from editor.utils import has_specie


class MapWidget(tk.Frame):
    COORDINATES_PARIS = (48.8566, 2.3522)
    DEFAULT_ZOOM = 5

    def __init__(self, parent, event_bus, image_data: ImageData,
                 metadata_data: MetadataData, style_data: StyleData, config: ConfigManager):
        super().__init__(parent)
        self._origin_after_id = None

        self.event_bus = event_bus
        self.image_data = image_data
        self.metadata_data = metadata_data
        self.style_data = style_data
        self.config = config
        self.parent = parent

        position = self.config.get('position', self.COORDINATES_PARIS)
        zoom = self.config.get('zoom', self.DEFAULT_ZOOM)

        self.red_icon = self.load_icon("assets/marker-red.png")
        self.blue_icon = self.load_icon("assets/marker-blue.png")

        self.map = tkintermapview.TkinterMapView(self, width=800, height=600)

        self.set_map_tiles()

        self.map.pack(fill="both", expand=True)

        self.reset_position(position, zoom)

        self.origin_marker = None
        self.new_marker = None

        self.map.canvas.bind("<Button-3>", self._on_right_click)
        self.map.canvas.bind("<Button-2>", self._on_right_click)

        self.event_bus.subscribe("metadata_updated", self.update_origin)
        self.event_bus.subscribe("metadata_saved", self.saved)

    def load_icon(self, filename, size=None):
        img = Image.open(resource_path(filename))
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def set_map_tiles(self):
        map_tiles = self.config.get('map', self.style_data.DEFAULT_MAP)
        self.map.set_tile_server(self.style_data.MAPS[map_tiles])

    def reset_position(self, position, zoom):
        """Reset la position et le zoom de la carte."""
        self.map.set_position(*position)
        self.map.set_zoom(zoom)

    def delete_markers(self):
        """Supprimer tous les marqueurs."""
        if self.origin_marker:
            try:
                self.origin_marker.delete()
            except Exception:
                pass
            self.origin_marker = None

        if self.new_marker:
            try:
                self.new_marker.delete()
            except Exception:
                pass
            self.new_marker = None

    def update_origin(self, publisher):
        """Évite le spam"""
        if self._origin_after_id:
            self.after_cancel(self._origin_after_id)

        self._origin_after_id = self.after(50, lambda: self._update_origin(publisher))

    def saved(self, data):
        if len(data) == 2:
            self.map.set_position(*data)

    def _update_origin(self, publisher):
        """Met à jour les marqueurs selon l'événement reçu."""
        if publisher == "open":
            coords = self.get_coordinates()
            self.add_origin_marker_event(coords)

        elif publisher == "close":
            self.delete_markers()

        elif publisher == "edit":
            coords = self.get_coordinates()
            self.add_marker_event(coords, coords == get_coordinates(self.image_data.pil_image))

        elif publisher == "update-map":
            self.set_map_tiles()

    def get_coordinates(self):
        """Récupère les coordonnées à partir des champs de métadonnées."""
        try:
            latitude = float(self.metadata_data.entries["latitude"].get())
            longitude = float(self.metadata_data.entries["longitude"].get())
        except ValueError:
            return None
        return latitude, longitude

    def add_origin_marker_event(self, coords):
        """Ajoute un marqueur à l'emplacement donné sur la carte."""
        self.delete_markers()
        self.update_idletasks()

        if coords:
            self.map.set_position(*coords)
            self.origin_marker = self.map.set_marker(coords[0], coords[1], text="Origine", icon=self.red_icon)

    def _on_right_click(self, event):
        x, y = event.x, event.y

        coords = self.map.convert_canvas_coords_to_decimal_coords(x, y)
        if not coords:
            return

        self.add_marker_event(coords)
        return "break"

    def add_marker_event(self, coords, origin=False):
        """Ajoute un marqueur à l'emplacement donné sur la carte."""

        if origin and self.new_marker:
            # Le marqueur d'origine change
            self.new_marker.delete()
            return

        if self.new_marker:
            self.new_marker.delete()

        if coords and self.image_data.image_open:
            self.metadata_data.entries["latitude"].delete(0, tk.END)
            self.metadata_data.entries["latitude"].insert(0, coords[0])
            self.metadata_data.entries["longitude"].delete(0, tk.END)
            self.metadata_data.entries["longitude"].insert(0, coords[1])

            if not has_specie(self.image_data.image_path):
                threading.Thread(target=self.get_specie, args=(coords[0], coords[1])).start()

            self.new_marker = self.map.set_marker(*coords,
                                                  text="Nouvelle",
                                                  icon=self.blue_icon)

    def add_marker_center_of_map(self, event=None):
        """Place un marqueur au centre de la carte visible."""
        coords = self.map.get_position()
        self.add_marker_event(coords, False)

    def get_specie(self, lat, lon):
        specie = find_specie(self.image_data.image_path, lat, lon)
        if specie:
            update_name = messagebox.askokcancel("Espèce détectée",
                                                 f"L'espèce {specie} a été reconnue.\nSi vous confirmez, cela va automatiquement ajouter l'espèce dans le nom du fichier.")
            if update_name:
                entry = self.metadata_data.entries['nom']
                new_name = f"{specie} {entry.get()}"
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, new_name)
                entry.config(state="readonly")
