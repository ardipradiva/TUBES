import sqlite3

conn = sqlite3.connect("ditmawa.db")
cur = conn.cursor()

# Tambah data dummy Event
cur.execute("INSERT INTO Event (nama_event, deskripsi, tanggal_mulai, tanggal_selesai, status_approval) VALUES (?, ?, ?, ?, ?)",
            ("Seminar AI", "Seminar tentang AI", "2024-07-01", "2024-07-01", "pending"))

# Tambah data dummy Room_Booking_Status
cur.execute("INSERT INTO Room_Booking_Status (event_id, room_id, status_booking, tanggal_update) VALUES (?, ?, ?, ?)",
            (1, 101, "pending", "2024-06-01"))

# Tambah data dummy Event_Approval_Log
cur.execute("INSERT INTO Event_Approval_Log (event_id, tanggal_approval, status, catatan) VALUES (?, ?, ?, ?)",
            (1, "2024-06-02", "pending", "Menunggu evaluasi"))

conn.commit()
conn.close()
