import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import random

BUFFER = 200
vin_buf = deque(maxlen=BUFFER)
vout_buf = deque(maxlen=BUFFER)
iL_buf = deque(maxlen=BUFFER)

fig, ax = plt.subplots(2,1)

def update(frame):
    # simulate real-time data
    Vin = random.uniform(10,15)
    Vout = Vin*random.uniform(0.4,0.8)
    iL = random.uniform(0.5,2)

    vin_buf.append(Vin)
    vout_buf.append(Vout)
    iL_buf.append(iL)

    ax[0].clear()
    ax[1].clear()

    ax[0].plot(vin_buf, label='Vin')
    ax[0].plot(vout_buf, label='Vout')
    ax[0].legend()

    ax[1].plot(iL_buf, label='iL')
    ax[1].legend()

ani = animation.FuncAnimation(fig, update, interval=50)
plt.show()
