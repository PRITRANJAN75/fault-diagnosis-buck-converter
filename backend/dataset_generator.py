import numpy as np
import os

N = 5000
SEQ_LEN = 20

# 🔥 AUTO PATH FIX (CRITICAL)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
MODEL_DIR = os.path.join(BASE_DIR, "../model")

# 🔥 ensure folders exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


def generate_sequence(mode=0):
    Vin_base = 48
    duty_base = 0.25

    seq = []

    for t in range(SEQ_LEN):

        Vin = Vin_base + np.random.normal(0, 0.5)
        duty = duty_base + 0.02 * np.sin(2 * np.pi * 0.1 * t)

        Vout = Vin * duty

        iout = 5 + np.random.normal(0, 0.1)
        iL = iout * 0.3 + np.random.normal(0, 0.05)

        ripple_v = 0.02 + np.random.normal(0, 0.003)
        ripple_i = 0.2 + np.random.normal(0, 0.01)

        # 🔥 FAULTS
        if mode == 1:  # ESR
            ripple_v *= np.random.uniform(3, 6)

        elif mode == 2:  # INPUT
            Vin += np.random.normal(0, 10)
            Vout = Vin * duty

        elif mode == 3:  # LOAD
            iout *= np.random.uniform(1.5, 3.0)
            iL = iout * np.random.uniform(0.2, 0.4)

        # 🔹 noise
        Vin += np.random.normal(0, 1.0)
        Vout += np.random.normal(0, 0.5)
        iL += np.random.normal(0, 0.2)
        iout += np.random.normal(0, 0.2)
        ripple_v += np.random.normal(0, 0.02)
        ripple_i += np.random.normal(0, 0.05)

        seq.append([Vin, Vout, iL, iout, ripple_v, ripple_i])

    return np.array(seq), mode


def generate_dataset():
    X = []
    y = []

    for _ in range(N):
        mode = np.random.choice([0, 1, 2, 3])
        seq, label = generate_sequence(mode)

        X.append(seq)
        y.append(label)

    X = np.array(X)
    y = np.array(y)

    # 🔥 NORMALIZATION
    mean = X.mean(axis=(0, 1))
    std = X.std(axis=(0, 1)) + 1e-6

    X = (X - mean) / std

    # 🔥 SAVE (FIXED PATHS)
    np.save(os.path.join(DATA_DIR, "X.npy"), X)
    np.save(os.path.join(DATA_DIR, "y.npy"), y)

    np.save(os.path.join(MODEL_DIR, "mean.npy"), mean)
    np.save(os.path.join(MODEL_DIR, "std.npy"), std)

    print("✅ Dataset saved correctly")
    print(f"📊 Shape: {X.shape}")


if __name__ == "__main__":
    generate_dataset()