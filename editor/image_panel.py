# python
from __future__ import annotations

import os
import shutil
from typing import Optional, List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QImage
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
    QFileDialog,
    QFrame,
)

from PIL import Image, ImageOps

from editor import resource_path
from editor.shared_data import StyleData
from editor.exif_editor_service import ExifEditorService
from editor.toast import Toast


class ImagePanel(QWidget):
    image_opened = pyqtSignal(str)  # path
    image_closed = pyqtSignal()
    request_recenter = pyqtSignal()
    request_find_specie = pyqtSignal()
    save_requested = pyqtSignal()
    save_as_requested = pyqtSignal()

    EXTENSIONS_LIST = [".jpg", ".jpeg", ".png", ".gif"]

    def __init__(self, style: StyleData):
        super().__init__()
        self.style = style
        self.exif_service = ExifEditorService(style)

        self.image_list: List[str] = []
        self.current_index: int = -1
        self.image_path: Optional[str] = None
        self.pil_image: Optional[Image.Image] = None

        self._build_ui()
        self.setAcceptDrops(True)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self._root_layout = root

        self.bar = QFrame(self)
        self.bar_layout = QHBoxLayout(self.bar)
        self.bar_layout.setContentsMargins(8, 6, 8, 6)
        self.bar_layout.setSpacing(8)

        self.btn_save = QToolButton()
        self.btn_save.setToolTip("Enregistrer (Ctrl+S)")
        self.btn_save.clicked.connect(self.save_requested.emit)

        self.btn_save_as = QToolButton()
        self.btn_save_as.setToolTip("Enregistrer sous (Ctrl+Shift+S)")
        self.btn_save.clicked.connect(self.save_as_requested.emit)

        self.btn_open = QToolButton()
        self.btn_open.setToolTip("Ouvrir une image (Ctrl+O)")
        self.btn_open.clicked.connect(self.open_file_dialog)

        self.btn_recenter = QToolButton()
        self.btn_recenter.setToolTip("Ajouter un marqueur centré (Ctrl+D)")
        self.btn_recenter.clicked.connect(lambda: self.request_recenter.emit())

        self.btn_find_specie = QToolButton()
        self.btn_find_specie.setToolTip("Recherche l'espèce (Ctrl+F)")
        self.btn_find_specie.clicked.connect(lambda: self.request_find_specie.emit())

        self.btn_close = QToolButton()
        self.btn_close.setToolTip("Fermer l'image (Ctrl+W)")
        self.btn_close.clicked.connect(self.close_image)

        for b in (self.btn_save, self.btn_save_as, self.btn_open, self.btn_recenter, self.btn_find_specie):
            self.bar_layout.addWidget(b)

        self.bar_layout.addStretch(1)
        self.bar_layout.addWidget(self.btn_close)

        root.addWidget(self.bar)

        self.image_area = QFrame(self)
        area_layout = QVBoxLayout(self.image_area)
        area_layout.setContentsMargins(10, 10, 10, 10)

        self.image_label = QLabel("")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        area_layout.addWidget(self.image_label, 1)

        self.drop_hint = QLabel("📂 Glissez une image ici\nou cliquez pour ouvrir")
        self.drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        area_layout.addWidget(self.drop_hint, 1)

        root.addWidget(self.image_area, 1)
        self.drop_hint.mousePressEvent = lambda e: self.open_file_dialog()

        nav = QFrame(self)
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(20, 8, 20, 8)

        self.btn_prev = QToolButton()
        self.btn_prev.clicked.connect(self.prev_image)

        self.btn_next = QToolButton()
        self.btn_next.clicked.connect(self.next_image)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.btn_next)

        root.addWidget(nav)
        self.nav = nav

        self._set_image_visible(False)
        self.apply_style()

    def apply_style(self) -> None:
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {self.style.BG_COLOR};
            }}
            QLabel {{
                color: {self.style.FONT_COLOR};
                font-size: 14px;
            }}
            """
        )
        self.bar.setStyleSheet(f"background: {self.style.BG_TAB_COLOR};")
        self.drop_hint.setStyleSheet(f"color: {self.style.FONT_COLOR};")

        def icon(name: str) -> QIcon:
            return QIcon(resource_path(f"assets/{self.style.MODE}/{name}"))

        self.btn_save.setIcon(icon("save.png"))
        self.btn_save_as.setIcon(icon("save_as.png"))
        self.btn_open.setIcon(icon("folder_open.png"))
        self.btn_recenter.setIcon(icon("recenter.png"))
        self.btn_find_specie.setIcon(icon("find_specie.png"))
        self.btn_close.setIcon(icon("close.png"))
        self.btn_prev.setIcon(icon("arrow_left.png"))
        self.btn_next.setIcon(icon("arrow_right.png"))

    def _set_image_visible(self, visible: bool) -> None:
        self.image_label.setVisible(visible)
        self.drop_hint.setVisible(not visible)

    def _pil_to_pixmap(self, image: Image.Image) -> QPixmap:
        rgb = image.convert("RGBA")
        data = rgb.tobytes("raw", "RGBA")
        qimg = QImage(data, rgb.width, rgb.height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimg)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.pil_image and self.image_label.isVisible():
            self._render_scaled()

    def _render_scaled(self) -> None:
        pix = self._pil_to_pixmap(self.pil_image)
        target = self.image_area.size()
        scaled = pix.scaled(
            target.width() - 20,
            target.height() - 20,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)

    def open_file_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir une image",
            "",
            "Images (*.jpg *.jpeg *.png *.gif);;Tous types (*.*)",
        )
        if path:
            self.load_from_path(path)

    def _build_image_list_from_path(self, image_path: str) -> None:
        folder = os.path.dirname(image_path)
        images = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in self.EXTENSIONS_LIST
        ]
        images.sort(key=lambda x: os.path.getctime(x))
        self.image_list = images
        self.current_index = images.index(image_path)

    def load_from_path(self, path: str) -> None:
        self.image_path = path
        self._build_image_list_from_path(path)
        self.load_image()

    def load_image(self) -> None:
        if not self.image_path:
            return
        try:
            image = Image.open(self.image_path)
            image = ImageOps.exif_transpose(image)
            self.pil_image = image

            self._set_image_visible(True)
            self._render_scaled()
            self.image_opened.emit(self.image_path)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")

    def close_image(self) -> None:
        self.image_list = []
        self.current_index = -1
        self.image_path = None
        self.pil_image = None
        self.image_label.setPixmap(QPixmap())
        self._set_image_visible(False)
        self.image_closed.emit()

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        file_path = urls[0].toLocalFile()
        if os.path.isfile(file_path) and os.path.splitext(file_path)[1].lower() in self.EXTENSIONS_LIST:
            self.load_from_path(file_path)

    def next_image(self) -> None:
        if not self.image_list or self.current_index < 0:
            return
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.image_path = self.image_list[self.current_index]
        self.load_image()

    def prev_image(self) -> None:
        if not self.image_list or self.current_index < 0:
            return
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.image_path = self.image_list[self.current_index]
        self.load_image()

    def save(self, get_values_callable=None) -> None:
        if not (self.image_path and self.pil_image):
            return
        if get_values_callable is None:
            return

        vals = get_values_callable()

        try:
            final_path = self.exif_service.save_exif_and_rename(
                self.pil_image,
                self.image_path,
                vals.get("nom", ""),
                vals.get("date_creation", ""),
                vals.get("latitude", ""),
                vals.get("longitude", ""),
                new_path=None,
            )
        except Exception:
            Toast(self.window(), self.style, "Problème avec la sauvegarde")
            return

        if final_path and final_path != self.image_path:
            self.image_path = final_path
            if 0 <= self.current_index < len(self.image_list):
                self.image_list[self.current_index] = final_path

        Toast(self.window(), self.style, "Image sauvegardée avec succès")
        self.load_image()

    def save_as(self, get_values_callable=None) -> None:
        if not (self.image_path and self.pil_image):
            return
        if get_values_callable is None:
            return

        base = os.path.basename(self.image_path)
        filename, ext = os.path.splitext(base)

        new_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer l'image sous...",
            f"{filename}-copy{ext}",
            "Images (*.jpg *.jpeg *.png *.gif);;Tous types (*.*)",
        )
        if not new_path:
            return

        shutil.copy2(self.image_path, new_path)
        vals = get_values_callable()

        try:
            _ = self.exif_service.save_exif_and_rename(
                self.pil_image,
                new_path,
                vals.get("nom", ""),
                vals.get("date_creation", ""),
                vals.get("latitude", ""),
                vals.get("longitude", ""),
                new_path=new_path,
            )
        except Exception:
            Toast(self.window(), self.style, "Problème avec la sauvegarde")
            return

        Toast(self.window(), self.style, "Image sauvegardée avec succès")
