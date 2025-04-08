import tkinter as tk


class MenuBar:
    def __init__(self, root, reset_callback, open_image_callback, close_image_callback, reset_values):
        self.root = root

        # Barre de menus
        menu_bar = tk.Menu(root)

        # Menu Outils
        outils_menu = tk.Menu(menu_bar, tearoff=0)
        outils_menu.add_command(label="Réinitialiser la fenêtre", command=reset_callback)
        outils_menu.add_command(label="Réinitialiser les valeurs", command=reset_values)
        menu_bar.add_cascade(label="Fenêtre", menu=outils_menu)

        # Menu Fichier
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Ouvrir une image", command=open_image_callback)
        file_menu.add_command(label="Fermer l'image", command=close_image_callback)
        menu_bar.add_cascade(label="Fichier", menu=file_menu)

        # Ajouter la barre de menu à la fenêtre principale
        root.config(menu=menu_bar)
