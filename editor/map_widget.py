import tkinter as tk

import tkintermapview

from editor.shared_data import MetadataData, StyleData, ImageData


class MapWidget(tk.Frame):
    COORDINATES_PARIS = (48.8566, 2.3522)

    def __init__(self, parent, event_bus, image_data: ImageData, metadata_data: MetadataData, style_data: StyleData):
        super().__init__(parent)

        self.event_bus = event_bus
        self.image_data = image_data
        self.metadata_data = metadata_data
        self.style_data = style_data
        self.parent = parent

        self.map = tkintermapview.TkinterMapView(self, width=800, height=600)
        self.map.pack(fill="both", expand=True)

        self.map.set_position(*self.COORDINATES_PARIS)
        self.map.set_zoom(5)

        self.origin_marker = None
        self.new_marker = None

        self.map.add_left_click_map_command(self.add_marker_event)

        self.event_bus.subscribe("metadata_updated", self.update_origin)

    def delete_markers(self):
        """Supprimer tous les marqueurs et recentrer la carte."""
        self.map.set_position(*self.COORDINATES_PARIS)
        if self.origin_marker:
            self.origin_marker.delete()
        if self.new_marker:
            self.new_marker.delete()

    def update_origin(self, publisher):
        """Met à jour les marqueurs selon l'événement reçu."""
        if publisher == "open":
            coordinates = self.get_coordinates()
            self.add_marker_event(coordinates, True)
        elif publisher == "close":
            self.delete_markers()
        elif publisher == "edit":
            coordinates = self.get_coordinates()
            self.add_marker_event(coordinates)

    def get_coordinates(self):
        """Récupère les coordonnées à partir des champs de métadonnées."""
        try:
            latitude = float(self.metadata_data.entries["latitude"].get())
            longitude = float(self.metadata_data.entries["longitude"].get())
        except ValueError:
            return None
        return latitude, longitude

    def add_marker_event(self, coords, origin=False):
        """Ajoute un marqueur à l'emplacement donné sur la carte."""
        self.event_bus.publish("metadata_updated", "add_marker")

        if coords:
            if origin:
                self.delete_markers()
                self.map.set_position(*coords)
                self.origin_marker = self.map.set_marker(coords[0], coords[1], text="Origine")
            else:
                if self.new_marker:
                    self.new_marker.delete()

                if self.origin_marker:
                    self.metadata_data.entries["latitude"].delete(0, tk.END)
                    self.metadata_data.entries["latitude"].insert(0, coords[0])
                    self.metadata_data.entries["longitude"].delete(0, tk.END)
                    self.metadata_data.entries["longitude"].insert(0, coords[1])

                    self.new_marker = self.map.set_marker(coords[0], coords[1], text="Nouvelle",
                                                          marker_color_circle=self.style_data.MARKER_CIRCLE_COLOR,
                                                          marker_color_outside=self.style_data.MARKER_OUTSIDE_COLOR)
