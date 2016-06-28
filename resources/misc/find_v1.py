from copy import copy

from verhulst_runner.base import brain_consts
from verhulst_runner.brainstem import *


def find_zilany_scaling_factor(anr, periph) -> float:
    w1_max = 0.0
    w1_target_amplitude = 0.15e-6
    tolerance = 1e-9
    step = 1e-18
    v1 = 1e-18
    while abs(w1_max - w1_target_amplitude) >= tolerance:
        temp_anr = copy(anr) * v1
        w1_max = CentralAuditoryResponse(periph, temp_anr)._simulate(BrainstemType.NelsonCarney04)[
            brain_consts.Wave1AN].max()
        v1 += step
        if v1 > 0.5:
            print("couldn't converge")
            break

    print("V1 set to {:0.5E} and gave a wave 1 amplitude of {:0.5E}".format(v1, w1_max))
