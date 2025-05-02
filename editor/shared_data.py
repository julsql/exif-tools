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
    MODE = "dark"

    EXIF_DATE_FORMAT = '%Y:%m:%d %H:%M:%S'
    DISPLAYED_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
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

        self.FONT = ("Segoe UI", 14)
        self.TITLE_FONT = ("Segoe UI", 18, "bold")
