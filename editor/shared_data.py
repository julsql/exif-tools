class ImageData:
    def __init__(self):
        self.image_path = None
        self.pil_image = None
        self.tk_image = None

class MetadataData:
    def __init__(self):
        self.entries = {}

class StyleData:
    BG_COLOR = "white"
    FONT_COLOR = "black"
    BG_TAB_COLOR = "white"
    SELECT_COLOR = "black"
    BORDER_COLOR = "black"
    BG_DISABLE = "lightgray"
    FG_DISABLE = "gray"
    FONT_ERROR_COLOR = "red"
    MARKER_CIRCLE_COLOR = "blue"
    MARKER_OUTSIDE_COLOR = "#4285ff"
    MODE = "dark"
    EXIF_DATE_FORMAT = '%Y:%m:%d %H:%M:%S'
    DISPLAYED_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
