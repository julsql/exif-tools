# python
from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Optional, Tuple

import piexif
from PIL import Image


def get_name(path: str) -> str:
    return ".".join(os.path.basename(path).split(".")[:-1])


def get_weight(path: str) -> str:
    size_bytes = os.path.getsize(path)
    size_kb = size_bytes / 1024
    return f"{size_kb:.2f} Ko"


def get_size(image: Image.Image) -> str:
    return f"{image.width} x {image.height}"


def get_format(image: Image.Image) -> Optional[str]:
    return image.format


def get_device(image: Image.Image) -> Optional[str]:
    try:
        exif_dict = piexif.load(image.info["exif"])
    except Exception:
        return None

    make = exif_dict.get("0th", {}).get(piexif.ImageIFD.Make, b"").decode("utf-8", errors="ignore")
    model = exif_dict.get("0th", {}).get(piexif.ImageIFD.Model, b"").decode("utf-8", errors="ignore")

    make = re.sub(r"\s+", " ", make).strip()
    model = re.sub(r"\s+", " ", model).strip()

    if not (make or model):
        return None

    if model.lower().startswith(make.lower()):
        return model
    return f"{make} {model}".strip()


def get_date_modify(path: str) -> datetime:
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts)


def _check_validity(values) -> bool:
    if not values:
        return False
    if not isinstance(values, (list, tuple)) or len(values) != 3:
        return False
    for value in values:
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            return False
        if value[1] == 0:
            return False
    return True


def _get_geotagging(exif_data) -> Tuple[Optional[float], Optional[float]]:
    gps = exif_data.get("GPS")
    if not gps:
        return None, None

    lat = gps.get(piexif.GPSIFD.GPSLatitude)
    lon = gps.get(piexif.GPSIFD.GPSLongitude)

    if not (_check_validity(lat) and _check_validity(lon)):
        return None, None

    lat_deg = lat[0][0] / lat[0][1]
    lat_min = lat[1][0] / lat[1][1]
    lat_sec = lat[2][0] / lat[2][1]
    latitude = lat_deg + (lat_min / 60) + (lat_sec / 3600)

    lon_deg = lon[0][0] / lon[0][1]
    lon_min = lon[1][0] / lon[1][1]
    lon_sec = lon[2][0] / lon[2][1]
    longitude = lon_deg + (lon_min / 60) + (lon_sec / 3600)

    lat_ref = gps.get(piexif.GPSIFD.GPSLatitudeRef, b"N").decode(errors="ignore")
    lon_ref = gps.get(piexif.GPSIFD.GPSLongitudeRef, b"E").decode(errors="ignore")

    if lat_ref == "S":
        latitude = -latitude
    if lon_ref == "W":
        longitude = -longitude

    return latitude, longitude


def get_coordinates(image: Image.Image) -> Tuple[Optional[float], Optional[float]]:
    try:
        exif_data = piexif.load(image.info["exif"])
    except Exception:
        return None, None
    return _get_geotagging(exif_data)


def get_date_taken(image: Image.Image, exif_date_format: str, displayed_date_format: str) -> Optional[str]:
    try:
        exif_data = piexif.load(image.info["exif"])
    except Exception:
        return None

    date_tags = [
        (piexif.ExifIFD.DateTimeOriginal, "Exif"),
        (piexif.ExifIFD.DateTimeDigitized, "Exif"),
        (piexif.ImageIFD.DateTime, "0th"),
    ]

    for tag, section in date_tags:
        raw = exif_data.get(section, {}).get(tag)
        if not raw:
            continue
        try:
            raw_str = raw.decode("utf-8")
            dt = datetime.strptime(raw_str, exif_date_format)
            return dt.strftime(displayed_date_format)
        except Exception:
            continue

    return None