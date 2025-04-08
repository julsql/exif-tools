import tkinter as tk
from tkinter import PhotoImage
from tkinter import filedialog

from PIL import Image, ImageTk

from editor.shared_data import ImageData, StyleData


class ImageWidget(tk.Frame):
    def __init__(self, parent, image_data: ImageData, style_data: StyleData):
        assets_path = "./assets/"
        icon_padding = 1
        icon_height = 20

        super().__init__(parent)
        self.image_data = image_data
        self.style_data = style_data

        self.parent = parent
        self.configure(bg=style_data.bg_color)

        # Créer la partie supérieure (40px de haut)
        self.top_frame = tk.Frame(self, height=20, bg=style_data.bg_tab_color)
        self.top_frame.pack(fill=tk.X, side=tk.TOP)
        self.bottom_border_frame = tk.Frame(self, height=1, bg=style_data.border_color)
        self.bottom_border_frame.pack(fill=tk.X, side=tk.TOP)

        # Ajouter les icônes à gauche
        self.save = self.load_icon(f"{assets_path}/{style_data.mode}/save.png", icon_height)
        self.save_as = self.load_icon(f"{assets_path}/{style_data.mode}/save_as.png", icon_height)
        self.add_photo = self.load_icon(f"{assets_path}/{style_data.mode}/folder_open.png", icon_height)
        self.close = self.load_icon(f"{assets_path}/{style_data.mode}/close.png", icon_height)

        self.icon_label1 = tk.Label(self.top_frame, image=self.save, bg=style_data.bg_tab_color)
        self.icon_label1.pack(side=tk.LEFT, padx=icon_padding)

        self.icon_label2 = tk.Label(self.top_frame, image=self.save_as, bg=style_data.bg_tab_color)
        self.icon_label2.pack(side=tk.LEFT, padx=icon_padding)

        self.icon_label3 = tk.Label(self.top_frame, image=self.add_photo, bg=style_data.bg_tab_color)
        self.icon_label3.pack(side=tk.LEFT, padx=icon_padding)

        self.icon_label4 = tk.Label(self.top_frame, image=self.close, bg=style_data.bg_tab_color)
        self.icon_label4.pack(side=tk.RIGHT, padx=icon_padding)

        self.image_area = tk.Label(self, bg=style_data.bg_tab_color, height=20)
        self.image_area.pack(fill=tk.BOTH, expand=True)

        self.icon_label3.bind("<Button-1>", self.open_file_dialog)
        self.icon_label4.bind("<Button-1>", self.close_image)

        self.loaded_image = None

    def load_icon(self, file_path, height):
        """Charge une icône et ajuste sa taille en maintenant le ratio."""
        icon = PhotoImage(file=file_path)
        ratio = icon.width() / icon.height()
        width = int(height * ratio)
        return icon.subsample(int(icon.width() / width), int(icon.height() / height))

    def close_image(self, event=None):
        """Ferme l'image."""
        self.loaded_image = None
        self.image_area.image = None
        self.image_area.config(image='')

        self.image_data.image_path = None
        self.image_data.pil_image = None
        self.image_data.tk_image = None
        self.event_generate("<<ImageUpdated>>")

    def open_file_dialog(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        """Charge l'image en entier et l'affiche dans la zone vide"""
        try:
            image = Image.open(file_path)

            tk_image = image
            # Si l'image est dans un format que Tkinter ne supporte pas, la convertir
            if image.format not in ['PNG', 'GIF', 'PPM', 'PGM']:
                tk_image = image.convert("RGB")

            # Redimensionner l'image pour l'affichage (en conservant la qualité)
            tk_image.thumbnail((self.winfo_width(), self.winfo_height()), Image.Resampling.LANCZOS)

            # Convertir l'image pour tkinter
            loaded_image = ImageTk.PhotoImage(tk_image)

            self.image_area.config(image=loaded_image)
            self.image_area.image = loaded_image

            self.image_data.image_path = file_path
            self.image_data.pil_image = image
            self.image_data.tk_image = loaded_image

            self.event_generate("<<ImageUpdated>>")

        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")

    def add_text(self, text):
        text_label = tk.Label(self, text=text, bg=self.style_data.bg_color, fg=self.style_data.font_color)
        text_label.pack(pady=10)
