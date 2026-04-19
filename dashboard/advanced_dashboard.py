import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/system.db')

BUFFER = 200
vin_buf = deque(maxlen=BUFFER)
vout_buf = deque(maxlen=BUFFER)
iL_buf = deque(maxlen=BUFFER)
residual_buf = deque(maxlen=BUFFER)

fig, ax = plt.subplots(3,1)

def update(frame):
    df = pd.read_sql("SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1", conn)

    if df.empty:
        return

    row = df.iloc[0]

    Vin = row['Vin']
    Vout = row['Vout']
    iL = row['iL']

    # simple residual estimation (placeholder)
    residual = abs(Vout - (Vin*0.5))

    vin_buf.append(Vin)
    vout_buf.append(Vout)
    iL_buf.append(iL)
    residual_buf.append(residual)

    ax[0].clear()
    ax[1].clear()
    ax[2].clear()

    ax[0].plot(vin_buf, label='Vin')
    ax[0].plot(vout_buf, label='Vout')
    ax[0].legend()
    ax[0].set_title("Voltage")

    ax[1].plot(iL_buf, label='iL')
    ax[1].legend()
    ax[1].set_title("Current")

    ax[2].plot(residual_buf, label='Residual')
    ax[2].legend()
    ax[2].set_title("Residual (Fault Indicator)")

ani = animation.FuncAnimation(fig, update, interval=100)
plt.show()
