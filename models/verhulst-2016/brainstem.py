import numpy as np
import numpy.matlib

from periphery_configuration import PeripheryOutput


class CarneyMTFs:
    """
    This class will implement weighted MTF responses to generate ABRs.
    """
    pass


class NelsonCarney04:
    """
    This class ports the Verhulst implementation of the Nelson and Carney (2004) brainstem and IC model.
    """
    M1 = 0.15e-6 / 2.7676e+07  # last value is uncompensated at 100 dB
    M3 = (1.5 * 0.15e-6) / 0.0036  # idem  with scaling W1
    M5 = (2 * 0.15e-6) / 0.0033  # idem with scaling W1 & 3

    TF = 19  # total  no of fibers on each IHC
    HSnormal = 13
    MSnormal = 3
    LSnormal = 3

    Acn = 1.5
    Aic = 1
    Scn = 0.6
    Sic = 1.5
    Dcn = 1e-3
    Dic = 2e-3
    Tex = 0.5e-3
    Tin = 2e-3

    # t=[0:size(ANHS,1)-1]/FS';


    def __init__(self, an: PeripheryOutput):
        self.anfOut = an
        self.Fs = an.conf.Fs
        dur = len(an.conf.stimulus)
        self.time = np.linspace(0, dur / self.Fs, num=dur)

    def run(self):
        # downsample the BM data (not sure why we do this..
        anfh = self.anfOut.anfH[1::2]
        anfm = self.anfOut.anfM[1::2]
        anfl = self.anfOut.anfL[1::2]

        dcnShift = int(round(self.Dcn * self.Fs))
        icShift = int(round(self.Dic * self.Fs))

        inhCn = np.multiply(self.Scn * (1 / (self.Tin ** 2)) * self.time, np.exp((-self.time) / self.Tin))
        inhCn = np.pad(inhCn, (dcnShift, 0), 'constant')[:-dcnShift]

        inhIc = np.multiply(self.Sic * (1 / (self.Tin ** 2)) * self.time, np.exp((-self.time) / self.Tin))
        inhIc = np.pad(inhIc, (icShift, 0), 'constant')[:-icShift]

        AN = np.matlib.repmat(self.LSnormal * np.ones(500), )
