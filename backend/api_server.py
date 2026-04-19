from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import numpy as np


app = Flask(__name__)
CORS(app)

def get_latest():
    conn = sqlite3.connect('data/system.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Vin, Vout, iL, iout, ripple_v, ripple_i, status, fault_type
        FROM readings
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row:
        # ✅ FIXED: consistent naming
        Vin, Vout, iL, iout, rv, ri, status, fault_type = row

        # 🔹 Power calculations
        duty = Vout / (Vin + 1e-6)
        Iin_est = iout * duty

        Pin = Vin * Iin_est
        Pout = Vout * iout

        efficiency = (Pout / (Pin + 1e-6)) * 100

        # clamp to realistic range
        efficiency = max(0, min(efficiency, 100))

        # 🔹 ESR calculation (for display only)
        if ri < 1e-4:
            esr = 0.001
        else:
            esr = (rv / ri) * 0.1

        esr = float(np.clip(esr, 0.001, 2.0))

        # ✅ IMPORTANT: NO status recomputation here
        # Backend (fusion engine) is the ONLY source of truth

        return {
            "Vin": Vin,
            "Vout": Vout,
            "Iin": iL,
            "Iout": iout,
            "Pin": Pin,
            "Pout": Pout,
            "Efficiency": efficiency,
            "ESR": esr,
            "Status": status,   # ✅ from DB
            "Fault": fault_type # ✅ from DB
        }

    return {}

@app.route('/data')
def data():
    return jsonify(get_latest())

if __name__ == '__main__':
    app.run(debug=True)
