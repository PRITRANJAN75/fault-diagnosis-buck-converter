import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense

MODEL_PATH = 'model/lstm_model.h5'

model = None


# =========================
# 🔥 BUILD MODEL (6 FEATURES)
# =========================
def build_model(input_shape):
    m = Sequential()
    m.add(LSTM(64, input_shape=input_shape))
    m.add(Dense(32, activation='relu'))
    m.add(Dense(4, activation='softmax'))  # 4 classes

    m.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return m


# =========================
# 🔥 TRAIN MODEL
# =========================
def train_lstm(X, y):
    print(f"📊 Training shape: {X.shape}")

    # 🔥 sanity check
    if X.shape[2] != 6:
        raise ValueError("❌ Model expects 6 features (Vin, Vout, iL, iout, ripple_v, ripple_i)")

    m = build_model((X.shape[1], X.shape[2]))
    m.fit(X, y, epochs=10, batch_size=32)

    m.save(MODEL_PATH)
    print("✅ Model trained & saved")


# =========================
# 🔥 LOAD MODEL
# =========================
def load_lstm():
    global model

    if model is None:
        model = load_model(MODEL_PATH)

        # 🔥 verify input shape
        expected_features = model.input_shape[-1]
        if expected_features != 6:
            raise ValueError(f"❌ Loaded model expects {expected_features} features, but 6 required")

        print("✅ LSTM model loaded (6 features confirmed)")

    return model


# =========================
# 🔥 PREDICTION (ROBUST)
# =========================
def predict_sequence(model, seq):

    # 🔥 check input shape
    if seq.shape[-1] != 6:
        raise ValueError("❌ Input sequence must have 6 features")

    probs = model.predict(seq, verbose=0)

    # 🔥 handle bad outputs
    if np.isnan(probs).any():
        return 0, 0.0

    label = int(np.argmax(probs))
    confidence = float(np.max(probs))

    # 🔥 soften confidence (avoid fake 1.0 certainty)
    confidence *= 0.9

    return label, confidence