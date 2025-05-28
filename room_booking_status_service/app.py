import sqlite3
import os
import contextlib
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_NAME = "event_data.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

@contextlib.contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Room_Booking_Status (
                    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    room_id INTEGER,
                    status_booking VARCHAR(255),
                    tanggal_update DATE
                )
            ''')
            conn.commit()
        print(f"RoomBookingStatusService: Database '{DB_NAME}' initialized.")
    except Exception as e:
        print(f"RoomBookingStatusService: Failed to initialize DB '{DB_NAME}' - {e}")
        raise

@app.route('/room-booking-status', methods=['POST'])
def update_room_booking_status():
    data = request.get_json()
    event_id = data.get('event_id')
    room_id = data.get('room_id')
    status_booking = data.get('status_booking')
    tanggal_update = data.get('tanggal_update')
    if not all([event_id, room_id, status_booking, tanggal_update]):
        return jsonify({'error': 'event_id, room_id, status_booking, tanggal_update are required'}), 400
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Room_Booking_Status (event_id, room_id, status_booking, tanggal_update) VALUES (?, ?, ?, ?)",
                (event_id, room_id, status_booking, tanggal_update)
            )
            conn.commit()
        return jsonify({'message': 'Room booking status updated'}), 200
    except Exception as e:
        app.logger.error(f"Error updating room booking status: {e}")
        return jsonify({'error': 'Failed to update room booking status'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5004, debug=True)
