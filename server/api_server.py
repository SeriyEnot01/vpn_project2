from flask import Flask, request, jsonify
from wg_manager import WireGuardManager
from key_manager import KeyManager
import threading

app = Flask(__name__)
wg = WireGuardManager()
keys = KeyManager()


@app.route('/api/status', methods=['GET'])
def get_status():
    """Получить статус сервера"""
    try:
        status = wg.get_status()
        return jsonify({'status': 'success', 'data': status})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/peer', methods=['POST'])
def add_peer():
    """Добавить нового клиента"""
    try:
        data = request.json
        client_id = data.get('client_id')
        if not client_id:
            return jsonify({'status': 'error', 'message': 'client_id required'}), 400

        # Генерируем ключи
        client_keys = keys.generate_client_keys(client_id)

        # Добавляем клиента в WireGuard
        wg.add_peer(
            public_key=client_keys['public'],
            allowed_ip=f"10.66.66.{int(client_id) + 2}/32"  # 10.66.66.2, 10.66.66.3, ...
        )

        return jsonify({
            'status': 'success',
            'client': client_keys
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/peer/<client_id>', methods=['DELETE'])
def remove_peer(client_id):
    """Удалить клиента"""
    try:
        client_keys = keys.get_client_keys(client_id)
        if not client_keys:
            return jsonify({'status': 'error', 'message': 'Client not found'}), 404

        wg.remove_peer(client_keys['public'])
        keys.delete_client_keys(client_id)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/peer/<client_id>', methods=['GET'])
def get_peer(client_id):
    """Получить информацию о клиенте"""
    try:
        client_keys = keys.get_client_keys(client_id)
        if not client_keys:
            return jsonify({'status': 'error', 'message': 'Client not found'}), 404

        info = wg.get_peer_info(client_keys['public'])
        return jsonify({
            'status': 'success',
            'client': {
                **client_keys,
                'info': info
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/peers', methods=['GET'])
def get_peers():
    """Получить список всех клиентов"""
    try:
        peers = wg.get_peers()
        return jsonify({
            'status': 'success',
            'peers': peers
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def start_api_server(host='0.0.0.0', port=5000):
    """Запускает API сервер"""
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    start_api_server()