import os
import shutil
import tkinter as tk
from datetime import datetime
from tkinter import filedialog

import piexif
from PIL import Image, ImageTk

from editor import resource_path
from editor.shared_data import ImageData, StyleData, MetadataData


def load_icon(file_path, height):
    """Charge une icône, ajuste sa taille en gardant le ratio, et renvoie une ImageTk."""
    image = Image.open(file_path)
    ratio = image.width / image.height
    width = int(height * ratio)
    resized_image = image.resize((width, height), Image.LANCZOS)
    return ImageTk.PhotoImage(resized_image)


class ImageWidget(tk.Frame):
    def __init__(self, parent, event_bus, image_data: ImageData, metadata_data: MetadataData, style_data: StyleData):
        assets_path = resource_path("assets/")
        icon_padding = 4
        icon_height = 20

        super().__init__(parent)
        self.event_bus = event_bus
        self.image_data = image_data
        self.metadata_data = metadata_data
        self.style_data = style_data

        self.parent = parent
        self.configure(bg=style_data.BG_COLOR)

        self.top_frame = tk.Frame(self, height=20, bg=style_data.BG_TAB_COLOR)
        self.top_frame.grid(row=0, column=0, sticky="ew")

        self.bottom_border_frame = tk.Frame(self, height=1, bg=style_data.BORDER_COLOR)
        self.bottom_border_frame.grid(row=1, column=0, sticky="ew")

        # Ajouter les icônes à gauche
        self.save_icon = load_icon(os.path.join(assets_path, style_data.MODE, "save.png"), icon_height)
        self.save_as_icon = load_icon(os.path.join(assets_path, style_data.MODE, "save_as.png"), icon_height)
        self.add_photo_icon = load_icon(os.path.join(assets_path, style_data.MODE, "folder_open.png"), icon_height)
        self.close_icon = load_icon(os.path.join(assets_path, style_data.MODE, "close.png"), icon_height)

        self.icon_label1 = tk.Label(self.top_frame, image=self.save_icon, bg=style_data.BG_TAB_COLOR)
        self.icon_label1.grid(row=0, column=0, padx=icon_padding)

        self.icon_label2 = tk.Label(self.top_frame, image=self.save_as_icon, bg=style_data.BG_TAB_COLOR)
        self.icon_label2.grid(row=0, column=1, padx=icon_padding)

        self.icon_label3 = tk.Label(self.top_frame, image=self.add_photo_icon, bg=style_data.BG_TAB_COLOR)
        self.icon_label3.grid(row=0, column=2, padx=icon_padding)

        self.icon_label4 = tk.Label(self.top_frame, image=self.close_icon, bg=style_data.BG_TAB_COLOR)
        self.icon_label4.grid(row=0, column=3, padx=icon_padding, sticky="e")

        # Zone d'affichage de l'image
        self.image_area = tk.Label(self, bg=style_data.BG_COLOR)
        self.image_area.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        self.top_frame.grid_columnconfigure(0, weight=0)
        self.top_frame.grid_columnconfigure(1, weight=0)
        self.top_frame.grid_columnconfigure(2, weight=0)
        self.top_frame.grid_columnconfigure(3, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Lier les actions
        button_event = "<Button-1>"
        self.icon_label1.bind(button_event, self.save)
        self.icon_label2.bind(button_event, self.save_as)
        self.icon_label3.bind(button_event, self.open_file_dialog)
        self.icon_label4.bind(button_event, self.close_image)

        self.loaded_image = None

    def save_data(self, new_path=None):
        image = self.image_data.pil_image
        path = self.image_data.image_path

        if not (image and path):
            return

        # Récupérer les valeurs des champs
        date_str = self.metadata_data.entries["date_creation"].get()
        latitude_str = self.metadata_data.entries["latitude"].get()
        longitude_str = self.metadata_data.entries["longitude"].get()

        # Valider les données
        date = self._parse_date(date_str)
        latitude = self._parse_coordinate(latitude_str)
        longitude = self._parse_coordinate(longitude_str)

        # Mettre à jour les métadonnées EXIF
        if date or latitude or longitude:
            exif_bytes = self._update_exif_metadata(image, date, latitude, longitude)
            if new_path:
                path = new_path
            piexif.insert(exif_bytes, path)

    def save_as(self, event=None):
        if self.image_data.image_open:
            path = self.image_data.image_path
            (filename, ext) = os.path.splitext(os.path.basename(path))

            file_path = filedialog.asksaveasfilename(
                defaultextension=ext,
                filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")],
                initialfile=f'{filename}-copy{ext}',
                title="Enregistrer l'image sous..."
            )

            if file_path:
                shutil.copy2(self.image_data.image_path, file_path)
                self.save_data(file_path)

    def save(self, event=None):
        if self.image_data.image_open:
            self.save_data()

    def _parse_date(self, date_str):
        try:
            return datetime.strptime(
                date_str, self.style_data.DISPLAYED_DATE_FORMAT
            ).strftime(self.style_data.EXIF_DATE_FORMAT)
        except ValueError:
            print("Format de date incorrect")
            return None

    def _parse_coordinate(self, coord_str):
        try:
            return float(coord_str)
        except ValueError:
            print("Format de latitude/longitude incorrect")
            return None

    def _decimal_to_dms_rational(self, deg):
        d = int(deg)
        m = int((deg - d) * 60)
        s = round(((deg - d) * 60 - m) * 60 * 10000)
        return [(d, 1), (m, 1), (s, 10000)]

    def _update_exif_metadata(self, image, date, latitude, longitude):
        exif_dict = piexif.load(image.info.get("exif", b""))
        print("save")

        # Dates
        if date:
            encoded_date = date.encode()
            exif_dict['0th'][piexif.ImageIFD.DateTime] = encoded_date
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = encoded_date
            exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = encoded_date

        # GPS
        if latitude:
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = b'N' if latitude >= 0 else b'S'
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = self._decimal_to_dms_rational(abs(latitude))

        if longitude:
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = b'E' if longitude >= 0 else b'W'
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = self._decimal_to_dms_rational(abs(longitude))

        return piexif.dump(exif_dict)

    def close_image(self, event=None):
        """Ferme l'image."""
        self.loaded_image = None
        self.image_area.image = None
        self.image_area.config(image='')

        self.image_data.image_path = None
        self.image_data.pil_image = None
        self.image_data.tk_image = None
        self.image_data.image_open = False
        self.event_bus.publish("metadata_updated", "close")

    def open_file_dialog(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
        if file_path:
            self.image_data.image_path = file_path
            self.load_image()

    def reset_image(self, event=None):
        if self.image_data.pil_image:
            image = self.image_data.pil_image
            tk_image = image
            if image.format not in ['PNG', 'GIF', 'PPM', 'PGM']:
                tk_image = image.convert("RGB")

            tk_image.thumbnail((self.winfo_width(), self.winfo_height()), Image.Resampling.LANCZOS)

            # Convertir l'image pour tkinter
            loaded_image = ImageTk.PhotoImage(tk_image)

            self.image_area.config(image=loaded_image)
            self.image_area.image = loaded_image
            self.image_data.tk_image = loaded_image

    def load_image(self):
        """Charge l'image en entier et l'affiche dans la zone vide"""
        try:
            image = Image.open(self.image_data.image_path)
            self.image_data.pil_image = image
            self.image_data.image_open = True
            self.reset_image()
            self.event_bus.publish("metadata_updated", "open")

        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")
