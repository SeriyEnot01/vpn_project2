from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from client.wg_controller import WGController
from client.config_manager import ConfigManager
import platform


class MainWindow(QMainWindow):
    #Создаёт контроллер, менеджер конфигов, устанавливает и запускает окно
    def __init__(self):
        super().__init__()
        self.controller = WGController()
        self.config_manager = ConfigManager()
        self.worker = None
        self.is_connected = False
        self.setWindowTitle("VPN Client")
        self.setFixedSize(400, 550)
        self.init_ui()
    
    #Создаёт все виджеты
    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("🔒 VPN Client")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # IP сервера
        ip_label = QLabel("Server: 89.127.203.246")
        ip_label.setAlignment(Qt.AlignCenter)
        ip_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(ip_label)

        # Статус
        self.status_label = QLabel("⚪ DISCONNECTED")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: gray;")
        layout.addWidget(self.status_label)

        # Кнопки (Connect + Disconnect в ряд)
        btn_layout = QHBoxLayout()

        self.btn_connect = QPushButton("CONNECT")
        self.btn_connect.clicked.connect(self.do_connect)
        self.btn_connect.setStyleSheet("""
            QPushButton {
                font-size: 14px; 
                padding: 10px; 
                background: #4CAF50; 
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        btn_layout.addWidget(self.btn_connect)

        self.btn_disconnect = QPushButton("DISCONNECT")
        self.btn_disconnect.clicked.connect(self.do_disconnect)
        self.btn_disconnect.setStyleSheet("""
            QPushButton {
                font-size: 14px; 
                padding: 10px; 
                background: #f44336; 
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        self.btn_disconnect.setEnabled(False)
        btn_layout.addWidget(self.btn_disconnect)

        layout.addLayout(btn_layout)

        # Логи
        layout.addWidget(QLabel("📜 Logs:"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(200)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.log_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.log("VPN Client started")
        self.log(f"Server: 89.127.203.246")
        
    # Подключает VPN, меняет статус на "🟢 CONNECTED", блокирует CONNECT, активирует DISCONNECT
    def do_connect(self):
        self.log("Connecting to 89.127.203.246...")
        config_path = self.config_manager.get_config_path()
        success = self.controller.connect(config_path)
        if success:
            self.is_connected = True
            self.status_label.setText("🟢 CONNECTED")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            self.log("✓ Connected to VPN")
        else:
            self.log("✗ Failed to connect")
            
    #Отключает VPN, меняет статус на "⚪ DISCONNECTED", активирует CONNECT, блокирует DISCONNECT
    def do_disconnect(self):
        self.log("Disconnecting...")
        self.controller.disconnect()
        self.is_connected = False
        self.status_label.setText("⚪ DISCONNECTED")
        self.status_label.setStyleSheet("color: gray; font-weight: bold;")
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.log("✓ Disconnected")
        
    #Добавляет сообщение с временной меткой в область логов
    def log(self, msg):
        from datetime import datetime
        self.log_area.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
