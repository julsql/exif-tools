# python
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QToolButton,
)

from editor import resource_path
from editor.shared_data import StyleData
from editor.exif_utils import (
    get_name,
    get_format,
    get_weight,
    get_size,
    get_device,
    get_date_taken,
    get_date_modify,
    get_coordinates,
)


@dataclass(frozen=True)
class FieldSpec:
    key: str
    title: str
    readonly: bool


class MetadataPanel(QWidget):
    metadata_changed = pyqtSignal()

    DEFAULT_MESSAGE = "✅️ Aucune erreur"
    WARNING_MESSAGE = "⚠️ Attention : "

    FIELDS = [
        FieldSpec("nom", "Nom", True),
        FieldSpec("format", "Format", True),
        FieldSpec("poids", "Poids", True),
        FieldSpec("dimensions", "Dimensions (lxH)", True),
        FieldSpec("appareil", "Appareil photo", True),
        FieldSpec("date_creation", "Date de création", False),
        FieldSpec("date_modification", "Date de modification", True),
        FieldSpec("latitude", "Latitude", False),
        FieldSpec("longitude", "Longitude", False),
    ]

    def __init__(self, style: StyleData):
        super().__init__()
        self.style = style

        self._data_snapshot: Optional[Dict[str, str]] = None
        self.entries: Dict[str, QLineEdit] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {self.style.BG_COLOR};
            }}
            QLabel {{
                color: {self.style.FONT_COLOR};
                font-size: 14px;
            }}
            QLineEdit {{
                color: {self.style.FONT_COLOR};
                background: {self.style.BG_COLOR};
                border: 1px solid {self.style.BORDER_COLOR};
                border-radius: 6px;
                padding: 6px;
            }}
            QLineEdit:read-only {{
                color: {self.style.FG_DISABLE};
                background: {self.style.BG_DISABLE};
                border: 1px solid {self.style.BORDER_COLOR};
            }}
            """
        )

        grid = QGridLayout(self)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        reset_icon = QIcon(resource_path(f"assets/{self.style.MODE}/reset.png"))

        self.reset_all_btn = QToolButton(self)
        self.reset_all_btn.setIcon(reset_icon)
        self.reset_all_btn.setToolTip("Réinitialiser les valeurs")
        self.reset_all_btn.clicked.connect(self.reset_all)
        grid.addWidget(self.reset_all_btn, 0, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)

        row = 1
        for spec in self.FIELDS:
            lab = QLabel(f"{spec.title} :")
            entry = QLineEdit()
            entry.setReadOnly(spec.readonly)

            self.entries[spec.key] = entry

            grid.addWidget(lab, row, 0)
            grid.addWidget(entry, row, 1)

            if not spec.readonly:
                btn = QToolButton(self)
                btn.setIcon(reset_icon)
                btn.setToolTip(f"Réinitialiser {spec.title}")
                btn.clicked.connect(lambda _=False, k=spec.key: self.reset_field(k))
                grid.addWidget(btn, row, 2)

                entry.editingFinished.connect(self._on_edit_finished)
            else:
                spacer = QLabel("")
                spacer.setFixedWidth(24)
                grid.addWidget(spacer, row, 2)

            row += 1

        self.error_label = QLabel(self.DEFAULT_MESSAGE)
        self.error_label.setStyleSheet(f"color: {self.style.FONT_COLOR};")
        grid.addWidget(self.error_label, row, 0, 1, 3)

        grid.setColumnStretch(1, 1)

    def _on_edit_finished(self) -> None:
        ok_date = self._validate_date()
        ok_coords = self._validate_coords()
        if ok_date and ok_coords:
            self._set_ok()
            self.metadata_changed.emit()

    def _set_ok(self) -> None:
        self.error_label.setText(self.DEFAULT_MESSAGE)
        self.error_label.setStyleSheet(f"color: {self.style.FONT_COLOR};")

    def _set_warn(self, text: str) -> None:
        self.error_label.setText(self.WARNING_MESSAGE + text)
        self.error_label.setStyleSheet(f"color: {self.style.FONT_ERROR_COLOR};")

    def _validate_coords(self) -> bool:
        lat_s = self.entries["latitude"].text().strip()
        lon_s = self.entries["longitude"].text().strip()

        # Autoriser vide (= suppression)
        if lat_s == "" and lon_s == "":
            return True

        try:
            lat = float(lat_s)
            lon = float(lon_s)
        except Exception:
            self._set_warn("Coordonnées invalides")
            return False

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            self._set_warn("Coordonnées invalides")
            return False

        return True

    def _validate_date(self) -> bool:
        s = self.entries["date_creation"].text().strip()

        # vide = suppression => OK
        if s == "":
            return True

        from datetime import datetime

        for fmt in self.style.ACCEPTED_DATE_FORMATS:
            try:
                dt = datetime.strptime(s, fmt)
                self.entries["date_creation"].setText(dt.strftime(self.style.DISPLAYED_DATE_FORMAT))
                return True
            except ValueError:
                continue

        self._set_warn("Date invalide")
        return False

    def clear_all(self) -> None:
        for spec in self.FIELDS:
            self.entries[spec.key].setText("")
        self._data_snapshot = None
        self._set_ok()

    def reset_field(self, key: str) -> None:
        if not self._data_snapshot:
            return
        if key not in self.entries:
            return
        self.entries[key].setText(self._data_snapshot.get(key, ""))
        if self._validate_date() and self._validate_coords():
            self._set_ok()
            self.metadata_changed.emit()

    def reset_all(self) -> None:
        if not self._data_snapshot:
            return
        for spec in self.FIELDS:
            self.entries[spec.key].setText(self._data_snapshot.get(spec.key, ""))
        if self._validate_date() and self._validate_coords():
            self._set_ok()
            self.metadata_changed.emit()

    def load_from_image(self, image, image_path: str) -> None:
        data = {
            "nom": get_name(image_path) if image_path else "",
            "format": str(get_format(image) or ""),
            "poids": get_weight(image_path) if image_path else "",
            "dimensions": get_size(image) if image else "",
            "appareil": str(get_device(image) or ""),
            "date_creation": str(
                get_date_taken(image, self.style.EXIF_DATE_FORMAT, self.style.DISPLAYED_DATE_FORMAT) or ""
            ),
            "date_modification": str(get_date_modify(image_path) if image_path else ""),
        }

        lat, lon = (None, None)
        if image:
            lat, lon = get_coordinates(image)

        data["latitude"] = "" if lat is None else str(lat)
        data["longitude"] = "" if lon is None else str(lon)

        self._data_snapshot = dict(data)

        for spec in self.FIELDS:
            self.entries[spec.key].setText(data.get(spec.key, ""))

        self._set_ok()

    def get_editable_values(self) -> Dict[str, str]:
        return {
            "nom": self.entries["nom"].text(),
            "date_creation": self.entries["date_creation"].text(),
            "latitude": self.entries["latitude"].text(),
            "longitude": self.entries["longitude"].text(),
        }

    # --------- Ajouts étape 3 ---------

    def set_coordinates(self, lat: float, lon: float, emit_change: bool = True) -> None:
        self.entries["latitude"].blockSignals(True)
        self.entries["longitude"].blockSignals(True)
        try:
            self.entries["latitude"].setText(str(lat))
            self.entries["longitude"].setText(str(lon))
        finally:
            self.entries["latitude"].blockSignals(False)
            self.entries["longitude"].blockSignals(False)

        if self._validate_date() and self._validate_coords():
            self._set_ok()
            if emit_change:
                self.metadata_changed.emit()

    def get_coordinates(self) -> Optional[tuple[float, float]]:
        lat_s = self.entries["latitude"].text().strip()
        lon_s = self.entries["longitude"].text().strip()
        try:
            lat = float(lat_s)
            lon = float(lon_s)
        except Exception:
            return None
        return lat, lon

    def set_name_prefix(self, prefix: str) -> None:
        current = self.entries["nom"].text().strip()
        new_value = f"{prefix} {current}".strip()
        self.entries["nom"].setText(new_value)