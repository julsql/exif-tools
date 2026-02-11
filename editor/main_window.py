# python
import os
import queue

import requests
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QColor, QPalette
from PyQt6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QDialog,
)

from editor import resource_path
from editor.config_manager import ConfigManager
from editor.shared_data import StyleData
from editor.image_panel import ImagePanel
from editor.metadata_panel import MetadataPanel
from editor.map_panel import MapPanel
from editor.specie_dialog import SpecieDialog

from detect_specie.inference_worker import InferenceWorker
from detect_specie.model_loader import ModelLoaderThread
from detect_specie.model_service import ModelService


class MainWindow(QMainWindow):
    DEFAULT_HEIGHT = 800
    DEFAULT_WIDTH = 1200
    DEFAULT_APP_TITLE = "Éditeur Exif"

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.style_data = StyleData()
        self.config = ConfigManager()
        self.config.load()

        theme = self.config.get("theme", "dark")
        self.style_data = StyleData(mode=theme)

        self.setWindowTitle(self.DEFAULT_APP_TITLE)
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))

        # Modèle (comme Tk : threads + queue, mais piloté par un timer Qt)
        self.model_queue = queue.Queue()
        self.model_service = ModelService()
        self.class_mapping = None
        self.transform = None
        self._origin_coords: tuple[float, float] | None = None  # NEW

        loader = ModelLoaderThread(self.model_service, self.model_queue)
        loader.start()

        self._build_ui()
        self._build_menu()

        QTimer.singleShot(0, self.restore_layout)
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(200)
        self._poll_timer.timeout.connect(self.check_model_queue)
        self._poll_timer.start()

    def _build_ui(self) -> None:
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.left_splitter = QSplitter(Qt.Orientation.Vertical, self.main_splitter)

        self.image_panel = ImagePanel(self.style_data)
        self.metadata_panel = MetadataPanel(self.style_data)
        self.map_panel = MapPanel(self.style_data, self.config)

        self.left_splitter.addWidget(self.image_panel)
        self.left_splitter.addWidget(self.metadata_panel)

        self.main_splitter.addWidget(self.left_splitter)
        self.main_splitter.addWidget(self.map_panel)

        self.setCentralWidget(self.main_splitter)

        self.setStyleSheet(f"QMainWindow {{ background: {self.style_data.BG_COLOR}; }}")
        self.apply_style()

        # Wiring
        self.image_panel.image_opened.connect(self._on_image_opened)
        self.image_panel.image_closed.connect(self._on_image_closed)

        self.image_panel.request_recenter.connect(self.map_panel.add_marker_center_of_map)
        self.image_panel.request_find_specie.connect(self._maybe_get_specie)
        self.image_panel.save_requested.connect(lambda: self.image_panel.save(self.metadata_panel.get_editable_values))
        self.image_panel.save_as_requested.connect(lambda: self.image_panel.save_as(self.metadata_panel.get_editable_values))

        self.map_panel.coords_picked.connect(self._on_map_coords_picked)
        self.metadata_panel.metadata_changed.connect(self._on_metadata_changed)

    def apply_style(self) -> None:
        self.setStyleSheet(f"QMainWindow {{ background: {self.style_data.BG_COLOR}; }}")
        self.image_panel.apply_style()
        self.metadata_panel.apply_style()
        self.map_panel.setStyleSheet(f"background: {self.style_data.BG_COLOR};")

    def _update_marker_actions_enabled(self) -> None:
        enabled = bool(self.image_panel.image_path)
        if hasattr(self, "act_center_marker"):
            self.act_center_marker.setEnabled(enabled)

    def _coords_match_origin(self, lat: float, lon: float) -> bool:
        if not self._origin_coords:
            return False
        o_lat, o_lon = self._origin_coords
        eps = 1e-6  # tolérance float (suffisante pour "même point" en UI)
        return abs(lat - o_lat) <= eps and abs(lon - o_lon) <= eps

    def _on_image_opened(self, path: str) -> None:
        self.setWindowTitle(os.path.basename(path))
        self.metadata_panel.load_from_image(self.image_panel.pil_image, path)

        self.map_panel.set_picking_enabled(True)
        self._update_marker_actions_enabled()

        coords = self.metadata_panel.get_coordinates()
        if coords:
            lat, lon = coords
            self._origin_coords = (lat, lon)  # NEW: origine
            self.map_panel.clear_markers()
            self.map_panel.set_origin_marker(lat, lon)
            self.map_panel.pan_to(lat, lon)
        else:
            self._origin_coords = None
            self.map_panel.clear_markers()

        self._maybe_get_specie()

    def _on_image_closed(self) -> None:
        self.setWindowTitle(self.DEFAULT_APP_TITLE)
        self.metadata_panel.clear_all()
        self.map_panel.clear_markers()

        self._origin_coords = None  # NEW

        self.map_panel.set_picking_enabled(False)
        self._update_marker_actions_enabled()

    def _on_map_coords_picked(self, lat: float, lon: float) -> None:
        if not self.image_panel.image_path:
            return

        # Met à jour les champs
        self.metadata_panel.set_coordinates(lat, lon, emit_change=True)

        # Si on retombe sur les coords d'origine -> supprime le bleu
        if self._coords_match_origin(lat, lon):
            self.map_panel.clear_new_marker()
            return

        # Sinon, place/maintient le bleu
        self.map_panel.set_new_marker(lat, lon)

    def _on_metadata_changed(self) -> None:
        coords = self.metadata_panel.get_coordinates()
        if coords and self.image_panel.image_path:
            lat, lon = coords

            # Si l'utilisateur remet les champs sur l'origine -> supprimer le bleu
            if self._coords_match_origin(lat, lon):
                self.map_panel.clear_new_marker()
            else:
                self.map_panel.set_new_marker(lat, lon)

        self._maybe_get_specie()

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()

        # Fenêtre
        menu_fenetre = menu_bar.addMenu("Fenêtre")

        act_reset_window = QAction("Réinitialiser la fenêtre", self)
        act_reset_window.setShortcut(QKeySequence("Ctrl+R"))
        act_reset_window.triggered.connect(self.reset_window)
        menu_fenetre.addAction(act_reset_window)

        self.act_toggle_theme = QAction("", self)
        self.act_toggle_theme.triggered.connect(self.toggle_theme)
        menu_fenetre.addAction(self.act_toggle_theme)

        # Switch map tiles (comme avant)
        self.act_switch_map = QAction("", self)
        self.act_switch_map.triggered.connect(self.switch_map)
        menu_fenetre.addAction(self.act_switch_map)

        # Switch reconnaissance espèce (comme avant)
        self.act_switch_recognition = QAction("", self)
        self.act_switch_recognition.triggered.connect(self.switch_specie_recognition)
        menu_fenetre.addAction(self.act_switch_recognition)

        self._refresh_switch_labels()
        self._refresh_theme_label()
        # Fichier
        menu_fichier = menu_bar.addMenu("Fichier")

        act_save = QAction("Enregistrer", self)
        act_save.setShortcut(QKeySequence(QKeySequence.StandardKey.Save))
        act_save.triggered.connect(lambda: self.image_panel.save(self.metadata_panel.get_editable_values))

        act_save_as = QAction("Enregistrer sous", self)
        act_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        act_save_as.triggered.connect(lambda: self.image_panel.save_as(self.metadata_panel.get_editable_values))

        act_open = QAction("Ouvrir une image", self)
        act_open.setShortcut(QKeySequence(QKeySequence.StandardKey.Open))
        act_open.triggered.connect(self.image_panel.open_file_dialog)

        act_close = QAction("Fermer l'image", self)
        act_close.setShortcut(QKeySequence("Ctrl+W"))
        act_close.triggered.connect(self.image_panel.close_image)

        act_center = QAction("Ajouter un marqueur centré", self)
        act_center.setShortcut(QKeySequence("Ctrl+D"))
        act_center.triggered.connect(self.map_panel.add_marker_center_of_map)
        self.act_center_marker = act_center

        act_find = QAction("Recherche l'espèce", self)
        act_find.setShortcut(QKeySequence("Ctrl+F"))
        act_find.triggered.connect(self._maybe_get_specie)

        act_next = QAction("Image suivante", self)
        act_next.setShortcut(QKeySequence(Qt.Key.Key_Right))
        act_next.triggered.connect(self.image_panel.next_image)

        act_prev = QAction("Image précédente", self)
        act_prev.setShortcut(QKeySequence(Qt.Key.Key_Left))
        act_prev.triggered.connect(self.image_panel.prev_image)

        menu_fichier.addAction(act_save)
        menu_fichier.addAction(act_save_as)
        menu_fichier.addSeparator()
        menu_fichier.addAction(act_open)
        menu_fichier.addAction(act_close)
        menu_fichier.addSeparator()
        menu_fichier.addAction(act_center)
        menu_fichier.addAction(act_find)
        menu_fichier.addSeparator()
        menu_fichier.addAction(act_next)
        menu_fichier.addAction(act_prev)

        # Aide
        menu_aide = menu_bar.addMenu("Aide")
        act_about = QAction("À propos", self)
        act_about.triggered.connect(self._about)
        menu_aide.addAction(act_about)
        update_about = QAction("Mise à jour", self)
        update_about.triggered.connect(self._update)
        menu_aide.addAction(update_about)
        self._update_marker_actions_enabled()

    def _refresh_theme_label(self) -> None:
        if self.style_data.MODE == "dark":
            self.act_toggle_theme.setText("Passer en mode clair")
        else:
            self.act_toggle_theme.setText("Passer en mode sombre")
        self.app.setPalette(self.build_palette())

    def build_palette(self):
        palette = QPalette()

        # Fond général des fenêtres et dialogs
        palette.setColor(QPalette.ColorRole.Window, QColor(self.style_data.BG_COLOR))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(self.style_data.FONT_COLOR))

        # Fond des zones éditables (QLineEdit, QTextEdit, etc.)
        palette.setColor(QPalette.ColorRole.Base, QColor(self.style_data.BG_TAB_COLOR))
        palette.setColor(QPalette.ColorRole.Text, QColor(self.style_data.FONT_COLOR))

        # Boutons
        palette.setColor(QPalette.ColorRole.Button, QColor(self.style_data.BUTTON_COLOR))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(self.style_data.FONT_COLOR))

        # Sélection
        palette.setColor(QPalette.ColorRole.Highlight, QColor(self.style_data.SELECT_COLOR))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(self.style_data.FONT_COLOR))

        # États désactivés
        palette.setColor(QPalette.ColorGroup.Disabled,
                         QPalette.ColorRole.Text,
                         QColor(self.style_data.FG_DISABLE))
        palette.setColor(QPalette.ColorGroup.Disabled,
                         QPalette.ColorRole.WindowText,
                         QColor(self.style_data.FG_DISABLE))
        palette.setColor(QPalette.ColorGroup.Disabled,
                         QPalette.ColorRole.ButtonText,
                         QColor(self.style_data.FG_DISABLE))
        return palette

    def toggle_theme(self) -> None:
        new_mode = "light" if self.style_data.MODE == "dark" else "dark"
        self.style_data.set_mode(new_mode)

        self.config.set("theme", new_mode)
        self.config.save()

        self.apply_style()
        self._refresh_theme_label()
        self._refresh_switch_labels()

    def _refresh_switch_labels(self) -> None:
        current_map = self.config.get("map", self.style_data.DEFAULT_MAP)
        self.act_switch_map.setText(self.style_data.MAPS_SWITCH_LABEL[current_map])

        recog = self.config.get("recognition", self.style_data.DEFAULT_SPECIE)
        self.act_switch_recognition.setText(self.style_data.SPECIE_SWITCH_LABEL[recog])

    def switch_map(self) -> None:
        old_map = self.config.get("map", self.style_data.DEFAULT_MAP)
        new_map = "international" if old_map == "french" else "french"
        self.config.set("map", new_map)
        self.config.save()

        tile_url = self.style_data.MAPS[new_map]
        self.map_panel.set_tile_url(tile_url)

        self._refresh_switch_labels()

    def switch_specie_recognition(self) -> None:
        recog = self.config.get("recognition", self.style_data.DEFAULT_SPECIE)
        self.config.set("recognition", not recog)
        self.config.save()
        self._refresh_switch_labels()

        # si on réactive, on relance une détection si possible
        self._maybe_get_specie()

    def _about(self) -> None:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "À propos", "Éditeur Exif\nVersion 2.0.1\n© 2025 Jul SQL")

    def _update(self):
        from PyQt6.QtWidgets import QMessageBox, QLabel
        from PyQt6.QtCore import Qt

        msg = QMessageBox(self)
        msg.setWindowTitle("Mise à jour")
        msg.setIcon(QMessageBox.Icon.Information)

        msg.setText(
            """
            <p>
            Pour mettre à jour, téléchargez la nouvelle version sur GitHub.
            </p>

            <p>
            <a href="https://github.com/julsql/exif-tools/releases/latest">
            https://github.com/julsql/exif-tools/releases/latest
            </a>
            </p>

            <p>
            Sinon, modifiez le fichier <b>install.sh</b> avec la nouvelle version
            (Version 2.0.1) et lancez le script dans un terminal.
            </p>
            """
        )

        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        # 🔑 Rendre le lien cliquable
        label = msg.findChild(QLabel)
        if label is not None:
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextBrowserInteraction
            )
            label.setOpenExternalLinks(True)

        msg.exec()

    def reset_window(self) -> None:
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        w = max(self.width(), 1)
        h = max(self.height(), 1)
        self.main_splitter.setSizes([w // 3, w - (w // 3)])
        self.left_splitter.setSizes([h // 2, h - (h // 2)])

        self.config.set("geometry_qt", [self.x(), self.y(), self.width(), self.height()])
        self.config.set("main_split_qt", self.main_splitter.sizes())
        self.config.set("left_split_qt", self.left_splitter.sizes())

        # Reset map position
        self.config.set("position", self.map_panel.COORDINATES_PARIS)
        self.config.set("zoom", self.map_panel.DEFAULT_ZOOM)
        self.config.save()

        self.map_panel.set_view(*self.map_panel.COORDINATES_PARIS, self.map_panel.DEFAULT_ZOOM)

    def restore_layout(self) -> None:
        geom = self.config.get("geometry_qt")
        if isinstance(geom, list) and len(geom) == 4:
            x, y, w, h = geom
            self.setGeometry(int(x), int(y), int(w), int(h))
        else:
            self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        main_sizes = self.config.get("main_split_qt")
        left_sizes = self.config.get("left_split_qt")

        if isinstance(main_sizes, list) and len(main_sizes) == 2:
            self.main_splitter.setSizes([int(main_sizes[0]), int(main_sizes[1])])
        else:
            w = max(self.width(), 1)
            self.main_splitter.setSizes([w // 3, w - (w // 3)])

        if isinstance(left_sizes, list) and len(left_sizes) == 2:
            self.left_splitter.setSizes([int(left_sizes[0]), int(left_sizes[1])])
        else:
            h = max(self.height(), 1)
            self.left_splitter.setSizes([h // 2, h - (h // 2)])

    def closeEvent(self, event) -> None:
        self.config.set("geometry_qt", [self.x(), self.y(), self.width(), self.height()])
        self.config.set("main_split_qt", self.main_splitter.sizes())
        self.config.set("left_split_qt", self.left_splitter.sizes())

        pos, zoom = self.map_panel.get_state_for_persist()
        self.config.set("position", pos)
        self.config.set("zoom", zoom)
        self.config.save()

        super().closeEvent(event)

    # ---------- Reconnaissance espèce (threads existants) ----------

    def _maybe_get_specie(self) -> None:
        recog = self.config.get("recognition", self.style_data.DEFAULT_SPECIE)
        if not recog:
            return
        if not (self.image_panel.image_path and self.image_panel.pil_image):
            return
        if not self.model_service.is_ready():
            return

        name_field = self.metadata_panel.entries["nom"].text()
        if self._has_specie(name_field):
            return

        coords = self.metadata_panel.get_coordinates()
        lat, lon = (None, None)
        if coords:
            lat, lon = coords

        worker = InferenceWorker(
            self.model_service,
            self.image_panel.image_path,
            lat,
            lon,
            self.model_queue,
            self.class_mapping,
            self.transform,
        )
        worker.start()

    def check_model_queue(self) -> None:
        while not self.model_queue.empty():
            event, payload = self.model_queue.get()

            if event == "model_ready":
                import birder
                self.class_mapping = {v: k for k, v in self.model_service.model_info.class_to_idx.items()}
                size = birder.get_size_from_signature(self.model_service.model_info.signature)
                self.transform = birder.classification_transform(size, self.model_service.model_info.rgb_stats)

            elif event == "inference_done":
                self._on_specie_detected(payload)

            elif event in ("model_error", "inference_error"):
                # On log, UX: silencieux comme avant (tu peux aussi ajouter un toast Qt ici)
                print(payload)

    def _on_specie_detected(self, payload: tuple) -> None:
        (specie, path) = payload
        if not specie:
            return
        if self.image_panel.image_path != path:
            return
        url = self._get_inat_taxon_link(specie)
        dlg = SpecieDialog(self, specie, url)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.metadata_panel.set_name_prefix(specie)

    def _has_specie(self, name: str) -> bool:
        parts = (name or "").split(" ")
        return len(parts) > 2 and parts[0][:1].isupper() and parts[1][:1].islower()

    def _get_inat_taxon_id(self, scientific_name: str) -> str | None:
        url = "https://api.inaturalist.org/v1/taxa"
        params = {"q": scientific_name, "rank": "species"}
        try:
            resp = requests.get(url, params=params, timeout=5)
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if results:
                return str(results[0].get("id"))
        except Exception:
            return None
        return None

    def _get_inat_taxon_link(self, scientific_name: str) -> str | None:
        taxon_id = self._get_inat_taxon_id(scientific_name)
        if taxon_id:
            return f"https://www.inaturalist.org/taxa/{taxon_id}"
        return None