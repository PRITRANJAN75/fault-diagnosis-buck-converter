import numpy as np

class RippleExtractor:
    def __init__(self, window_size=5):
        self.window_size = window_size

    def compute(self, signal_window):
        arr = np.array(signal_window)
        if len(arr) < self.window_size:
            return 0.0
        window = arr[-self.window_size:]
        x = np.arange(len(window))
        coeffs = np.polyfit(x, window, 1)
        trend = coeffs[0] * x + coeffs[1]
        window_detrended = window - trend
        delta = float(np.max(window_detrended) - np.min(window_detrended))

        return delta