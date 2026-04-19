from collections import deque
import numpy as np

class FaultFusionEngine:
    def __init__(self):
        self.esr_history = deque(maxlen=20)
        self.last_status = "NORMAL"

    def compute_trend(self):
        if len(self.esr_history) < 10:
            return 0.0

        x = np.arange(len(self.esr_history))
        y = np.array(self.esr_history)

        slope = np.polyfit(x, y, 1)[0]
        return float(slope)

    def evaluate(self, esr, error, voltage_drop, lstm_pred, confidence):
        self.esr_history.append(esr)
        trend = self.compute_trend()

        score = 0

        # ✅ FIXED NORMAL ZONE (REALISTIC)
        if (
            error < 0.18 and
            esr < 0.02 and
            confidence < 0.7
        ):
            self.last_status = "NORMAL"
            return "NORMAL", trend

        # ESR contribution
        if esr > 0.07:
            score += 3
        elif esr > 0.04:
            score += 2
        elif esr > 0.025:
            score += 1

        # Error contribution
        if error > 0.45:
            score += 3
        elif error > 0.3:
            score += 2
        elif error > 0.22:
            score += 1

        # =========================
        # 🔥 INPUT FAULT DETECTION (NEW)
        # =========================
        if voltage_drop > 0.35:
            score += 3
        elif voltage_drop > 0.25:
            score += 2
        elif voltage_drop > 0.18:
            score += 1

        # Trend contribution
        if trend > 0.01:
            score += 2
        elif trend > 0.003:
            score += 1

        # LSTM support
        if lstm_pred != 0 and confidence > 0.8:
            score += 2

        # Final decision
        if score >= 6:
            status = "FAULT"
        elif score >= 3:
            status = "WARNING"
        else:
            status = "NORMAL"

        # Hysteresis
        if self.last_status == "FAULT" and status == "WARNING":
            status = "FAULT"
        if self.last_status == "WARNING" and status == "NORMAL":
            status = "WARNING"

        self.last_status = status
        return status, trend
