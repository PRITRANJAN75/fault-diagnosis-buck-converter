class BuckConverterDT:
    def __init__(self, L=100e-6, C=100e-6, R=10, dt=1e-5, efficiency=0.92):
        self.L = L           # Inductor (reserved for future dynamic model)
        self.C = C           # Capacitor (reserved for future dynamic model)
        self.R = R           # Load resistance (reserved for future dynamic model)
        self.dt = dt         # Time step (reserved for future dynamic model)
        self.efficiency = efficiency  # Empirical calibration factor k (Phase II)
        self.iL = 0.0        # Inductor current state
        self.vC = 0.0        # Capacitor voltage state

    def step(self, Vin, duty):
        # ✅ Calibrated steady-state average model
        # V_virtual = Vin * D * k
        # k = 0.92 accounts for MOSFET conduction loss, diode forward drop,
        # inductor winding resistance, and PCB parasitic losses (Phase II calibration)
        v_virtual = Vin * duty * self.efficiency

        self.vC = v_virtual
        self.iL = v_virtual / self.R

        return self.vC, self.iL