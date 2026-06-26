import subprocess
import os
import json
from pathlib import Path


class KeyManager:
    def __init__(self, keys_dir="/etc/wireguard/keys"):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(parents=True, exist_ok=True)

    def generate_server_keys(self):
        """Генерирует ключи сервера"""
        priv_path = self.keys_dir / "server_private.key"
        pub_path = self.keys_dir / "server_public.key"

        if not priv_path.exists():
            # Генерируем приватный
            result = subprocess.run(['wg', 'genkey'], capture_output=True, text=True)
            with open(priv_path, 'w') as f:
                f.write(result.stdout.strip())
            os.chmod(priv_path, 0o600)

            # Генерируем публичный
            with open(priv_path, 'r') as f:
                result = subprocess.run(['wg', 'pubkey'],
                                        input=f.read(),
                                        capture_output=True, text=True)
            with open(pub_path, 'w') as f:
                f.write(result.stdout.strip())
            os.chmod(pub_path, 0o600)

        return self.get_server_keys()

    def get_server_keys(self):
        """Возвращает ключи сервера"""
        priv_path = self.keys_dir / "server_private.key"
        pub_path = self.keys_dir / "server_public.key"

        if priv_path.exists() and pub_path.exists():
            with open(priv_path, 'r') as f:
                private = f.read().strip()
            with open(pub_path, 'r') as f:
                public = f.read().strip()
            return {'private': private, 'public': public}
        return None

    def generate_client_keys(self, client_id):
        """Генерирует ключи для клиента"""
        priv_path = self.keys_dir / f"client_{client_id}_private.key"
        pub_path = self.keys_dir / f"client_{client_id}_public.key"

        # Генерируем приватный
        result = subprocess.run(['wg', 'genkey'], capture_output=True, text=True)
        with open(priv_path, 'w') as f:
            f.write(result.stdout.strip())
        os.chmod(priv_path, 0o600)

        # Генерируем публичный
        with open(priv_path, 'r') as f:
            result = subprocess.run(['wg', 'pubkey'],
                                    input=f.read(),
                                    capture_output=True, text=True)
        with open(pub_path, 'w') as f:
            f.write(result.stdout.strip())
        os.chmod(pub_path, 0o600)

        return {
            'id': client_id,
            'private': self._read_key(priv_path),
            'public': self._read_key(pub_path)
        }

    def get_client_keys(self, client_id):
        """Возвращает ключи клиента"""
        priv_path = self.keys_dir / f"client_{client_id}_private.key"
        pub_path = self.keys_dir / f"client_{client_id}_public.key"

        if priv_path.exists() and pub_path.exists():
            return {
                'id': client_id,
                'private': self._read_key(priv_path),
                'public': self._read_key(pub_path)
            }
        return None

    def delete_client_keys(self, client_id):
        """Удаляет ключи клиента"""
        priv_path = self.keys_dir / f"client_{client_id}_private.key"
        pub_path = self.keys_dir / f"client_{client_id}_public.key"

        if priv_path.exists():
            priv_path.unlink()
        if pub_path.exists():
            pub_path.unlink()

    def _read_key(self, path):
        with open(path, 'r') as f:
            return f.read().strip()