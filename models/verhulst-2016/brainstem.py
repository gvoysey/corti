from collections import namedtuple
from os import path

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

    LowFrequencyCutoff = 175.0  # hz

    BrainstemOutput = namedtuple("NelsonCarney04 Output", ["W1", "CN", "IC", "RanF", "RicF", "RcnF"])

    def __init__(self, an: PeripheryOutput):
        self.anfOut = an
        self.Fs = an.conf.Fs
        self.cf = an.cf
        count, dur = an.conf.stimulus.shape
        self.time = np.linspace(0, dur / self.Fs, num=dur)

        self.anfh = self.anfOut.anfH[:, 1::2]
        self.anfm = self.anfOut.anfM[:, 1::2]
        self.anfl = self.anfOut.anfL[:, 1::2]
        self.cf = self.anfOut.cf[1::2]
        self.cutoffCf = [index for index, value in enumerate(self.cf) if value >= 175.0][-1]
        self.timeLen, self.bmSegments = self.anfh.shape

    def run(self):
        inhCn = self._make_inhibition_component(self.Scn, self.Dcn)
        inhIc = self._make_inhibition_component(self.Sic, self.Dic)

        AN = self._make_summed_an_response()
        output = self._simulate_brainstem_and_midbrain(AN, inhCn, inhIc)
        self._save(output)

    def _save(self, output):
        np.savez(path.join(self.anfOut.conf.output_folder, "nc04 response {0}dB".format(self.anfOut.stimulusLevel)),
                 output)

    def _shift(self, delay: float) -> int:
        return int(round(delay * self.Fs))

    def _inhibition_time_weight(self) -> np.ndarray:
        """ Create a weighted exponential
        :return:
        """
        return np.multiply((1 / (self.Tin ** 2)) * self.time, np.exp((-1 * self.time) / self.Tin))

    def _excitation_time_weight(self) -> np.ndarray:
        """ Create a weighted exponential
        :return:
        """
        return np.multiply((1 / (self.Tex ** 2)) * self.time, np.exp((-1 * self.time) / self.Tex))

    def _make_inhibition_component(self, s: float, delay: float) -> np.ndarray:
        """ Make the DCN or ICN inhibition component.
        Returns $S_{cn}*\frac{1}{t_{in}^2}*\vec{t}*e^{\frac{-\vec{t}}{t_{in}}}$ time shifted by delay
        :param s: some weighting factor
        :param delay: time period, in units of (Fs^-1)s.  This value will be converted to an integer number of samples.
        """
        lag = self._shift(delay)
        inhibition = s * self._inhibition_time_weight()
        return np.pad(inhibition, (lag, 0), 'constant')[:-lag]

    def _make_summed_an_response(self) -> np.ndarray:
        """Create an auditory nerve population response.
        Contains the contributions of low, medium, and high spontaneous rate fibers individually weighted by fiber count,
        and overall weighted by some magic constant.
        :return:
        """
        bmSegments = self.bmSegments
        timeLen = self.timeLen

        lsr = numpy.matlib.repmat(self.LSnormal * np.ones((1, bmSegments)), timeLen, 1) * self.anfl
        msr = numpy.matlib.repmat(self.MSnormal * np.ones((1, bmSegments)), timeLen, 1) * self.anfm
        hsr = numpy.matlib.repmat(self.HSnormal * np.ones((1, bmSegments)), timeLen, 1) * self.anfh

        return (lsr + msr + hsr) * self.M1

    def _simulate_brainstem_and_midbrain(self, AN: np.ndarray, inhCn: np.ndarray, inhIc: np.ndarray) -> BrainstemOutput:
        bmSegments = self.bmSegments
        timeLen = self.timeLen

        W1 = np.zeros(timeLen)
        IC = np.zeros(timeLen)
        CN = np.zeros(timeLen)
        RanF = np.zeros((bmSegments, timeLen))
        RicF = np.zeros((bmSegments, timeLen))
        RcnF = np.zeros((bmSegments, timeLen))

        for i in range(bmSegments):
            Rcn1 = self.Acn * np.convolve(self._excitation_time_weight(), AN[:, i])
            Rcn2 = np.convolve(inhCn, np.roll(AN[:, i], self._shift(self.Dcn)))
            Rcn = (Rcn1 - Rcn2) * self.M3

            Ric1 = self.Aic * np.convolve(self._excitation_time_weight(), Rcn)
            Ric2 = np.convolve(inhIc, np.roll(Rcn, self._shift(self.Dic)))
            Ric = (Ric1 - Ric2) * self.M5

            if i <= self.cutoffCf:
                W1 += AN[:, i]
                CN += Rcn[0:timeLen]
                IC += Ric[0:timeLen]

            RanF[i, :] = AN[:, i]
            RicF[i, :] = Ric[0:timeLen]
            RcnF[i, :] = Rcn[0:timeLen]

        retval = self.BrainstemOutput(W1=W1, CN=CN, IC=IC, RanF=RanF, RicF=RicF, RcnF=RcnF)
        return retval
