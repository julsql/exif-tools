from tkinter import PhotoImage

class ExifEditorApp:
    def __init__(self, root):
        self.root = root
        icon = PhotoImage(file="./assets/icon.png")

        root.iconphoto(True, icon)
