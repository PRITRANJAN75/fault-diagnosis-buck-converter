import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import sqlite3
import pandas as pd

from backend.digital_twin import BuckConverterDT

conn = sqlite3.connect('data/system.db')

dt = BuckConverterDT()

BUFFER = 200
vin_buf = deque(maxlen=BUFFER)
vout_buf = deque(maxlen=BUFFER)
vvirtual_buf = deque(maxlen=BUFFER)
residual_buf = deque(maxlen=BUFFER)

fig, ax = plt.subplots(3,1)

def update(frame):
    df = pd.read_sql("SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1", conn)

    if df.empty:
        return

    row = df.iloc[0]

    Vin = row['Vin']
    Vout = row['Vout']

    duty = Vout/Vin if Vin>0 else 0.5
    V_virtual, _ = dt.step(Vin, duty)

    residual = abs(Vout - V_virtual)

    vin_buf.append(Vin)
    vout_buf.append(Vout)
    vvirtual_buf.append(V_virtual)
    residual_buf.append(residual)

    ax[0].clear()
    ax[1].clear()
    ax[2].clear()

    ax[0].plot(vin_buf, label='Vin')
    ax[0].plot(vout_buf, label='Vout')
    ax[0].plot(vvirtual_buf, label='V_virtual')
    ax[0].legend()
    ax[0].set_title("Voltage (Real vs Digital Twin)")

    ax[1].plot(residual_buf, label='Residual')
    ax[1].legend()
    ax[1].set_title("True Residual (Fault Indicator)")

    threshold = 0.5
    faults = [1 if r>threshold else 0 for r in residual_buf]
    ax[2].plot(faults, label='Fault Flag')
    ax[2].legend()
    ax[2].set_title("Fault Detection")

ani = animation.FuncAnimation(fig, update, interval=100)
plt.show()
