# event_submission_service/app.py
import sqlite3
import os
import contextlib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
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
                CREATE TABLE IF NOT EXISTS Event (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama_event VARCHAR(255) NOT NULL,
                    deskripsi VARCHAR(1000),
                    tanggal_mulai DATE NOT NULL,
                    tanggal_selesai DATE NOT NULL,
                    status_approval VARCHAR(255) DEFAULT 'pending'
                )
            ''')
            conn.commit()
        print(f"EventSubmissionService: Database '{DB_NAME}' initialized.")
    except Exception as e:
        print(f"EventSubmissionService: Failed to initialize DB '{DB_NAME}' - {e}")
        raise

@app.route('/events', methods=['POST'])
def submit_event():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    nama_event = data.get('nama_event')
    deskripsi = data.get('deskripsi')
    tanggal_mulai = data.get('tanggal_mulai')
    tanggal_selesai = data.get('tanggal_selesai')
    if not all([nama_event, tanggal_mulai, tanggal_selesai]):
        return jsonify({'error': 'nama_event, tanggal_mulai, tanggal_selesai are required'}), 400
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Event (nama_event, deskripsi, tanggal_mulai, tanggal_selesai, status_approval) VALUES (?, ?, ?, ?, ?)",
                (nama_event, deskripsi, tanggal_mulai, tanggal_selesai, 'pending')
            )
            conn.commit()
            event_id = cursor.lastrowid
        return jsonify({
            'event_id': event_id,
            'nama_event': nama_event,
            'deskripsi': deskripsi,
            'tanggal_mulai': tanggal_mulai,
            'tanggal_selesai': tanggal_selesai,
            'status_approval': 'pending'
        }), 201
    except Exception as e:
        app.logger.error(f"Error saving event: {e}")
        return jsonify({'error': 'Failed to save event'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)