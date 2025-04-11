import json
import os


class ConfigManager:
    def __init__(self):
        home = os.path.expanduser("~")
        self.path = os.path.join(home, ".exiftools", "window_config.json")
        self.config = {}
        self.create_folder()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"[ConfigManager] Erreur chargement config: {e}")
                self.config = {}

    def save(self):
        try:
            with open(self.path, "w") as f:
                json.dump(self.config, f)
        except Exception as e:
            print(f"[ConfigManager] Erreur sauvegarde config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value

    def create_folder(self):
        folder = os.path.dirname(self.path)
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[ConfigManager] Dossier config créé : {folder}")
