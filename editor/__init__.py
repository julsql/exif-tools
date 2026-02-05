# python
# Package PyQt6 pour la migration progressive de l'app.

import os
import sys


def resource_path(relative_path):
    """Renvoie le chemin absolu vers un fichier, que ce soit depuis la source ou le bundle PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
