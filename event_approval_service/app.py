# event_approval_service/app.py
import sqlite3
import os
import contextlib
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)
CORS(app)
# Explain: Mendefinisikan nama file database KHUSUS untuk layanan produk.
DB_NAME = "event_data.db"
# Explain: Membuat path lengkap ke file database di dalam direktori layanan ini.
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

# --- Utilitas Database ---
@contextlib.contextmanager
def get_db_connection():
    # Explain: Menghubungkan ke file database spesifik 'product_data.db'.
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Inisialisasi database produk (product_data.db) jika belum ada."""
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
        print(f"EventApprovalService: Database '{DB_NAME}' initialized.")
    except Exception as e:
        print(f"EventApprovalService: Failed to initialize DB '{DB_NAME}' - {e}")
        raise

# --- API Endpoints ---

@app.route('/events/<int:event_id>/approve', methods=['POST'])
def approve_event(event_id):
    data = request.get_json()
    status = data.get('status') # 'approved' or 'rejected'
    catatan = data.get('catatan', '')
    tanggal_approval = data.get('tanggal_approval')
    if status not in ['approved', 'rejected']:
        return jsonify({'error': 'status must be approved or rejected'}), 400
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Event SET status_approval = ? WHERE event_id = ?", (status, event_id))
            cursor.execute(
                "INSERT INTO Event_Approval_Log (event_id, tanggal_approval, status, catatan) VALUES (?, ?, ?, ?)",
                (event_id, tanggal_approval, status, catatan)
            )
            conn.commit()
        return jsonify({'event_id': event_id, 'status': status, 'catatan': catatan, 'tanggal_approval': tanggal_approval}), 200
    except Exception as e:
        app.logger.error(f"Error approving event: {e}")
        return jsonify({'error': 'Failed to approve/reject event'}), 500

# --- Menjalankan Aplikasi ---
if __name__ == '__main__':
    init_db() # Inisialisasi DB saat start
    # Explain: Port 5002 untuk layanan produk.
    app.run(host='0.0.0.0', port=5002, debug=True)