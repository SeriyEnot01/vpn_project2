#!/bin/bash

echo "=== VPN Server Setup ==="

# Проверка прав
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Установка WireGuard
echo "Installing WireGuard..."
apt update
apt install wireguard wireguard-tools -y

# Включение IP форвардинга
echo "Enabling IP forwarding..."
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# Создание директорий
mkdir -p /etc/wireguard/keys

# Генерация ключей сервера
echo "Generating server keys..."
cd /etc/wireguard
wg genkey | tee keys/server_private.key | wg pubkey > keys/server_public.key
chmod 600 keys/*.key

# Создание конфига
echo "Creating WireGuard config..."
cat > /etc/wireguard/wg0.conf << 'EOF'
[Interface]
Address = 10.66.66.1/24
ListenPort = 51820
PrivateKey =  # Вставьте сюда приватный ключ из keys/server_private.key

PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
PostUp = iptables -A FORWARD -o wg0 -j ACCEPT
PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
PostDown = iptables -D FORWARD -o wg0 -j ACCEPT
PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
EOF

# Замена приватного ключа в конфиге
PRIV_KEY=$(cat keys/server_private.key)
sed -i "s|PrivateKey = |PrivateKey = $PRIV_KEY|" /etc/wireguard/wg0.conf

echo "=== Setup Complete ==="
echo "Server public key: $(cat keys/server_public.key)"
echo "To start server: wg-quick up wg0"
echo "To enable autostart: systemctl enable wg-quick@wg0"