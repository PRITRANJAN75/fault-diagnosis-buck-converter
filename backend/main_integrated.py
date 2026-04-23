from serial_reader_v2 import read_data
from digital_twin import BuckConverterDT
from database import insert_data, init_db
from lstm_model import load_lstm, predict_sequence
from sequence_buffer import SequenceBuffer
from fault_fusion import FaultFusionEngine
from logger import log_data

import numpy as np
from collections import deque

# ✅ INIT DB
init_db()

# 🔹 Fixed duty cycle
DUTY_FIXED = 0.25

# 🔹 DT warmup counter — ignore voltage_drop until DT has settled
dt_warmup_steps = 0
DT_WARMUP_REQUIRED = 50

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
        # 🔹 DIGITAL TWIN — FIXED DUTY
        # =========================
        duty = DUTY_FIXED
        v_virtual, _ = dt.step(Vin, duty)

        dt_warmup_steps += 1

        error = abs(Vout - v_virtual) / max(Vout, 1)
        error *= 0.2
        error = min(error, 0.5)

        # ✅ Suppress voltage_drop during DT warmup — DT hasn't settled yet
        if dt_warmup_steps < DT_WARMUP_REQUIRED:
            voltage_drop = 0.0
        else:
            voltage_drop = abs(Vout - v_virtual) / max(v_virtual, 1)

        # =========================
        # 🔥 ESR (DISABLED FOR REAL HARDWARE)
        # =========================
        esr = 0.02

        # =========================
        # ✅ SANITY CHECK — Vout must be within ±15% of expected (Vin * duty)
        # =========================
        VOUT_EXPECTED = Vin * DUTY_FIXED
        VOUT_MIN = VOUT_EXPECTED * 0.85
        VOUT_MAX = VOUT_EXPECTED * 1.15

        if not (VOUT_MIN <= Vout <= VOUT_MAX):
            status = "FAULT"
            fault_type = "INPUT_FAULT"
            trend = 0.0
            print(
                f"[SANITY] Vout={Vout:.2f} outside expected range "
                f"[{VOUT_MIN:.2f}, {VOUT_MAX:.2f}] for duty={DUTY_FIXED} → INPUT_FAULT"
            )

        else:
            # =========================
            # 🔥 FUSION — pass iout so load fault can be detected
            # =========================
            status, trend = fusion.evaluate(esr, error, voltage_drop, pred, confidence,iout)

            # =========================
            # 🔥 FAULT LOGIC
            # =========================
            if status == "NORMAL":
                fault_type = "NORMAL"

            else:
                if iout > 5.0:
                    fault_type = "LOAD_FAULT"
                elif iout > 4.0:
                    fault_type = "LOAD_FAULT"
                elif voltage_drop > 0.25:
                    fault_type = "INPUT_FAULT"
                else:
                    if confidence < 0.75:
                        fault_type = "UNSURE"
                        pred = 0
                    elif error < 0.05 and voltage_drop < 0.13:
                        fault_type = "UNSURE"
                    else:
                        fault_type = fault_map.get(pred, "UNKNOWN")

        # =========================
        # ✅ STORE
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
            f"ESR:{esr:.3f} | Error:{error:.3f} | Trend:{trend:.5f} | "
            f"Vout:{Vout:.2f} | VDrop:{voltage_drop:.4f}"
        )

except KeyboardInterrupt:
    print("Stopped")
