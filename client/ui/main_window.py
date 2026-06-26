from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QTextEdit, QProgressBar,
                             QListWidget)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal

from client.wg_controller import WGController
from client.config_manager import ConfigManager
from client.ui.settings_dialog import SettingsDialog

import platform


class VPNWorker(QThread):
    """Воркер для асинхронных операций"""
    status_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)
    stats_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(bool)

    def __init__(self, controller, action, config_path=None):
        super().__init__()
        self.controller = controller
        self.action = action
        self.config_path = config_path

    def run(self):
        try:
            if self.action == 'connect':
                success = self.controller.connect(self.config_path)
            elif self.action == 'disconnect':
                success = self.controller.disconnect()
            elif self.action == 'status':
                success, stats = self.controller.get_status()
                if success:
                    self.stats_signal.emit(stats)
                self.finished_signal.emit(success)
                return
            else:
                success = False

            if success:
                self.status_signal.emit("Connected")
                self.log_signal.emit("✓ VPN tunnel established")
            else:
                self.status_signal.emit("Failed")
                self.log_signal.emit("✗ Failed to establish VPN")

            self.finished_signal.emit(success)
        except Exception as e:
            self.log_signal.emit(f"✗ Error: {str(e)}")
            self.finished_signal.emit(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = WGController()
        self.config_manager = ConfigManager()
        self.worker = None
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_stats)

        self.init_ui()
        self.check_status()

    def init_ui(self):
        self.setWindowTitle("VPN Client")
        self.setFixedSize(480, 700)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("🔒 VPN Client")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Список серверов
        layout.addWidget(QLabel("Select Server:"))
        self.server_list = QListWidget()
        self.server_list.addItem("My Server (89.127.203.246)")
        self.server_list.setFixedHeight(80)
        layout.addWidget(self.server_list)

        # Статус
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.StyledPanel)
        status_layout = QVBoxLayout()

        self.status_indicator = QLabel("⚪")
        self.status_indicator.setStyleSheet("font-size: 48px;")
        self.status_indicator.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_indicator)

        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: gray;")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)

        status_frame.setLayout(status_layout)
        layout.addWidget(status_frame)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_connect = QPushButton("🔗 Connect")
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.btn_connect.clicked.connect(self.toggle_vpn)

        self.btn_settings = QPushButton("⚙️")
        self.btn_settings.setFixedWidth(50)
        self.btn_settings.clicked.connect(self.show_settings)

        btn_layout.addWidget(self.btn_connect)
        btn_layout.addWidget(self.btn_settings)
        layout.addLayout(btn_layout)

        # Статистика
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.StyledPanel)
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(QLabel("📊 Statistics"))

        stats_grid = QHBoxLayout()
        self.rx_label = QLabel("↓ 0 B")
        self.tx_label = QLabel("↑ 0 B")
        self.time_label = QLabel("⏱ 00:00:00")
        stats_grid.addWidget(self.rx_label)
        stats_grid.addWidget(self.tx_label)
        stats_grid.addWidget(self.time_label)
        stats_layout.addLayout(stats_grid)

        # Прогресс-бар для сигнала
        self.signal_bar = QProgressBar()
        self.signal_bar.setMaximum(4)
        self.signal_bar.setValue(0)
        self.signal_bar.setFixedHeight(5)
        stats_layout.addWidget(self.signal_bar)

        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)

        # Логи
        layout.addWidget(QLabel("📜 Logs:"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        self.log_area.setPlaceholderText("VPN logs will appear here...")
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.log_area)

        central.setLayout(layout)

        # Настройка статус-таймера
        self.status_timer.start(2000)  # Обновление каждые 2 секунды

        # Логируем начало
        self.log("VPN Client started")
        self.log(f"OS: {platform.system()} {platform.release()}")
        self.log(f"Config path: {self.config_manager.get_config_path()}")

    def toggle_vpn(self):
        """Включает/выключает VPN"""
        if self.btn_connect.text() == "🔗 Connect":
            self.log("Connecting to VPN...")
            self.btn_connect.setEnabled(False)
            self.btn_connect.setText("Connecting...")

            # Выбираем конфиг
            config_path = self.config_manager.get_config_path()

            self.worker = VPNWorker(self.controller, 'connect', config_path)
            self.worker.status_signal.connect(self.update_status)
            self.worker.log_signal.connect(self.log)
            self.worker.finished_signal.connect(self.on_connect_finished)
            self.worker.start()
        else:
            self.log("Disconnecting...")
            self.btn_connect.setEnabled(False)

            self.worker = VPNWorker(self.controller, 'disconnect')
            self.worker.status_signal.connect(self.update_status)
            self.worker.log_signal.connect(self.log)
            self.worker.finished_signal.connect(self.on_disconnect_finished)
            self.worker.start()

    def on_connect_finished(self, success):
        self.btn_connect.setEnabled(True)
        if success:
            self.btn_connect.setText("🔒 Disconnect")
            self.btn_connect.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
        else:
            self.btn_connect.setText("🔗 Connect")
            self.btn_connect.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)

    def on_disconnect_finished(self, success):
        self.btn_connect.setEnabled(True)
        self.btn_connect.setText("🔗 Connect")
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def update_status(self, text):
        if text == "Connected":
            self.status_indicator.setText("🟢")
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        elif text == "Disconnected":
            self.status_indicator.setText("🔴")
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: gray; font-weight: bold;")
        else:
            self.status_indicator.setText("⚪")
            self.status_label.setText(text)

    def update_stats(self):
        """Обновляет статистику"""
        if self.controller.is_connected():
            worker = VPNWorker(self.controller, 'status')
            worker.stats_signal.connect(self.display_stats)
            worker.start()

    def display_stats(self, stats):
        rx = stats.get('rx', 0)
        tx = stats.get('tx', 0)
        self.rx_label.setText(f"↓ {self.format_bytes(rx)}")
        self.tx_label.setText(f"↑ {self.format_bytes(tx)}")

        # Сигнал (пример)
        self.signal_bar.setValue(4)

    def check_status(self):
        """Проверяет начальный статус"""
        if self.controller.is_connected():
            self.on_connect_finished(True)
            self.log("VPN already connected")
        else:
            self.update_status("Disconnected")

    def format_bytes(self, bytes):
        """Форматирует байты в читаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"

    def log(self, message):
        """Добавляет сообщение в лог"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")

    def show_settings(self):
        """Показывает окно настроек"""
        dialog = SettingsDialog(self)
        dialog.exec_()