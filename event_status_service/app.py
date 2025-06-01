# event_status_service/app.py
import sqlite3
import os
import contextlib
from flask import Flask, jsonify
from flask_cors import CORS

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)
CORS(app)
# Explain: Mendefinisikan nama file database KHUSUS untuk layanan pengguna.
DB_NAME = "event_data.db"
# Explain: Membuat path lengkap ke file database di dalam direktori layanan ini.
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

# --- Utilitas Database ---
@contextlib.contextmanager
def get_db_connection():
    # Explain: Menghubungkan ke file database spesifik 'user_data.db'.
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Inisialisasi database pengguna (user_data.db) jika belum ada."""
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Room_Booking_Status (
                    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    room_id INTEGER,
                    status_booking VARCHAR(255),
                    tanggal_update DATE,
                    FOREIGN KEY(event_id) REFERENCES Event(event_id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Event_Approval_Log (
                    approval_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    tanggal_approval DATE,
                    status VARCHAR(255),
                    catatan VARCHAR(1000),
                    FOREIGN KEY(event_id) REFERENCES Event(event_id)
                )
            ''')
            conn.commit()
        # Explain: Pesan konfirmasi mencantumkan nama DB yang benar.
        print(f"EventStatusService: Database '{DB_NAME}' initialized.")
    except Exception as e:
        print(f"EventStatusService: Failed to initialize DB '{DB_NAME}' - {e}")
        raise

# --- API Endpoints ---

@app.route('/events/<int:event_id>/status', methods=['GET'])
def get_event_status(event_id):
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Event WHERE event_id = ?", (event_id,))
            event = cursor.fetchone()
            cursor.execute("SELECT * FROM Event_Approval_Log WHERE event_id = ? ORDER BY tanggal_approval DESC", (event_id,))
            approval_logs = cursor.fetchall()
            cursor.execute("SELECT * FROM Room_Booking_Status WHERE event_id = ? ORDER BY tanggal_update DESC", (event_id,))
            booking_status = cursor.fetchall()
        return jsonify({
            'event': dict(event) if event else None,
            'approval_logs': [dict(row) for row in approval_logs],
            'room_booking_status': [dict(row) for row in booking_status]
        }), 200
    except Exception as e:
        app.logger.error(f"Error fetching event status: {e}")
        return jsonify({'error': 'Failed to fetch event status'}), 500

# --- Menjalankan Aplikasi ---
if __name__ == '__main__':
    init_db() # Inisialisasi DB saat start
    # Explain: host='0.0.0.0' agar bisa diakses dari layanan lain di mesin yang sama.
    #          Port 5007 untuk layanan pengguna.
    app.run(host='0.0.0.0', port=5007, debug=True)