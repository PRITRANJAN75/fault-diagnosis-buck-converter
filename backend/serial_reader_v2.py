import serial

# 🔥 INIT SERIAL (VERIFY COM PORT)
ser = serial.Serial('COM16', 115200, timeout=1)


def read_data():
    try:
        line = ser.readline().decode(errors='ignore').strip()

        if not line:
            return None

        parts = line.split(',')

        # 🔥 EXPECT EXACTLY 6 VALUES FROM ARDUINO
        if len(parts) != 6:
            return None

        Vin, Vout, iL, iout, ripple_v, ripple_i = map(float, parts)

        # 🔥 DEBUG (REAL VALUES FROM ARDUINO)
        print(f"[RIPPLE DEBUG] V_ripple={ripple_v:.4f}, I_ripple={ripple_i:.4f}")

        return Vin, Vout, iL, iout, ripple_v, ripple_i

    except Exception as e:
        print(f"[SERIAL ERROR] {e}")
        return None


# 🔥 TEST MODE (RUN FILE DIRECTLY)
if __name__ == "__main__":
    print("🔌 Serial reader started...")

    while True:
        data = read_data()

        if data is not None:
            print("DATA:", data)