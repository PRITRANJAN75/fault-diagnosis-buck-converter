import numpy as np
import pandas as pd

# 🔥 LOAD CSV
df = pd.read_csv("../data/generated_dataset.csv")

# 🔥 FEATURES (IMPORTANT — 6 FEATURES)
X = df[["Vin", "Vout", "iL", "iout", "ripple_v", "ripple_i"]].values
y = df["label"].values

SEQ_LEN = 20

X_seq = []
y_seq = []

# 🔥 CREATE SEQUENCES
for i in range(len(X) - SEQ_LEN):
    X_seq.append(X[i:i+SEQ_LEN])
    y_seq.append(y[i+SEQ_LEN])

X_seq = np.array(X_seq)
y_seq = np.array(y_seq)

print("📊 Sequence shape:", X_seq.shape)

# 🔥 SAVE
np.save("../data/X.npy", X_seq)
np.save("../data/y.npy", y_seq)

print("✅ Sequences saved → data/X.npy, data/y.npy")

