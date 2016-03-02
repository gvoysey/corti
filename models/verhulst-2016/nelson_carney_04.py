import numpy as np

class NelsonCarney04:
    M1 = 0.15e-6 / 2.7676e+07 # last value is uncompensated at 100 dB
    M3 = (1.5 * 0.15e-6) / 0.0036#  idem  with scaling W1
    M5 = (2 * 0.15e-6) / 0.0033 #idem with scaling W1 & 3

    TF = 19 #total  no of fibers on each IHC
    HSnormal = 13
    MSnormal = 3
    LSnormal = 3

    L = [60, 80]
    FS = 100000

