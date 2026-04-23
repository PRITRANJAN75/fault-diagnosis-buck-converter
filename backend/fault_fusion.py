from collections import deque
import numpy as np


class FaultFusionEngine:
    def __init__(self):
        self.esr_history = deque(maxlen=20)
        self.last_status = "NORMAL"
        self.normal_streak = 0

    def compute_trend(self):
        if len(self.esr_history) < 10:
            return 0.0

        x = np.arange(len(self.esr_history))
        y = np.array(self.esr_history)

        slope = np.polyfit(x, y, 1)[0]
        return float(slope)

    def evaluate(self, esr, error, voltage_drop, lstm_pred, confidence, iout):
        self.esr_history.append(esr)
        trend = self.compute_trend()

        score = 0

        # =========================
        # 🔥 LOAD FAULT — check iout FIRST before anything else
        # iout is the only direct signal for load fault
        # =========================
        if iout > 5.0:
            self.normal_streak = 0
            self.last_status = "FAULT"
            return "FAULT", trend
        elif iout > 4.0:
            # borderline — let scoring decide but add weight
            score += 2

        # =========================
        # ✅ STRONG NORMAL ZONE
        # =========================
        if (
            error < 0.05 and
            esr <= 0.02 and
            voltage_drop < 0.13 and
            confidence < 0.90
        ):
            self.normal_streak += 1
            self.last_status = "NORMAL"
            return "NORMAL", trend

        # --- SCORING ---

        # ESR
        if esr > 0.07:
            score += 3
        elif esr > 0.04:
            score += 2
        elif esr > 0.025:
            score += 1

        # ERROR
        if error > 0.45:
            score += 3
        elif error > 0.30:
            score += 2
        elif error > 0.22:
            score += 1

        # VOLTAGE DROP
        if voltage_drop > 0.25:
            score += 2
        elif voltage_drop > 0.18:
            score += 1

        # TREND
        if trend > 0.01:
            score += 2
        elif trend > 0.003:
            score += 1

        # LSTM
        if lstm_pred != 0 and confidence > 0.92:
            score += 1

        # --- FINAL DECISION ---
        if score >= 6:
            status = "FAULT"
            self.normal_streak = 0
        elif score >= 3:
            status = "WARNING"
            self.normal_streak = 0
        else:
            status = "NORMAL"

        # HYSTERESIS
        if self.last_status == "FAULT" and status == "WARNING":
            status = "FAULT"

        if self.last_status == "WARNING" and status == "NORMAL":
            self.normal_streak += 1
            if self.normal_streak >= 3:
                self.normal_streak = 0
                status = "NORMAL"
            else:
                status = "WARNING"

        self.last_status = status
        return status, trend