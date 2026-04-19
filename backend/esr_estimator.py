import numpy as np

class ESREstimator:
    def estimate(self, vout_window, iL_window):
        vout = np.array(vout_window)
        iL = np.array(iL_window)

        v_ripple = np.ptp(vout)
        i_ripple = np.ptp(iL)

        if i_ripple == 0:
            return 0, 0, 100

        esr = v_ripple / i_ripple
        cap_drop = min(100, (v_ripple / (np.mean(vout)+1e-6)) * 100)
        health = max(0, 100 - cap_drop)

        return esr, cap_drop, health
