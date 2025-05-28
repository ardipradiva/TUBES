import sqlite3
import requests
from datetime import datetime

DB = "ditmawa.db"

def submit_event(_, info, nama_event, deskripsi, tanggal_mulai, tanggal_selesai):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Event (nama_event, deskripsi, tanggal_mulai, tanggal_selesai, status_approval) VALUES (?, ?, ?, ?, ?)",
        (nama_event, deskripsi, tanggal_mulai, tanggal_selesai, "pending")
    )
    event_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {
        "event_id": event_id,
        "nama_event": nama_event,
        "deskripsi": deskripsi,
        "tanggal_mulai": tanggal_mulai,
        "tanggal_selesai": tanggal_selesai,
        "status_approval": "pending"
    }

def approve_event(_, info, event_id, status, catatan=None):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "UPDATE Event SET status_approval=? WHERE event_id=?",
        (status, event_id)
    )
    cur.execute(
        "INSERT INTO Event_Approval_Log (event_id, tanggal_approval, status, catatan) VALUES (?, ?, ?, ?)",
        (event_id, datetime.now().date(), status, catatan)
    )
    approval_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {
        "approval_id": approval_id,
        "event_id": event_id,
        "tanggal_approval": str(datetime.now().date()),
        "status": status,
        "catatan": catatan
    }

def notify_approved_event(_, info, event_id):
    # Simulasi kirim ke API logistik
    # response = requests.post("https://logistik.api/approved-event", json={"event_id": event_id})
    # return response.status_code == 200
    return True  # Dummy

def event_status(_, info, event_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Event WHERE event_id=?", (event_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "event_id": row[0],
            "nama_event": row[1],
            "deskripsi": row[2],
            "tanggal_mulai": row[3],
            "tanggal_selesai": row[4],
            "status_approval": row[5]
        }
    return None

def room_booking_status(_, info, event_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Room_Booking_Status WHERE event_id=?", (event_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "booking_id": row[0],
            "event_id": row[1],
            "room_id": row[2],
            "status_booking": row[3],
            "tanggal_update": row[4]
        }
    return None

def update_room_booking_status(_, info, event_id, room_id, status_booking):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO Room_Booking_Status (event_id, room_id, status_booking, tanggal_update) VALUES (?, ?, ?, ?)",
        (event_id, room_id, status_booking, datetime.now().date())
    )
    conn.commit()
    cur.execute("SELECT * FROM Room_Booking_Status WHERE event_id=? AND room_id=?", (event_id, room_id))
    row = cur.fetchone()
    conn.close()
    return {
        "booking_id": row[0],
        "event_id": row[1],
        "room_id": row[2],
        "status_booking": row[3],
        "tanggal_update": row[4]
    }

resolvers = {
    "Query": {
        "eventStatus": event_status,
        "roomBookingStatus": room_booking_status,
    },
    "Mutation": {
        "submitEvent": submit_event,
        "approveEvent": approve_event,
        "notifyApprovedEvent": notify_approved_event,
        "updateRoomBookingStatus": update_room_booking_status,
    }
}
