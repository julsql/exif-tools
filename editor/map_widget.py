import tkinter as tk

import tkintermapview

from editor import resource_path
from editor.metadata_widget import get_coordinates
from editor.shared_data import MetadataData, StyleData, ImageData


class MapWidget(tk.Frame):

    def __init__(self, parent, event_bus, image_data: ImageData, position: tuple[int, int], zoom: int, metadata_data: MetadataData, style_data: StyleData):
        super().__init__(parent)

        self.event_bus = event_bus
        self.image_data = image_data
        self.metadata_data = metadata_data
        self.style_data = style_data
        self.parent = parent

        self.red_icon = tk.PhotoImage(file=resource_path("assets/marker-red.png"))
        self.blue_icon = tk.PhotoImage(file=resource_path("assets/marker-blue.png"))

        self.map = tkintermapview.TkinterMapView(self, width=800, height=600)

        self.map.set_tile_server("https://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png")
        # self.map.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")

        self.map.pack(fill="both", expand=True)

        self.reset_position(position, zoom)

        self.origin_marker = None
        self.new_marker = None

        self.map.add_left_click_map_command(self.add_marker_event)

        self.event_bus.subscribe("metadata_updated", self.update_origin)

    def reset_position(self, position, zoom):
        """Reset la position et le zoom de la carte."""
        self.map.set_position(*position)
        self.map.set_zoom(zoom)

    def delete_markers(self):
        """Supprimer tous les marqueurs."""
        if self.origin_marker:
            self.origin_marker.delete()
        if self.new_marker:
            self.new_marker.delete()

    def update_origin(self, publisher):
        """Met à jour les marqueurs selon l'événement reçu."""
        if publisher == "open":
            coordinates = self.get_coordinates()
            self.add_origin_marker_event(coordinates)
        elif publisher == "close":
            self.delete_markers()
        elif publisher == "edit":
            coordinates = self.get_coordinates()
            self.add_marker_event(coordinates, coordinates == get_coordinates(self.image_data.pil_image))

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
        self.event_bus.publish("metadata_updated", "add_marker")
        self.delete_markers()

        if coords:
            self.map.set_position(*coords)
            self.origin_marker = self.map.set_marker(coords[0], coords[1], text="Origine", icon=self.red_icon)

    def add_marker_event(self, coords, origin=False):
        """Ajoute un marqueur à l'emplacement donné sur la carte."""

        if origin and self.new_marker:
            self.new_marker.delete()
            return

        if self.new_marker:
            self.new_marker.delete()

        if coords and self.image_data.image_open:
            self.event_bus.publish("metadata_updated", "add_marker")

            self.metadata_data.entries["latitude"].delete(0, tk.END)
            self.metadata_data.entries["latitude"].insert(0, coords[0])
            self.metadata_data.entries["longitude"].delete(0, tk.END)
            self.metadata_data.entries["longitude"].insert(0, coords[1])

            self.new_marker = self.map.set_marker(*coords,
                                                  text="Nouvelle",
                                                  icon=self.blue_icon)
