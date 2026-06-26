import os
import json
import shutil


class ConfigManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/vpn-client")
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.default_config = os.path.join(os.path.dirname(__file__), "configs", "client.conf")

        # Создаём директорию
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(__file__), "configs"), exist_ok=True)

        self._load_settings()

    def _load_settings(self):
        """Загружает настройки"""
        self.settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                pass

    def _save_settings(self):
        """Сохраняет настройки"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def get_config_path(self):
        """Возвращает путь к конфигу"""
        config_path = self.settings.get('config_path')
        if config_path and os.path.exists(config_path):
            return config_path

        # Создаём дефолтный конфиг
        return self.create_default_config()

    def set_config_path(self, path):
        """Устанавливает путь к конфигу"""
        self.settings['config_path'] = path
        self._save_settings()

    def create_default_config(self):
        """Создаёт дефолтный конфиг"""
        config_path = os.path.join(self.config_dir, "wg0.conf")

        if not os.path.exists(config_path):
            # Копируем шаблон
            template = os.path.join(os.path.dirname(__file__), "configs", "client.conf.example")
            if os.path.exists(template):
                shutil.copy(template, config_path)
            else:
                # Создаём стандартный конфиг
                with open(config_path, 'w') as f:
                    f.write("""[Interface]
PrivateKey = CHANGE_ME
Address = 10.66.66.2/24
DNS = 8.8.8.8

[Peer]
PublicKey = CHANGE_ME
Endpoint = CHANGE_ME:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
""")
                os.chmod(config_path, 0o600)

        return config_path