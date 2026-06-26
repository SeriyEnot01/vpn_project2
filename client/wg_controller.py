import subprocess
import os
import platform
import shutil
import re


class WGController:
    def __init__(self):
        self.os_type = platform.system()
        self._check_wireguard()

    def _check_wireguard(self):
        """Проверяет наличие WireGuard"""
        if self.os_type == "Windows":
            wg_path = shutil.which("wg.exe")
            if not wg_path:
                raise Exception("WireGuard not found. Please install WireGuard for Windows.")
        else:
            wg_path = shutil.which("wg")
            if not wg_path:
                raise Exception("WireGuard not found. Please install WireGuard.")

    def connect(self, config_path):
        """Подключает VPN"""
        try:
            if self.os_type == "Windows":
                # На Windows используем wg
                result = subprocess.run(
                    ['wg', 'setconf', 'wg0', config_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"Error: {result.stderr}")
                    return False

                # Активируем интерфейс
                subprocess.run(
                    ['netsh', 'interface', 'set', 'interface', 'wg0', 'enabled'],
                    capture_output=True
                )
            else:
                # Linux/macOS
                subprocess.run(
                    ['sudo', 'wg-quick', 'up', config_path],
                    check=True,
                    capture_output=True
                )
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Отключает VPN"""
        try:
            if self.os_type == "Windows":
                subprocess.run(
                    ['netsh', 'interface', 'set', 'interface', 'wg0', 'disabled'],
                    capture_output=True
                )
            else:
                subprocess.run(
                    ['sudo', 'wg-quick', 'down', 'wg0'],
                    check=True,
                    capture_output=True
                )
            return True
        except Exception as e:
            print(f"Disconnection error: {e}")
            return False

    def is_connected(self):
        """Проверяет статус"""
        try:
            result = subprocess.run(
                ['wg', 'show'],
                capture_output=True,
                text=True
            )
            return "interface: wg0" in result.stdout
        except:
            return False

    def get_status(self):
        """Получает статистику"""
        try:
            result = subprocess.run(
                ['wg', 'show', 'wg0'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return False, {}

            # Парсим вывод
            stats = {
                'rx': 0,
                'tx': 0,
                'handshake': 0
            }

            # Ищем transfer: 123.45 MiB received, 67.89 MiB sent
            match = re.search(r'transfer: ([\d.]+) (MiB|KiB|GiB) received, ([\d.]+) (MiB|KiB|GiB) sent', result.stdout)
            if match:
                rx = self._parse_bytes(match.group(1), match.group(2))
                tx = self._parse_bytes(match.group(3), match.group(4))
                stats['rx'] = rx
                stats['tx'] = tx

            return True, stats
        except Exception as e:
            print(f"Status error: {e}")
            return False, {}

    def _parse_bytes(self, value, unit):
        """Парсит размер в байты"""
        value = float(value)
        if unit == 'KiB':
            return int(value * 1024)
        elif unit == 'MiB':
            return int(value * 1024 * 1024)
        elif unit == 'GiB':
            return int(value * 1024 * 1024 * 1024)
        else:
            return int(value)