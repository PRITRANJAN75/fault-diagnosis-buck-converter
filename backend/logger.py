import csv
from datetime import datetime

def log_data(esr, error, lstm, status):
    with open("logs.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now(),
            esr,
            error,
            lstm,
            status
        ])