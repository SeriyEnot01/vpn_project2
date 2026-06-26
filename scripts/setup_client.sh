#!/bin/bash

echo "=== VPN Client Setup ==="

# Установка WireGuard
echo "Installing WireGuard..."
if command -v apt &> /dev/null; then
    apt update
    apt install wireguard wireguard-tools -y
elif command -v dnf &> /dev/null; then
    dnf install wireguard-tools -y
elif command -v pacman &> /dev/null; then
    pacman -S wireguard-tools
else
    echo "Unsupported package manager. Please install WireGuard manually."
    exit 1
fi

# Создание директории
mkdir -p ~/.config/vpn-client

# Генерация ключей
echo "Generating client keys..."
cd ~/.config/vpn-client
wg genkey | tee client_private.key | wg pubkey > client_public.key
chmod 600 *.key

echo "Client public key: $(cat client_public.key)"
echo "Add this key to server's wg0.conf"

# Создание конфига
echo "Creating client config..."
cat > ~/.config/vpn-client/wg0.conf << 'EOF'
[Interface]
PrivateKey =  # Вставьте сюда приватный ключ из client_private.key
Address = 10.66.66.2/24
DNS = 8.8.8.8

[Peer]
PublicKey = # Вставьте сюда публичный ключ сервера
Endpoint = SERVER_IP:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
EOF

echo "=== Setup Complete ==="
echo "1. Add your client public key to server's wg0.conf"
echo "2. Add server's public key to client config"
echo "3. Change SERVER_IP in client config"
echo "4. To start: wg-quick up ~/.config/vpn-client/wg0.conf"