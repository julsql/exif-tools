class ImageData:
    def __init__(self):
        self.image_path = None
        self.pil_image = None
        self.tk_image = None

class MetadataData:
    def __init__(self):
        self.entries = {}

class StyleData:
    def __init__(self):
        self.bg_color = "white"
        self.font_color = "black"
        self.bg_tab_color = "white"
        self.select_color = "black"
        self.border_color = "black"
        self.bg_disable = "lightgray"
        self.fg_disable = "gray"
        self.font_error_color = "red"

        self.marker_circle_color = "blue"
        self.marker_outside_color = "#4285ff"

        self.mode = "dark"

        self.exif_date_format = '%Y:%m:%d %H:%M:%S'
        self.displayed_date_format = '%Y-%m-%d %H:%M:%S'
