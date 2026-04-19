import numpy as np

class RippleExtractor:
    def compute(self, signal_window):
        arr = np.array(signal_window)
        if len(arr) < 5:
            return 0.0
        return float(np.max(arr) - np.min(arr))
