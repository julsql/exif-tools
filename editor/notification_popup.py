import tkinter as tk

from editor.shared_data import StyleData


class ToastNotification(tk.Toplevel):
    def __init__(self, parent, style_data: StyleData, message: str, duration: int = 2000):
        super().__init__(parent)
        self.overrideredirect(True)
        try:
            self.wm_attributes("-transparent", True)
        except tk.TclError:
            pass
        self.attributes("-topmost", True)
        self.configure(bg=style_data.BG_COLOR, bd=0)

        font = style_data.FONT

        self.frame = tk.Frame(
            self,
            bg=style_data.BG_COLOR,
            bd=0,
        )
        self.frame.pack(fill="both", expand=True)
        self.frame.config(highlightbackground=style_data.BORDER_COLOR, highlightthickness=1)

        # Label centré
        self.label = tk.Label(
            self.frame,
            text=message,
            font=font,
            bg=style_data.BG_COLOR,
            fg=style_data.FONT_COLOR,
            anchor="center",
            justify="center"
        )
        self.label.pack(ipadx=10, pady=5)

        self.update_idletasks()

        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()

        # Calcul de la position
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + 20
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.attributes("-alpha", 0.0)
        self.fade_in()
        self.after(duration, self.fade_out)

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            self.attributes("-alpha", alpha + 0.1)
            self.after(30, self.fade_in)

    def fade_out(self):
        alpha = self.attributes("-alpha")
        if alpha > 0:
            self.attributes("-alpha", alpha - 0.1)
            self.after(30, self.fade_out)
        else:
            self.destroy()
