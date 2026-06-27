import subprocess
import os
import platform
import shutil
import re
import time


class WGController:
    def __init__(self):
        self.os_type = platform.system()
        self.wg_interface = "wg0"  # для Linux
        if self.os_type == "Windows":
            self.wg_interface = "client"
        self.wg_path = self._find_wg()
        self._check_wireguard()

    def _find_wg(self):
        """Находит путь к wg.exe на Windows"""
        if self.os_type == "Windows":
            paths = [
                r"C:\Program Files\WireGuard\wg.exe",
                r"C:\Program Files (x86)\WireGuard\wg.exe",
                shutil.which("wg.exe") or ""
            ]
            for path in paths:
                if path and os.path.exists(path):
                    return path
            return "wg.exe"
        return "wg"

    def _check_wireguard(self):
        """Проверяет наличие WireGuard"""
        if self.os_type == "Windows":
            if not os.path.exists(self.wg_path):
                raise Exception("WireGuard not found. Please install WireGuard for Windows.")
        else:
            wg_path = shutil.which("wg")
            if not wg_path:
                raise Exception("WireGuard not found. Please install WireGuard.")

    def connect(self, config_path):
        """Подключает VPN на Windows (интерфейс уже создан через GUI)"""
        try:
            if self.os_type == "Windows":
                # Проверяем, есть ли интерфейс client
                check = subprocess.run(
                    [self.wg_path, 'show'],
                    capture_output=True,
                    text=True
                )

                if "interface: client" not in check.stdout:
                    print("WireGuard interface 'client' not found.")
                    return False

                if "latest handshake" in check.stdout:
                    print("VPN already connected (handshake present)")
                    return True

                print("Interface found, trying to activate...")
                subprocess.run(
                    ['netsh', 'interface', 'set', 'interface', 'client', 'enabled'],
                    capture_output=True,
                    text=True
                )

                # Проверяем снова
                time.sleep(2)
                check2 = subprocess.run(
                    [self.wg_path, 'show'],
                    capture_output=True,
                    text=True
                )

                if "latest handshake" in check2.stdout:
                    return True

                # Если handshake всё ещё нет — пробуем перезагрузить интерфейс
                print("No handshake, trying to reset interface...")
                subprocess.run(
                    [self.wg_path, 'setconf', 'client', config_path],
                    capture_output=True,
                    text=True
                )
                time.sleep(2)

                check3 = subprocess.run(
                    [self.wg_path, 'show'],
                    capture_output=True,
                    text=True
                )

                return "latest handshake" in check3.stdout

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
                # Отключаем интерфейс
                subprocess.run(
                    ['netsh', 'interface', 'set', 'interface', 'WireGuard', 'disabled'],
                    capture_output=True,
                    text=True
                )
                # Очищаем конфиг
                subprocess.run(
                    [self.wg_path, 'setconf', 'wg0', ''],
                    capture_output=True,
                    text=True
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
                [self.wg_path, 'show'],
                capture_output=True,
                text=True
            )
            return "interface:" in result.stdout and (
                    "wg0" in result.stdout or "WireGuard" in result.stdout
            )
        except:
            return False

    def _has_handshake(self):
        """Проверяет, есть ли реальное соединение с сервером"""
        try:
            result = subprocess.run(
                [self.wg_path, 'show'],
                capture_output=True,
                text=True
            )
            return "latest handshake" in result.stdout
        except:
            return False

    def get_status(self):
        """Получает статистику"""
        try:
            result = subprocess.run(
                [self.wg_path, 'show'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return False, {}

            stats = {
                'rx': 0,
                'tx': 0,
                'handshake': 0
            }

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
        value = float(value)
        if unit == 'KiB':
            return int(value * 1024)
        elif unit == 'MiB':
            return int(value * 1024 * 1024)
        elif unit == 'GiB':
            return int(value * 1024 * 1024 * 1024)
        else:
            return int(value)