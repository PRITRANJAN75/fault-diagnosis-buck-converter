import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

# =========================
# 🔥 LOAD DATA
# =========================
X = np.load("../data/X.npy")
y = np.load("../data/y.npy")

print("📊 Raw X shape:", X.shape)

# =========================
# 🔥 SANITY CHECK
# =========================
if X.shape[2] != 6:
    raise ValueError("❌ X must have 6 features (Vin, Vout, iL, iout, ripple_v, ripple_i)")

# =========================
# 🔥 NORMALIZATION (CRITICAL)
# =========================
mean = X.mean(axis=(0, 1))
std = X.std(axis=(0, 1)) + 1e-6

np.save("../model/mean.npy", mean)
np.save("../model/std.npy", std)
X = (X - mean) / std

print("✅ Normalization saved")

# =========================
# 🔥 ONE-HOT LABELS
# =========================
y = to_categorical(y, num_classes=4)

# =========================
# 🔥 SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# 🔥 MODEL
# =========================
model = Sequential([
    LSTM(64, input_shape=(X.shape[1], X.shape[2])),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(4, activation='softmax')
])

model.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

# =========================
# 🔥 TRAIN
# =========================
model.fit(
    X_train,
    y_train,
    epochs=20,
    batch_size=32,
    validation_data=(X_test, y_test),
    verbose=1
)

# =========================
# 🔥 SAVE MODEL
# =========================
model.save("../model/lstm_model.h5")

print("✅ Model trained & saved")

# =========================
# 🔥 EVALUATION
# =========================
loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"📊 Test Accuracy: {acc:.3f}")