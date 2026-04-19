import random

def read_data():
    Vin = random.uniform(10,15)
    Vout = Vin*random.uniform(0.4,0.8)
    iL = random.uniform(0.5,2)
    iout = iL*random.uniform(0.8,1.1)
    return Vin, Vout, iL, iout
