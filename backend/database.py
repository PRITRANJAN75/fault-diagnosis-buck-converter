import sqlite3

def init_db():
    conn = sqlite3.connect('data/system.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            Vin REAL,
            Vout REAL,
            iL REAL,
            iout REAL,
            ripple_v REAL,
            ripple_i REAL,
            status TEXT,
            fault_type TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_data(Vin, Vout, iL, iout, ripple_v, ripple_i, status, fault_type):
    conn = sqlite3.connect('data/system.db')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO readings 
        (Vin, Vout, iL, iout, ripple_v, ripple_i, status, fault_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (Vin, Vout, iL, iout, ripple_v, ripple_i, status, fault_type))

    conn.commit()
    conn.close()