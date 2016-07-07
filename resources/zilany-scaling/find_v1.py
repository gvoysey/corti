"""
This script iteratively computes the scaling factor such that the summed auditory nerve response of the Zilany (2014)
model results in a wave 1 peak amplitude near 15 uV for an 80dB SPL click stimulus.

This criterion allows it to match the magnitudes of the Verhulst (2012/15) model, which was similarly calibrated.

See the `zilany-scaling-factor` commit (SHA ea73385343d4508244ab192c59212008205acf77 or
https://github.com/gvoysey/corti/releases/tag/zilany-scaling-factor ) for how it was used to determine the value of Z1.
"""
import numpy as np


# Call find_zilany inline in the verhulst model code.  ref tag `zilany-scaling-factor`.

def _total_hack(anr: np.ndarray):
    timeLen, cfCount = anr.shape
    AN = anr
    W1 = np.zeros(timeLen)

    for i in range(cfCount):
        if i <= 959:  # ew, hard-coded.  this assumes a zilany model, 1000 CFs.
            W1 += AN[:, i]
    return W1.max()


def find_zilany_scaling_factor(anr: np.ndarray) -> float:
    w1_max = 0.0
    w1_target_amplitude = 0.15e-6
    tolerance = 1e-9
    step = 1e-18
    v1 = 1e-18
    while abs(w1_max - w1_target_amplitude) >= tolerance:
        temp_anr = anr.copy() * v1
        w1_max = _total_hack(temp_anr)
        v1 += step
        if v1 > 0.5:
            print("couldn't converge")
            break

    print("V1 set to {:0.5E} and gave a wave 1 amplitude of {:0.5E}".format(v1, w1_max))
