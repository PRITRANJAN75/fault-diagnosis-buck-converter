import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import sqlite3
import pandas as pd
import numpy as np

from ripple_extractor_v2 import RippleExtractor
conn = sqlite3.connect('data/system.db')

BUFFER = 200
ripple_v_buf = deque(maxlen=BUFFER)
ripple_i_buf = deque(maxlen=BUFFER)
esr_buf = deque(maxlen=BUFFER)
health_buf = deque(maxlen=BUFFER)

# 🔥 SMALL WINDOW
ripple_ext = RippleExtractor(window_size=5)

ESR_NOMINAL = 0.05
ESR_MAX = 2.0

# 🔥 NEW: Smoothing variables
alpha = 0.2
esr_smooth = None

fig, ax = plt.subplots(3,1)

def update(frame):
    global esr_smooth

    df = pd.read_sql("SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1", conn)

    if df.empty:
        return

    row = df.iloc[0]

    # ✅ Ripple-only signals
    ripple_v = row['ripple_v']
    ripple_i = row['ripple_i']

    ripple_v_buf.append(ripple_v)
    ripple_i_buf.append(ripple_i)

    if len(ripple_v_buf) > 10:
        delta_v = ripple_ext.compute(ripple_v_buf)
        delta_i = ripple_ext.compute(ripple_i_buf)

        if delta_i < 1e-3:
            esr = 0
        else:
            esr = delta_v / delta_i

        esr = float(np.clip(esr, 0.001, 2.0))

        # 🔥 EMA SMOOTHING
        if esr_smooth is None:
            esr_smooth = esr
        else:
            esr_smooth = alpha * esr + (1 - alpha) * esr_smooth

        print(f"ΔV={delta_v:.3f}, ΔI={delta_i:.3f}, ESR={esr_smooth:.3f}")

        # 🔥 FAULT DETECTION
        if esr_smooth > 0.5:
            print("⚠️ Capacitor Degrading")

        # 🔥 HEALTH
        health = 100 * (1 - (esr_smooth - ESR_NOMINAL) / (ESR_MAX - ESR_NOMINAL))
        health = float(np.clip(health, 0, 100))

    else:
        esr_smooth = 0
        health = 100

    esr_buf.append(esr_smooth)
    health_buf.append(health)

    ax[0].clear()
    ax[1].clear()
    ax[2].clear()

    ax[0].plot(ripple_v_buf, label='Ripple Voltage')
    ax[0].set_title('Ripple Voltage')
    ax[0].legend()

    ax[1].plot(esr_buf, label='ESR (Ohm)')
    ax[1].set_title('Smoothed ESR')
    ax[1].legend()

    ax[2].plot(health_buf, label='Health %')
    ax[2].set_title('Capacitor Health')
    ax[2].legend()

ani = animation.FuncAnimation(fig, update, interval=100)
plt.show()