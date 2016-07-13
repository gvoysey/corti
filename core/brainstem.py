import logging

import numpy as np
# noinspection PyPackageRequirements
import progressbar
from os import path

from core.base import runtime_consts, brain_consts as b, periph_consts as p, BrainstemType
from .periphery_configuration import PeripheryOutput


def simulate_brainstem(anResults: [(PeripheryOutput, np.ndarray, str)]) -> [{}]:
    # return Parallel(n_jobs=-1, max_nbytes=100e6)(delayed(_solve_one)(x) for x in anResults)
    retval = []
    for i in anResults:
        retval.append(_solve_one(i))
    return retval


def _solve_one(periphery: (PeripheryOutput, np.ndarray, str)) -> {}:
    return CentralAuditoryResponse(periphery[0], periphery[1], periphery[2]).run()


class CentralAuditoryResponse:
    """
    This class implements the midbrain and brainstem models developed by Laurel Carney et al, and set forth in
    - Nelson, P. C., and Carney, L. H. (2004). “A phenomenological model of peripheral and central
    neural responses to amplitude-modulated tones,” J. Acoust. Soc. Am., 116, 2173. doi:10.1121/1.1784442
    - Carney, L. H., Li, T., and McDonough, J. M. (2015). “Speech Coding in the Brain: Representation of Vowel
    Formants by Midbrain Neurons Tuned to Sound Fluctuations,” eNeuro, 2, 1–12. doi:10.1523/ENEURO.0004-15.2015
    """

    LowFrequencyCutoff = 175.0  # CFs below this threshold will not be used to estimate the compound action potential

    def __init__(self, an: PeripheryOutput, anr: np.ndarray, modelType: str):
        self.anr = anr
        self.anfOut = an
        self.Fs = an.conf.Fs
        self.cf = an.output[p.CenterFrequency]
        dur = anr.shape[0]
        self.time = np.linspace(0, dur / self.Fs, num=dur)
        self.cf = self.anfOut.output[p.CenterFrequency]
        self.cutoffCf = [index for index, value in enumerate(self.cf) if value >= self.LowFrequencyCutoff][-1]
        self.brainstemType = BrainstemType[modelType.casefold()]

    def run(self) -> {}:
        """
        Simulate the brainstem and midbrain according to the single IC component system given in
        Nelson, P. C., and Carney, L. H. (2004). “A phenomenological model of peripheral and central
        neural responses to amplitude-modulated tones,” J. Acoust. Soc. Am., 116, 2173. doi:10.1121/1.1784442
        """

        output = self._simulate()
        self._save(output)
        return output

    def _save(self, output: {}) -> None:
        if self.anfOut.conf.pypet:
            return
        name = runtime_consts.BrainstemOutputFilePrefix + "{0}dB".format(self.anfOut.output[p.StimulusLevel])
        outpath = self.anfOut.outputFolder
        # save the data out to a npz file whose keys are the field names of output.
        np.savez(path.join(outpath, name), **output)
        logging.log(logging.INFO, "wrote {0:<10} to {1}".format(name, path.abspath(outpath)))

    def _shift(self, delay: float) -> int:
        return int(round(delay * self.Fs))

    def __alpha(self, scalingFactor: float) -> np.ndarray:
        """Make an alpha function of the form
        $\frac{1}{sF^2}*\vec{t}*e^{\frac{-\vec{t}}{sF}}$
        """
        # noinspection PyTypeChecker
        return np.multiply((1 / (scalingFactor ** 2)) * self.time, np.exp(((-1 * self.time) / scalingFactor)))

    def _excitation_wave(self, tex: float) -> np.ndarray:
        """A bare wrapper around the alpha generator, for readability and clarity."""
        return self.__alpha(tex)

    def _inhibition_wave(self, s: float, Tin: float, delay: float) -> np.ndarray:
        """ Make the DCN or ICN inhibition component.
        Returns $S_{cn}*\frac{1}{t_{in}^2}*\vec{t}*e^{\frac{-\vec{t}}{t_{in}}}$ time shifted by delay (an alpha function)
        :param s: some weighting factor
        :param delay: time period, in units of (Fs^-1)s.  This value will be converted to an integer number of samples.
        """
        lag = self._shift(delay)
        inhibition = s * self.__alpha(Tin)
        return np.pad(inhibition, (lag, 0), 'constant')[:-lag]

    def _cn(self, cf) -> np.ndarray:
        AN = self.anr
        Acn = 1.5
        Scn = 0.6
        Dcn = 1e-3
        M3 = (1.5 * 0.15e-6) / 0.0036  # idem  with scaling W1
        Tex = 0.5e-3
        Tin = 2e-3
        inhCn = self._inhibition_wave(Scn, Tin, Dcn)
        Rcn1 = Acn * np.convolve(self._excitation_wave(Tex), AN[:, cf])
        Rcn2 = np.convolve(inhCn, np.roll(AN[:, cf], self._shift(Dcn)))
        Rcn = (Rcn1 - Rcn2) * M3
        return Rcn

    def _ic(self, rcn, aic, sic, dic, tin, tex):
        inhIc = self._inhibition_wave(sic, tin, dic)
        Ric1 = aic * np.convolve(self._excitation_wave(tex), rcn)
        Ric2 = np.convolve(inhIc, np.roll(rcn, self._shift(dic)))
        return (Ric1 - Ric2)

    def _ic_bandpass(self, rcn):
        """
        Returns the UNWEIGHTED IC modeled as a bank of band-pass filters.
        :param rcn:
        :return:
        """
        Tex = 0.5e-3
        Tin = 2e-3
        Dic = 2e-3
        Aic = 1
        Sic = 1.5
        return self._ic(rcn, Aic, Sic, Dic, Tin, Tex)

    def _ic_lowpass(self, rcn):
        Tex = 2e-3
        Tin = 5e-3
        Dic = 2e-3
        Aic = 1
        Sic = 1.5
        return self._ic(rcn, Aic, Sic, Dic, Tin, Tex)

    def _ic_band_reject(self, rcn):
        Tex = 0.5e-3
        Tin = 2e-3
        Dic = 2e-3
        Aic = 1
        Sic = 1.5
        return self._ic(rcn, Aic, Sic, Dic, Tin, Tex)

    def __simulate_IC(self, modelType: BrainstemType, rcn: np.ndarray, weights=(.5, .25, .25)) -> np.ndarray:
        M5 = (2 * 0.15e-6) / 0.0033  # idem with scaling W1 & 3

        if modelType == BrainstemType.nelsoncarney04:
            retval = self._ic_bandpass(rcn)
        elif modelType == BrainstemType.carney2015:
            retval = (self._ic_bandpass(weights[0] * rcn) +
                      self._ic_band_reject(weights[1] * rcn) +
                      self._ic_lowpass(weights[2] * rcn))
        else:
            raise NotImplementedError

        return retval * M5

    def _simulate(self, weights: [(float, float, float)] = None) -> {}:
        timeLen, cfCount = self.anr.shape
        AN = self.anr
        W1 = np.zeros(timeLen)
        IC = np.zeros(timeLen)
        CN = np.zeros(timeLen)
        RanF = np.zeros((cfCount, timeLen))
        RicF = np.zeros((cfCount, timeLen))
        RcnF = np.zeros((cfCount, timeLen))

        with progressbar.ProgressBar(max_value=cfCount) as bar:
            for i in range(cfCount):

                Rcn = self._cn(i)
                if weights is not None:
                    Ric = self.__simulate_IC(self.brainstemType, Rcn, weights)
                else:
                    Ric = self.__simulate_IC(self.brainstemType, Rcn)

                if i <= self.cutoffCf:
                    W1 += AN[:, i]
                    CN += Rcn[0:timeLen]
                    IC += Ric[0:timeLen]

                RanF[i, :] = AN[:, i]
                RicF[i, :] = Ric[0:timeLen]  # chop off the duplicated convolution side
                RcnF[i, :] = Rcn[0:timeLen]  # chop off the duplicated convolution side
                bar.update(i)
        return {
            b.BrainstemModelType: self.brainstemType.name,
            b.Wave1_AN    : W1,
            b.Wave3_CN    : CN,
            b.Wave5_IC    : IC,
            b.ANPopulation: RanF,
            b.CNPopulation: RcnF,
            b.ICPopulation: RicF
        }
