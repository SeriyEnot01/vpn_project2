from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # Путь к конфигу
        layout.addWidget(QLabel("Config File:"))
        config_layout = QHBoxLayout()
        self.config_path = QLineEdit()
        self.config_path.setPlaceholderText("Path to WireGuard config")
        self.config_path.setText("configs/client.conf")
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_config)
        config_layout.addWidget(self.config_path)
        config_layout.addWidget(self.browse_btn)
        layout.addLayout(config_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def browse_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Config File", "", "Config Files (*.conf)"
        )
        if file_path:
            self.config_path.setText(file_path)

    def save(self):
        # Сохраняем настройки
        from client.config_manager import ConfigManager
        manager = ConfigManager()
        manager.set_config_path(self.config_path.text())
        self.accept()