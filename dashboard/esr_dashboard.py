import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import sqlite3
import pandas as pd

from backend.esr_estimator import ESREstimator
from backend.ripple_extractor import RippleExtractor

conn = sqlite3.connect('data/system.db')

BUFFER = 200
vout_buf = deque(maxlen=BUFFER)
iL_buf = deque(maxlen=BUFFER)
esr_buf = deque(maxlen=BUFFER)
health_buf = deque(maxlen=BUFFER)

esr_est = ESREstimator()
ripple_ext = RippleExtractor()

fig, ax = plt.subplots(3,1)

def update(frame):
    df = pd.read_sql("SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1", conn)

    if df.empty:
        return

    row = df.iloc[0]

    Vout = row['Vout']
    iL = row['iL']

    vout_buf.append(Vout)
    iL_buf.append(iL)

    if len(vout_buf) > 20:
        v_ripple = ripple_ext.compute(vout_buf)
        i_ripple = ripple_ext.compute(iL_buf)

        esr, cap_drop, health = esr_est.estimate(vout_buf, iL_buf)
    else:
        esr, health = 0, 100

    esr_buf.append(esr)
    health_buf.append(health)

    ax[0].clear()
    ax[1].clear()
    ax[2].clear()

    ax[0].plot(vout_buf, label='Vout')
    ax[0].set_title('Output Voltage')
    ax[0].legend()

    ax[1].plot(esr_buf, label='ESR')
    ax[1].set_title('Estimated ESR')
    ax[1].legend()

    ax[2].plot(health_buf, label='Health %')
    ax[2].set_title('Capacitor Health')
    ax[2].legend()

ani = animation.FuncAnimation(fig, update, interval=100)
plt.show()
