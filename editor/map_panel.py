# python
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional, Tuple

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QUrl, QEvent
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from editor import resource_path
from editor.config_manager import ConfigManager
from editor.shared_data import StyleData


@dataclass
class MapState:
    lat: float
    lon: float
    zoom: int


class _Bridge(QObject):
    coordsPicked = pyqtSignal(float, float)
    stateChanged = pyqtSignal(float, float, int)

    def __init__(self, init_params: dict):
        super().__init__()
        self._init_params = init_params

    @pyqtSlot(result="QVariant")
    def getInitParams(self):
        return self._init_params

    @pyqtSlot(float, float)
    def onCoordsPicked(self, lat: float, lon: float):
        self.coordsPicked.emit(lat, lon)

    @pyqtSlot(float, float, int)
    def onMapStateChanged(self, lat: float, lon: float, zoom: int):
        self.stateChanged.emit(lat, lon, zoom)


class MapPanel(QWidget):
    COORDINATES_PARIS = (48.8566, 2.3522)
    DEFAULT_ZOOM = 5

    coords_picked = pyqtSignal(float, float)
    file_dropped = pyqtSignal(QEvent)

    def __init__(self, style: StyleData, config: ConfigManager):
        super().__init__()
        self.style = style
        self.config = config

        self._last_state: Optional[MapState] = None

        position = self.config.get("position", self.COORDINATES_PARIS)
        zoom = self.config.get("zoom", self.DEFAULT_ZOOM)
        tile_key = self.config.get("map", self.style.DEFAULT_MAP)
        tile_url = self.style.MAPS.get(tile_key, self.style.MAPS[self.style.DEFAULT_MAP])

        lat, lon = position if isinstance(position, (list, tuple)) and len(position) == 2 else self.COORDINATES_PARIS

        red_icon_path = resource_path("assets/marker-red.png")
        blue_icon_path = resource_path("assets/marker-blue.png")

        init_params = {
            "tileUrl": tile_url,
            "lat": float(lat),
            "lon": float(lon),
            "zoom": int(zoom),
            "redIconUrl": QUrl.fromLocalFile(red_icon_path).toString(),
            "blueIconUrl": QUrl.fromLocalFile(blue_icon_path).toString(),
        }

        self.view = QWebEngineView(self)
        self.view.installEventFilter(self)

        settings = self.view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        self.channel = QWebChannel(self.view.page())
        self.bridge = _Bridge(init_params)
        self.channel.registerObject("bridge", self.bridge)
        self.view.page().setWebChannel(self.channel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        html_path = resource_path("editor/map_leaflet.html")
        url = QUrl.fromLocalFile(html_path)
        self.view.loadFinished.connect(self._on_load_finished)
        self.view.load(url)

        self.bridge.coordsPicked.connect(self._on_coords_picked)
        self.bridge.stateChanged.connect(self._on_state_changed)

        self.setStyleSheet(f"background: {self.style.BG_COLOR};")

    def eventFilter(self, obj, event):
        if obj is self.view:
            if event.type() == QEvent.Type.DragEnter:
                if event.mimeData().hasUrls():
                    event.acceptProposedAction()
                    return True
            if event.type() == QEvent.Type.Drop:
                self.file_dropped.emit(event)
                event.acceptProposedAction()
                return True

        return super().eventFilter(obj, event)

    def _on_load_finished(self, ok: bool) -> None:
        # Par défaut: pas d'image ouverte => picking désactivé
        self.set_picking_enabled(False)

    def set_picking_enabled(self, enabled: bool) -> None:
        js = f"setPickingEnabled({str(bool(enabled)).lower()});"
        self.view.page().runJavaScript(js)

    def _on_coords_picked(self, lat: float, lon: float) -> None:
        self.coords_picked.emit(lat, lon)

    def _on_state_changed(self, lat: float, lon: float, zoom: int) -> None:
        self._last_state = MapState(lat=lat, lon=lon, zoom=int(zoom))

    def set_tile_url(self, tile_url: str) -> None:
        self.view.page().runJavaScript(f"setTileUrl({json.dumps(tile_url)});")

    def set_view(self, lat: float, lon: float, zoom: int) -> None:
        self.view.page().runJavaScript(f"setView({lat}, {lon}, {int(zoom)});")

    def pan_to(self, lat: float, lon: float) -> None:
        self.view.page().runJavaScript(f"panTo({lat}, {lon});")

    def set_origin_marker(self, lat: float, lon: float) -> None:
        self.view.page().runJavaScript(f"setOriginMarker({lat}, {lon});")

    def set_new_marker(self, lat: float, lon: float) -> None:
        self.view.page().runJavaScript(f"setNewMarker({lat}, {lon});")

    def clear_new_marker(self) -> None:
        self.view.page().runJavaScript("clearNewMarker();")

    def clear_markers(self) -> None:
        self.view.page().runJavaScript("clearMarkers();")

    def add_marker_center_of_map(self) -> None:
        js = "getCenter();"

        def _cb(res):
            if not res:
                return
            try:
                lat = float(res.get("lat"))
                lon = float(res.get("lon"))
            except Exception:
                return
            self.set_new_marker(lat, lon)
            self.coords_picked.emit(lat, lon)

        self.view.page().runJavaScript(js, _cb)

    def get_state_for_persist(self) -> Tuple[Tuple[float, float], int]:
        if self._last_state:
            return (self._last_state.lat, self._last_state.lon), int(self._last_state.zoom)

        pos = self.config.get("position", self.COORDINATES_PARIS)
        zoom = self.config.get("zoom", self.DEFAULT_ZOOM)
        if isinstance(pos, (list, tuple)) and len(pos) == 2:
            return (float(pos[0]), float(pos[1])), int(zoom)
        return self.COORDINATES_PARIS, int(zoom)
