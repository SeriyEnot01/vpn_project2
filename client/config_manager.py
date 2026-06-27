import os
import json
import shutil


class ConfigManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/vpn-client")
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.default_config = os.path.join(os.path.dirname(__file__), "configs", "client.conf")

        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(__file__), "configs"), exist_ok=True)
        self._load_settings()

    def _load_settings(self):
        self.settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                pass

    def _save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def get_config_path(self):
        project_config = os.path.join(os.path.dirname(__file__), "configs", "client.conf")

        if os.path.exists(project_config):
            return project_config
        config_path = os.path.join(self.config_dir, "wg0.conf")
        if not os.path.exists(config_path):
            import shutil
            shutil.copy(project_config, config_path)

        return config_path
        return self.create_default_config()

    def set_config_path(self, path):
        self.settings['config_path'] = path
        self._save_settings()