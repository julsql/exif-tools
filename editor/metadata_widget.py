import os
import re
import tkinter as tk
from datetime import datetime
from tkinter import ttk

import piexif

from editor import resource_path
from editor.image_widget import load_icon
from editor.shared_data import ImageData, StyleData, MetadataData


class MetadataWidget(tk.Frame):
    WARNING_MESSAGE = "⚠️ Attention : "
    LABELS = [{"key": "nom", "title": "Nom", "disable": True},
              {"key": "format", "title": "Format", "disable": True},
              {"key": "poids", "title": "Poids", "disable": True},
              {"key": "dimensions", "title": "Dimensions (lxH)", "disable": True},
              {"key": "appareil", "title": "Appareil photo", "disable": True},
              {"key": "date_creation", "title": "Date de création", "disable": False},
              {"key": "date_modification", "title": "Date de modification", "disable": True},
              {"key": "latitude", "title": "Latitude", "disable": False},
              {"key": "longitude", "title": "Longitude", "disable": False},
              ]

    def __init__(self, parent, event_bus, image_data: ImageData, metadata_data: MetadataData, style_data: StyleData):
        button_event = "<Button-1>"
        focus_out_event = "<FocusOut>"
        enter_event = "<Return>"
        entry_style = "Custom.TEntry"

        super().__init__(parent)
        self.event_bus = event_bus
        self.image_data = image_data
        self.metadata_data = metadata_data
        self.style_data = style_data

        self.configure(bg=style_data.BG_COLOR)

        assets_path = resource_path("assets/")
        self.reset_icon = load_icon(os.path.join(assets_path, style_data.MODE, "reset.png"), 20)
        self.reset_button = tk.Label(self, image=self.reset_icon, bg=style_data.BG_COLOR, padx=0)
        self.reset_button.grid(row=0, column=0, sticky="w")
        self.reset_button.bind(button_event, self.reset_all)

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure(entry_style,
                        foreground=style_data.FONT_COLOR,
                        fieldbackground=style_data.BG_COLOR,
                        background=style_data.BG_COLOR,
                        bordercolor=style_data.BG_COLOR,
                        relief="flat",
                        padding=3,
                        font=style_data.FONT)

        style.map(entry_style, bordercolor=[])

        style.map(entry_style,
                  foreground=[("readonly", self.style_data.FG_DISABLE)],
                  fieldbackground=[("readonly", self.style_data.BG_DISABLE)],
                  background=[("readonly", self.style_data.BG_COLOR)],
                  )

        for i, label_data in enumerate(self.LABELS):
            label = tk.Label(self, text="{0} : ".format(label_data["title"]), bg=style_data.BG_COLOR,
                             fg=style_data.FONT_COLOR, font=style_data.FONT)

            entry = ttk.Entry(self, style='Custom.TEntry')

            if label_data["key"] in ["latitude", "longitude"]:
                entry.bind(enter_event, self.on_validate_coordinates_change)
                entry.bind(focus_out_event, self.on_validate_coordinates_change)

            if label_data["key"] in ["date_creation"]:
                entry.bind(enter_event, self.on_validate_date_change)
                entry.bind(focus_out_event, self.on_validate_date_change_focus_out)

            label.grid(row=i + 1, column=0, sticky="w", padx=5, pady=5)
            entry.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=5)

            if label_data["disable"]:
                entry.config(state="readonly")
            else:
                btn_reset = tk.Label(self, image=self.reset_icon, bg=style_data.BG_COLOR, padx=0)
                btn_reset.bind(button_event,
                               lambda event, local_key=label_data["key"], index=i: self.reset(event, local_key, index))
                btn_reset.grid(row=i + 1, column=2, padx=5, pady=5)

            self.metadata_data.entries[label_data["key"]] = entry

        self.errorLabel = tk.Label(self, text="", bg=style_data.BG_COLOR, fg=style_data.FONT_ERROR_COLOR,
                                   font=style_data.FONT)
        self.errorLabel.grid(row=len(self.LABELS) + 2, column=0, columnspan=3, sticky="we", padx=5, pady=5)

        self.grid_columnconfigure(1, weight=1)

        self.event_bus.subscribe("metadata_updated", self.update_metadata)

    def on_focus_in(self, event):
        """Changement de bordure quand l'entry reçoit le focus."""
        event.widget.config(highlightbackground=self.style_data.SELECT_COLOR,
                            highlightcolor=self.style_data.SELECT_COLOR)

    def on_focus_out(self, event):
        """Changement de bordure quand l'entry reçoit le focus."""
        event.widget.config(highlightbackground=self.style_data.BORDER_COLOR,
                            highlightcolor=self.style_data.BG_COLOR)

    def on_validate_coordinates_change(self, event=None):
        if self.coordinates_valid():
            self.errorLabel.configure(text="")
            self.event_bus.publish("metadata_updated", "edit")
        else:
            self.errorLabel.configure(text=self.WARNING_MESSAGE + "Coordonnées invalides")

    def on_validate_date_change(self, event=None):
        if self.date_valid():
            self.errorLabel.configure(text="")
        else:
            self.errorLabel.configure(text=self.WARNING_MESSAGE + "Date invalide")

    def on_validate_date_change_focus_out(self, event=None):
        self.on_validate_date_change(event)

    def coordinates_valid(self):
        try:
            lat = float(self.metadata_data.entries["latitude"].get())
            lon = float(self.metadata_data.entries["longitude"].get())
        except (ValueError, TypeError):
            return False

        return -90 <= lat <= 90 and -180 <= lon <= 180

    def date_valid(self):
        try:
            date_create_str = self.metadata_data.entries["date_creation"].get()
            datetime.strptime(date_create_str, self.style_data.DISPLAYED_DATE_FORMAT)
            return True
        except (ValueError, TypeError):
            return False

    def reset(self, event, key, index):
        """Reset la valeur d'un input."""
        if self.image_data.image_open:
            entry = self.metadata_data.entries[key]
            entry.delete(0, tk.END)

            data = self.get_data()
            if data:
                value = data[index]["value"]
                if value:
                    entry.insert(0, value)
            self.event_bus.publish("metadata_updated", "edit")

    def reset_all(self, event=None):
        """Reset la valeur des metadata."""
        if self.image_data.image_open:
            for index, entry in enumerate(self.metadata_data.entries.values()):
                entry.config(state="normal")
                entry.delete(0, tk.END)

                data = self.get_data()
                if data:
                    value = data[index]["value"]
                    entry.insert(0, value)
                if self.LABELS[index]["disable"]:
                    entry.config(state="readonly")
            self.event_bus.publish("metadata_updated", "edit")

    def hook_imagewidget(self):
        # Récupère le widget parent et s'abonne à son événement
        if self.master and hasattr(self.master, "winfo_children"):
            for widget in self.master.winfo_children():
                widget.bind("<<ImageUpdated>>", self.update_metadata)

    def get_data(self):
        image = self.image_data.pil_image
        path = self.image_data.image_path

        if image and path:
            latitude, longitude = get_coordinates(image)
            return [{"key": "nom", "value": get_name(path)},
                    {"key": "format", "value": get_format(image)},
                    {"key": "poids", "value": get_poids(path)},
                    {"key": "dimensions", "value": get_size(image)},
                    {"key": "appareil", "value": get_device(image)},
                    {"key": "date_creation", "value": get_date_taken(image, self.style_data.EXIF_DATE_FORMAT,
                                                                     self.style_data.DISPLAYED_DATE_FORMAT)},
                    {"key": "date_modification", "value": get_date_modify(path)},
                    {"key": "latitude", "value": latitude},
                    {"key": "longitude", "value": longitude},
                    ]
        return None

    def update_metadata(self, publisher):
        self.errorLabel.configure(text="")
        if publisher == "open":
            data = self.get_data()
            if data:
                self._populate_entries(data)
        elif publisher == "close":
            self._clear_all_entries()

    def _populate_entries(self, data):
        for i, label_data in enumerate(data):
            key = label_data["key"]
            value = str(label_data.get("value") or "")

            if key in self.metadata_data.entries:
                self._update_entry(i, key, value)

    def _update_entry(self, index, key, value):
        entry = self.metadata_data.entries[key]
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)

        if self.LABELS[index]["disable"]:
            entry.config(state="readonly")

    def _clear_all_entries(self):
        for index, entry in enumerate(self.metadata_data.entries.values()):
            entry.config(state="normal")
            entry.delete(0, tk.END)

            if self.LABELS[index]["disable"]:
                entry.config(state="readonly")


def get_date_taken(image, exif_date_format, displayed_date_format):
    try:
        exif_data = piexif.load(image.info['exif'])
    except Exception:
        return None
    else:
        date_prise_vue = exif_data.get("0th", {}).get(piexif.ImageIFD.DateTime)

        if date_prise_vue:
            date_prise_vue = date_prise_vue.decode('utf-8')
            date_obj = datetime.strptime(date_prise_vue, exif_date_format)
            date_prise_vue_formattee = date_obj.strftime(displayed_date_format)
            return date_prise_vue_formattee
        else:
            return None


def get_date_modify(path):
    date_modification_timestamp = os.path.getmtime(path)
    date_modification = datetime.fromtimestamp(date_modification_timestamp)
    return date_modification


def get_poids(path):
    poids_image = os.path.getsize(path)
    poids_image_ko = (poids_image / 1024)
    return f"{poids_image_ko:.2f} Ko"


def get_name(path):
    return ".".join(path.split("/")[-1].split(".")[:-1])


def get_device(image):
    """Retourne le nom de l'appareil photo qui a pris une image si disponibles"""
    try:
        exif_dict = piexif.load(image.info['exif'])
    except Exception:
        return None
    else:
        if "0th" in exif_dict:
            make = exif_dict["0th"].get(piexif.ImageIFD.Make, b"").decode("utf-8", errors="ignore")
            model = exif_dict["0th"].get(piexif.ImageIFD.Model, b"").decode("utf-8", errors="ignore")
            make = re.sub(r'\s+', ' ', make).strip()
            model = re.sub(r'\s+', ' ', model).strip()
            if model.lower().startswith(make.lower()):
                result = model
            else:
                result = f"{make} {model}"
            return result
        else:
            return None


def get_format(image):
    return image.format


def get_size(image):
    return f"{image.width} x {image.height}"


def get_geotagging(exif_data):
    """Extrait les données GPS du dictionnaire EXIF"""
    if "GPS" in exif_data:
        gps_data = exif_data["GPS"]
        latitude = gps_data.get(piexif.GPSIFD.GPSLatitude)
        longitude = gps_data.get(piexif.GPSIFD.GPSLongitude)

        if latitude and longitude:
            lat_deg = latitude[0][0] / latitude[0][1]
            lat_min = latitude[1][0] / latitude[1][1]
            lat_sec = latitude[2][0] / latitude[2][1]
            latitude = lat_deg + (lat_min / 60) + (lat_sec / 3600)

            lon_deg = longitude[0][0] / longitude[0][1]
            lon_min = longitude[1][0] / longitude[1][1]
            lon_sec = longitude[2][0] / longitude[2][1]
            longitude = lon_deg + (lon_min / 60) + (lon_sec / 3600)

            # Si la latitude ou longitude sont dans l'hémisphère sud ou ouest, on inverse les signes
            if gps_data.get(piexif.GPSIFD.GPSLatitudeRef).decode() == 'S':
                latitude = -latitude
            if gps_data.get(piexif.GPSIFD.GPSLongitudeRef).decode() == 'W':
                longitude = -longitude

            return latitude, longitude
    return None, None


def get_coordinates(image):
    """Retourne les coordonnées GPS d'une image si disponibles"""
    try:
        exif_data = piexif.load(image.info['exif'])
    except Exception:
        return None, None
    else:
        latitude, longitude = get_geotagging(exif_data)
        if latitude is not None and longitude is not None:
            return latitude, longitude
        else:
            return None, None
