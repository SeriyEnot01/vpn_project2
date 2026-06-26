import subprocess
import sys
import os
import platform

def get_os_info():
    """Возвращает информацию об ОС"""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'architecture': platform.machine()
    }

def check_wireguard_installed():
    """Проверяет установлен ли WireGuard"""
    try:
        subprocess.run(['wg', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_network_interfaces():
    """Возвращает список сетевых интерфейсов"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
            return result.stdout
        else:
            result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
            return result.stdout
    except:
        return "Failed to get interfaces"

def get_ip_address(interface='wg0'):
    """Возвращает IP адрес интерфейса"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['netsh', 'interface', 'ip', 'show', 'addresses'],
                                  capture_output=True, text=True)
            # Простой парсинг для Windows
            for line in result.stdout.split('\n'):
                if interface in line:
                    return line.split('IP Address:')[-1].strip()
        else:
            result = subprocess.run(['ip', '-br', 'addr', 'show', interface],
                                  capture_output=True, text=True)
            parts = result.stdout.split()
            if len(parts) >= 3:
                return parts[2].split('/')[0]
    except:
        pass
    return None

def show_notification(title, message):
    """Показывает системное уведомление"""
    system = platform.system()
    try:
        if system == "Linux":
            subprocess.run(['notify-send', title, message], check=False)
        elif system == "Darwin":
            subprocess.run(['osascript', '-e', f'display notification "{message}" with title "{title}"'],
                         check=False)
        elif system == "Windows":
            subprocess.run(['powershell', '-command',
                          f'[System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'],
                         check=False)
    except:
        pass  # Если уведомление не работает, игнорируем