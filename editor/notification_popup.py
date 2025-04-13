import tkinter as tk
from tkinter import ttk

from editor.shared_data import StyleData


class NotificationPopup(tk.Toplevel):
    def __init__(self, style_data: StyleData, title="Notification", message="Ceci est un message.",
                 width=300, height=150):
        super().__init__(None)

        self.title(title)
        self.resizable(False, False)
        self.geometry(f"{width}x{height}")
        self.attributes("-topmost", True)
        self.configure(bg=style_data.BG_COLOR)

        # Pour certains OS (Windows) : effet semi-transparent pour "modern look"
        self.wm_attributes("-alpha", 0.97)

        # Centre la fenêtre
        self._center_window(width, height)

        # Style ttk
        style = ttk.Style(self)
        style.theme_use("default")

        # Label stylé
        style.configure("Notification.TLabel",
                        background=style_data.BG_COLOR,
                        foreground=style_data.FONT_COLOR,
                        font=style_data.FONT)

        label = ttk.Label(self, text=message, style="Notification.TLabel",
                          wraplength=width - 20, anchor="center", justify="center")
        label.pack(pady=20, padx=10)

        # Bouton stylé
        style.configure("Notification.TButton",
                        background=style_data.BUTTON_COLOR,
                        foreground=style_data.FONT_COLOR,
                        borderwidth=0,
                        focusthickness=0,
                        padding=6)
        style.map("Notification.TButton",
                  background=[('active', style_data.BUTTON_HOVER_COLOR)])

        close_btn = ttk.Button(self, text="Fermer", command=self.destroy, style="Notification.TButton")
        close_btn.pack(pady=5)

        self.grab_set()

    def _center_window(self, width, height):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
