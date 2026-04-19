class BuckConverterDT:
    def __init__(self, L=100e-6, C=100e-6, R=10, dt=1e-5):
        self.L = L
        self.C = C
        self.R = R
        self.dt = dt
        self.iL = 0
        self.vC = 0

    def step(self, Vin, duty):
        # ✅ Deterministic (NO RANDOMNESS)
        efficiency = 0.92
        v_virtual = Vin * duty * efficiency

        self.vC = v_virtual
        self.iL = 0

        return self.vC, self.iL