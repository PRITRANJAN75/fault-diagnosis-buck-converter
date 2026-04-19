from serial_reader_v2 import read_data
from digital_twin import BuckConverterDT
from database import insert_data
from database import init_db

from lstm_model import load_lstm, predict_sequence
from sequence_buffer import SequenceBuffer
from fault_fusion import FaultFusionEngine
from logger import log_data

import numpy as np
from collections import deque

# ✅ INIT DB
init_db()

# 🔹 History buffer for majority voting
pred_history = deque(maxlen=5)

# 🔹 Load model + normalization parameters
model = load_lstm()
mean = np.load("model/mean.npy")
std = np.load("model/std.npy")

dt = BuckConverterDT()
buffer = SequenceBuffer(50)
fusion = FaultFusionEngine()

# 🔥 FAULT LABELS
fault_map = {
    0: "NORMAL",
    1: "ESR_FAULT",
    2: "INPUT_FAULT",
    3: "LOAD_FAULT"
}

try:
    while True:
        data = read_data()
        if data is None:
            continue

        Vin, Vout, iL, iout, ripple_v, ripple_i = data

        # =========================
        # 🔹 NORMALIZATION
        # =========================
        features = np.array([Vin, Vout, iL, iout, ripple_v, ripple_i])
        features = (features - mean) / std

        # =========================
        # 🔹 LSTM
        # =========================
        buffer.add(features)
        seq = buffer.get_sequence()

        if seq is not None:
            seq = seq.reshape(1, seq.shape[0], seq.shape[1])
            pred, confidence = predict_sequence(model, seq)

            pred_history.append(pred)
            if len(pred_history) == pred_history.maxlen:
                pred = max(set(pred_history), key=pred_history.count)
        else:
            pred, confidence = 0, 0.0

        # =========================
        # 🔹 DIGITAL TWIN
        # =========================
        duty = Vout / Vin if Vin > 0 else 0.5
        v_virtual, _ = dt.step(Vin, duty)

        error = abs(Vout - v_virtual) / max(Vout, 1)

        # 🔥 LOAD sensitivity
        if iout > 2.0:
            error += 0.25

        error = min(error, 0.5)

        # 🔥 INPUT signal
        voltage_drop = (Vin - Vout) / max(Vin, 1)

        # =========================
        # 🔹 ESR
        # =========================
        if ripple_i < 1e-4:
            esr = 0.001
        else:
            esr = (ripple_v / ripple_i) * 0.1

        esr = float(np.clip(esr, 0.001, 0.5))

        # =========================
        # 🔥 FUSION
        # =========================
        status, trend = fusion.evaluate(esr, error, voltage_drop, pred, confidence)

        # =========================
        # 🔥 ✅ FIXED FAULT LOGIC (CRITICAL)
        # =========================
        if status == "NORMAL":
            fault_type = "NORMAL"

        else:
            # 1. ESR fault (clear signature)
            if esr > 0.05:
                fault_type = "ESR_FAULT"

            # 2. LOAD fault (HIGH CURRENT)
            elif iout > 1.5:
                fault_type = "LOAD_FAULT"

            # 3. INPUT fault (LOW INPUT VOLTAGE)
            elif Vin < 10.0:
                fault_type = "INPUT_FAULT"

            # 4. fallback to LSTM
            else:
                if confidence < 0.6:
                    fault_type = "UNSURE"
                    pred = 0
                else:
                    fault_type = fault_map.get(pred, "UNKNOWN")

        # =========================
        # ✅ STORE (correct place)
        # =========================
        insert_data(Vin, Vout, iL, iout, ripple_v, ripple_i, status, fault_type)

        # =========================
        # 🔹 LOG
        # =========================
        log_data(esr, error, pred, status)

        # =========================
        # 🔥 OUTPUT
        # =========================
        print(
            f"[FUSION] Status:{status} | Fault:{fault_type} | Conf:{confidence:.2f} | "
            f"ESR:{esr:.3f} | Error:{error:.3f} | Trend:{trend:.5f} | Vout:{Vout:.2f}"
        )

except KeyboardInterrupt:
    print("Stopped")