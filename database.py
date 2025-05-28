import sqlite3

DATABASE_NAME = "ditmawa.db"

def get_db_connection():
    """Membuka koneksi ke database dengan row factory untuk akses kolom berdasarkan nama."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Membuat tabel jika belum ada."""
    conn = get_db_connection()
    c = conn.cursor()

    # Tabel event
    c.execute("""
        CREATE TABLE Event (
            event_id INTEGER PRIMARY KEY,
            nama_event VARCHAR(255) NOT NULL,
            deskripsi VARCHAR(1000) NOT NULL,
            tanggal_mulai DATE NOT NULL,
            tanggal_selesai DATE NOT NULL,
            status_approval VARCHAR(255) NOT NULL
        )
    """)

    # Tabel room booking status
    c.execute("""
        CREATE TABLE Room_Booking_Status (
            booking_id INTEGER PRIMARY KEY,
            event_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            status_booking VARCHAR(255),
            tanggal_update DATE,
            FOREIGN KEY (event_id) REFERENCES Event(event_id)
        )
    """)

    # Tabel Event approval log
    c.execute("""
        CREATE TABLE Event_Approval_Log (
            approval_id INTEGER PRIMARY KEY,
            event_id INTEGER NOT NULL,
            tanggal_approval DATE,
            status VARCHAR(255),
            catatan VARCHAR(1000),
            FOREIGN KEY (event_id) REFERENCES Event(event_id)
        )
              
    """)

    conn.commit()
    conn.close()
    print("Tabel berhasil dibuat.")

if __name__ == "__main__":
    init_db()