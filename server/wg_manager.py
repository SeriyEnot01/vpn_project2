import subprocess
import os
import json
from pathlib import Path


class WireGuardManager:
    def __init__(self, config_path="/etc/wireguard/wg0.conf"):
        self.config_path = config_path
        self._check_root()

    def _check_root(self):
        """Проверяет права root"""
        if os.geteuid() != 0:
            raise PermissionError("This script must be run as root")

    def start(self):
        """Запускает WireGuard"""
        try:
            subprocess.run(['wg-quick', 'up', 'wg0'], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to start: {e.stderr.decode()}")
            return False

    def stop(self):
        """Останавливает WireGuard"""
        try:
            subprocess.run(['wg-quick', 'down', 'wg0'], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop: {e.stderr.decode()}")
            return False

    def restart(self):
        """Перезапускает WireGuard"""
        self.stop()
        return self.start()

    def add_peer(self, public_key, allowed_ip, persistent_keepalive=25):
        """
        Добавляет нового клиента
        """
        try:
            cmd = [
                'wg', 'set', 'wg0',
                'peer', public_key,
                'allowed-ips', allowed_ip,
                'persistent-keepalive', str(persistent_keepalive)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to add peer: {e.stderr.decode()}")
            return False

    def remove_peer(self, public_key):
        """Удаляет клиента"""
        try:
            subprocess.run(['wg', 'set', 'wg0', 'peer', public_key, 'remove'],
                           check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove peer: {e.stderr.decode()}")
            return False

    def get_status(self):
        """Получает статус подключений"""
        try:
            result = subprocess.run(['wg', 'show'], capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr.decode()}"

    def get_peers(self):
        """Получает список подключенных пиров"""
        try:
            result = subprocess.run(['wg', 'show', 'wg0', 'peers'],
                                    capture_output=True, text=True)
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except:
            return []

    def get_peer_info(self, public_key):
        """Получает информацию о конкретном пире"""
        try:
            # wg show wg0 peers
            # или парсим полный вывод
            output = self.get_status()
            # Простой парсинг (можно улучшить)
            lines = output.split('\n')
            in_peer = False
            info = {}
            for line in lines:
                if line.strip().startswith('peer:'):
                    if public_key in line:
                        in_peer = True
                    else:
                        in_peer = False
                elif in_peer:
                    if 'endpoint' in line:
                        info['endpoint'] = line.split(':')[-1].strip()
                    elif 'allowed ips' in line:
                        info['allowed_ips'] = line.split(':')[-1].strip()
                    elif 'latest handshake' in line:
                        info['latest_handshake'] = line.split(':')[-1].strip()
                    elif 'transfer' in line:
                        info['transfer'] = line.split(':')[-1].strip()
            return info
        except:
            return {}