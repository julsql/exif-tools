import json
import os


class ConfigManager:
    def __init__(self, path="config/window_config.json"):
        self.path = path
        self.config = {}

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
