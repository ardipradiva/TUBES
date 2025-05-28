import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
LOGISTICS_API_URL = "http://logistics-system/api/room-booking"  # Placeholder URL

@app.route('/notify-approved-event', methods=['POST'])
def notify_approved_event():
    data = request.get_json()
    event_id = data.get('event_id')
    if not event_id:
        return jsonify({'error': 'event_id is required'}), 400
    # Simulate sending event data to logistics system
    try:
        # In a real system, fetch event details from DB or another service
        payload = {'event_id': event_id}
        response = requests.post(LOGISTICS_API_URL, json=payload, timeout=5)
        response.raise_for_status()
        return jsonify({'message': 'Notification sent to logistics', 'response': response.json()}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to notify logistics: {e}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
