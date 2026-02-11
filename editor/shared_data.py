# python
class ImageData:
    def __init__(self):
        self.image_path = None
        self.pil_image = None
        self.tk_image = None
        self.image_open = False


class MetadataData:
    def __init__(self):
        self.entries = {}


class StyleData:
    EXIF_DATE_FORMAT = '%Y:%m:%d %H:%M:%S'
    DISPLAYED_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    ACCEPTED_DATE_FORMATS = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H-%M-%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d %H-%M',
        '%Y-%m-%d',
        '%Y:%m:%d %H:%M:%S',
        '%Y:%m:%d %H-%M-%S',
        '%Y:%m:%d %H:%M',
        '%Y:%m:%d %H-%M',
        '%Y:%m:%d',
        '%d/%m/%Y %H-%M-%S',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y %H-%M',
        '%d/%m/%Y',
    ]
    FONT = ("Segoe UI", 14)
    TITLE_FONT = ("Segoe UI", 18, "bold")
    SELECT_CURSOR = "hand2"
    DEFAULT_MAP = "french"
    DEFAULT_SPECIE = True
    MAPS = {"french": "https://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
            "international": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"}
    MAPS_SWITCH_LABEL = {
        "french": "Utiliser une carte française",
        "international": "Utiliser une carte internationale"
    }
    EXTENSIONS_LIST = [".jpg", ".jpeg", ".png", ".gif"]

    SPECIE_SWITCH_LABEL = {
        True: "Désactiver la reconnaissance d'espèce",
        False: "Activer la reconnaissance d'espèce"
    }

    def __init__(self, mode: str = "dark"):
        self.MODE = "dark"
        self.set_mode(mode)

    def set_mode(self, mode: str) -> None:
        mode = (mode or "dark").lower()
        self.MODE = "light" if mode == "light" else "dark"

        if self.MODE == "dark":
            self.BG_COLOR = "#1e1e1e"
            self.FONT_COLOR = "#f0f0f0"
            self.BG_TAB_COLOR = "#2c2c2c"
            self.SELECT_COLOR = "#61dafb"
            self.BORDER_COLOR = "#3c3c3c"
            self.BG_DISABLE = "#444444"
            self.FG_DISABLE = "#888888"
            self.FONT_ERROR_COLOR = "#ff5555"
            self.BUTTON_COLOR = "#444444"
            self.BUTTON_HOVER_COLOR = "#666666"
        else:
            self.BG_COLOR = "#f5f5f5"
            self.FONT_COLOR = "#1e1e1e"
            self.BG_TAB_COLOR = "#ffffff"
            self.SELECT_COLOR = "#007acc"
            self.BORDER_COLOR = "#cccccc"
            self.BG_DISABLE = "#e0e0e0"
            self.FG_DISABLE = "#888888"
            self.FONT_ERROR_COLOR = "#d32f2f"
            self.BUTTON_COLOR = "#e0e0e0"
            self.BUTTON_HOVER_COLOR = "#d0d0d0"