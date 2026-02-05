# python
from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Optional

import piexif
from PIL import Image

from editor.shared_data import StyleData


class ExifEditorService:
    def __init__(self, style_data: StyleData):
        self.style_data = style_data

    def parse_name(self, name: str) -> str:
        return re.sub(r'[\\/:"*?<>|]', "_", name or "")

    def parse_date_to_exif(self, date_str: str) -> Optional[str]:
        # "" -> suppression
        if date_str == "":
            return ""

        for fmt in self.style_data.ACCEPTED_DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt).strftime(self.style_data.EXIF_DATE_FORMAT)
            except ValueError:
                continue
        return None

    def parse_coordinate(self, coord_str: str):
        if coord_str == "":
            return ""
        try:
            return float(coord_str)
        except ValueError:
            return None

    def save_exif_and_rename(
        self,
        image: Image.Image,
        current_path: str,
        name_str: str,
        date_str: str,
        latitude_str: str,
        longitude_str: str,
        new_path: str | None = None,
    ) -> str | None:
        if not (image and current_path):
            return None

        name = self.parse_name(name_str)
        date = self.parse_date_to_exif(date_str)
        latitude = self.parse_coordinate(latitude_str)
        longitude = self.parse_coordinate(longitude_str)

        if date is None:
            raise ValueError("Format de date incorrect")
        if latitude is None or longitude is None:
            # Autorise la suppression via "" mais pas les valeurs non parseables
            raise ValueError("Coordonnées invalides")

        exif_bytes = self._update_exif_metadata(image, date, latitude, longitude)
        piexif.insert(exif_bytes, current_path)

        if new_path:
            final_path = new_path
        elif name:
            ext = os.path.splitext(current_path)[1]
            safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()
            final_path = os.path.join(os.path.dirname(current_path), f"{safe_name}{ext}")
        else:
            final_path = current_path

        if final_path != current_path:
            os.rename(current_path, final_path)

        return final_path

    def _decimal_to_dms_rational(self, deg: float):
        d = int(deg)
        m = int((deg - d) * 60)
        s = round(((deg - d) * 60 - m) * 60 * 10000)
        return [(d, 1), (m, 1), (s, 10000)]

    def _update_exif_metadata(self, image: Image.Image, date, latitude, longitude) -> bytes:
        exif_data = image.info.get("exif")
        if exif_data:
            exif_dict = piexif.load(exif_data)
        else:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}}

        if date is not None:
            self._update_exif_date(exif_dict, date)

        if latitude is not None:
            self._update_exif_latitude(exif_dict, latitude)
        if longitude is not None:
            self._update_exif_longitude(exif_dict, longitude)

        self._clean_metadata(exif_dict)
        return piexif.dump(exif_dict)

    def _clean_metadata(self, exif_dict):
        for _, ifd in exif_dict.items():
            if not isinstance(ifd, dict):
                continue
            for tag, value in list(ifd.items()):
                if isinstance(value, int):
                    ifd[tag] = (value, 1)
                elif isinstance(value, tuple) and len(value) == 1:
                    ifd[tag] = (value[0], 1)
                elif isinstance(value, str):
                    ifd[tag] = value.encode("utf-8")
                elif isinstance(value, list):
                    new_list = []
                    for v in value:
                        if isinstance(v, int):
                            new_list.append((v, 1))
                        elif isinstance(v, tuple):
                            new_list.append((v[0], 1) if len(v) == 1 else v)
                        else:
                            new_list.append(v)
                    ifd[tag] = new_list

        exif_dict.get("Exif", {}).pop(37500, None)
        return exif_dict

    def _update_exif_longitude(self, exif_dict, longitude):
        if longitude == "":
            exif_dict["GPS"].pop(piexif.GPSIFD.GPSLongitudeRef, None)
            exif_dict["GPS"].pop(piexif.GPSIFD.GPSLongitude, None)
            return

        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = b"E" if longitude >= 0 else b"W"
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = self._decimal_to_dms_rational(abs(longitude))

    def _update_exif_latitude(self, exif_dict, latitude):
        if latitude == "":
            exif_dict["GPS"].pop(piexif.GPSIFD.GPSLatitudeRef, None)
            exif_dict["GPS"].pop(piexif.GPSIFD.GPSLatitude, None)
            return

        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = b"N" if latitude >= 0 else b"S"
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = self._decimal_to_dms_rational(abs(latitude))

    def _update_exif_date(self, exif_dict, date):
        if date == "":
            exif_dict["0th"].pop(piexif.ImageIFD.DateTime, None)
            exif_dict["Exif"].pop(piexif.ExifIFD.DateTimeOriginal, None)
            exif_dict["Exif"].pop(piexif.ExifIFD.DateTimeDigitized, None)
            return

        encoded = date.encode()
        exif_dict["0th"][piexif.ImageIFD.DateTime] = encoded
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = encoded
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = encoded