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
        self.peripheryOutput = an

    def run(self):
        anfh = self.peripheryOutput.anfH[1::2]
        anfm = self.peripheryOutput.anfM[1::2]
