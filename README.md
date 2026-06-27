# 🔒 VPN Client

Клиент-серверное VPN-решение на базе WireGuard / AmneziaWG с графическим интерфейсом на PyQt5 и REST API для управления сервером.

---

## 📌 Описание проекта

Проект представляет собой VPN-клиент с графическим интерфейсом для подключения к удалённому VPN-серверу. Серверная часть работает на базе WireGuard (с поддержкой AmneziaWG для обхода блокировок) и предоставляет REST API для управления клиентами.

**Основные возможности:**
- Подключение и отключение VPN через графический интерфейс
- Генерация ключей на сервере
- REST API для удалённого управления сервером
- Поддержка WireGuard и AmneziaWG
- Кроссплатформенность (Windows / Linux)
---

## 📁 Структура проекта
vpn-project/
├── client/ # Клиентская часть (PyQt5 GUI)
│ ├── main.py
│ ├── wg_controller.py
│ ├── config_manager.py
│ ├── ui/
│ │ ├── main_window.py
│ │ └── settings_dialog.py
│ └── configs/
│ └── client.conf
├── server/ # Серверная часть (Python + Flask)
│ ├── api_server.py
│ ├── wg_manager.py
│ ├── key_manager.py
│ └── configs/
│ └── wg0.conf
└── README.md


---

## 🚀 Запуск клиента

### 1. Установка зависимостей

```bash
pip install -r client/requirements.txt
python client/main.py
pip install -r server/requirements.txt
python server/api_server.py
python server/api_server.py
После запуска API будет доступен по адресу:
http://<IP_сервера>:5000

Статус сервера
bash
curl http://89.127.203.246:5000/api/status

Добавить клиента
bash
curl -X POST http://89.127.203.246:5000/api/peer \
  -H "Content-Type: application/json" \
  -d '{"client_id": "1"}'
