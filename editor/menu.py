import tkinter as tk


class MenuBar:
    def __init__(self, root, reset_callback):
        self.root = root
        self.reset_callback = reset_callback

        # Barre de menus
        menu_bar = tk.Menu(root)

        # Menu Outils
        outils_menu = tk.Menu(menu_bar, tearoff=0)
        outils_menu.add_command(label="Réinitialiser la fenêtre", command=self.reset_callback)
        menu_bar.add_cascade(label="Fenêtre", menu=outils_menu)

        # Ajouter la barre de menu à la fenêtre principale
        root.config(menu=menu_bar)
