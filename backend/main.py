from serial_reader import read_data
from digital_twin import BuckConverterDT
from lstm_model import load_lstm
from sequence_buffer import SequenceBuffer

import numpy as np

model = load_lstm()
dt = BuckConverterDT()
buffer = SequenceBuffer(50)

while True:
    data = read_data()
    if data is None:
        continue

    Vin, Vout, iL, iout = data

    buffer.add([Vin, Vout, iL, iout])
    seq = buffer.get_sequence()

    if seq is not None:
        seq = seq.reshape(1, seq.shape[0], seq.shape[1])
        pred = np.argmax(model.predict(seq, verbose=0))
    else:
        pred = 0

    v_virtual, i_virtual = dt.step(Vin, Vout/Vin if Vin>0 else 0.5)

    print(f"Fault:{pred} Vout:{Vout:.2f} Virtual:{v_virtual:.2f}")
