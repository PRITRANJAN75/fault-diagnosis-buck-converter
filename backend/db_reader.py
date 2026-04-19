import sqlite3

conn = sqlite3.connect('data/system.db', check_same_thread=False)

def get_latest_ripple(window=5):
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT ripple_v, ripple_i
        FROM readings
        ORDER BY timestamp DESC
        LIMIT {window}
    """)
    
    rows = cursor.fetchall()

    if not rows:
        return 0.0, 0.0

    r_v = [r[0] for r in rows]
    r_i = [r[1] for r in rows]

    return sum(r_v)/len(r_v), sum(r_i)/len(r_i)