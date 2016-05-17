import logging
from enum import Enum

import numpy as np
import numpy.matlib
import os
import progressbar
from os import path

from verhulst_runner.base import runtime_consts, brain_consts as b, periph_consts as p
from .periphery_configuration import PeripheryOutput


def simulate_brainstem(anResults: [(PeripheryOutput, np.ndarray, bool)]) -> [{}]:
    # return Parallel(n_jobs=-1, max_nbytes=100e6)(delayed(_solve_one)(x) for x in anResults)
    retval = []
    for i in anResults:
        retval.append(_solve_one(i))
    return retval


def _solve_one(periphery: (PeripheryOutput, np.ndarray, bool)) -> {}:
    return CentralAuditoryResponse(periphery[0], periphery[1]).run(periphery[2])


class AuditoryNerveResponse:
    """Synthesizes an Auditory Nerve population response from the output of a periphery model
    """

    TotalFiberPerIHC = 19  # to match the verhulst model scaling.
    M1 = 0.15e-6 / 2.7676e+07  # last value is uncompensated at 100 dB

    def __init__(self, an: PeripheryOutput):
        self.anfOut = an
        self.Fs = an.conf.Fs
        self.cf = an.output[p.CenterFrequency]
        self.anfh = self.anfOut.output[p.AuditoryNerveFiberHighSpont]
        self.anfm = self.anfOut.output[p.AuditoryNerveFiberMediumSpont]
        self.anfl = self.anfOut.output[p.AuditoryNerveFiberLowSpont]
        self.timeLen, self.cfCount = self.anfh.shape
        self.lowSR = None
        self.medSR = None
        self.highSR = None
        self.ANR = None

    def unweighted_an_response(self, ls_normal: float = 3, ms_normal: float = 3, hs_normal: float = 13,
                               degradation: () = None) -> np.ndarray:
        """Create an auditory nerve population response with a fixed distribution of fiber types per hair cell.
        Contains the contributions of low, medium, and high spontaneous rate fibers individually weighted by fiber count.
        An optional parameter for modeling hair cell loss is available.
        :param ls_normal: The number of low spont rate fibers per IHC
        :param ms_normal: The number of medium spont rate fibers per IHC
        :param hs_normal: The number of high spont rate fibers per IHC
        :param degradation: a tuple representing how much each fiber type should be degraded.
                            Values should be either scalar or ndarrays of the same shape as each fiber
                            type component, and contain values between zero and one.
        :return: the AN population response.
        """
        if (ls_normal + ms_normal + hs_normal) - self.TotalFiberPerIHC > 0.0001:
            logging.error("More fibers per IHC were specified than the Verhulst model currently supports!")

        return self.sum_fibers(ls_normal, ms_normal, hs_normal, degradation)

    def cf_weighted_an_response(self, degradation: () = None) -> np.ndarray:
        """Create an auditory nerve population response with a logistic distribution of fiber types per hair cell.
        Contains the contributions of low, medium, and high spontaneous rate fibers individually weighted by fiber count.
        An optional parameter for modeling hair cell loss is available.
        :param degradation: a tuple representing how much each fiber type should be degraded.
                            Values should be either scalar or ndarrays of the same shape as each fiber
                            type component, and contain values between zero and one.
        :return: the AN population response
        """
        lsr_weight, msr_weight, hsr_weight = self._map_cf_dependent_distribution(self.TotalFiberPerIHC)

        return self.sum_fibers(lsr_weight, msr_weight, hsr_weight, degradation)

    def sum_fibers(self, ls_weight, ms_weight, hs_weight, degradation=None):
        cfs = self.cfCount
        timeLen = self.timeLen

        if degradation is not None:
            ls_weight, ms_weight, hs_weight = self.degrade_an_components(ls_weight, ms_weight, hs_weight, degradation)

        lsr = numpy.matlib.repmat(ls_weight * np.ones((1, cfs)), timeLen, 1) * self.anfl
        msr = numpy.matlib.repmat(ms_weight * np.ones((1, cfs)), timeLen, 1) * self.anfm
        hsr = numpy.matlib.repmat(hs_weight * np.ones((1, cfs)), timeLen, 1) * self.anfh

        self.lowSR = lsr
        self.medSR = msr
        self.highSR = hsr
        self.ANR = (lsr + msr + hsr) * self.M1
        return self.ANR

    def _map_cf_dependent_distribution(self, total_fiber_scaling_factor=1) -> ():
        """Returns a distribution percentage of hair cell SR types as a function of CF.
        Distribution statistics taken from
        Temchin, A. N., Rich, N. C., and Ruggero, M. a (2008). “Threshold Tuning Curves of Chinchilla Auditory Nerve
        Fibers II: Dependence on Spontaneous Activity and Relation to Cochlear Nonlinearity,” J. Neurophysiol., 100,
        2899–2906. doi:10.1152/jn.90639.2008
        and
        Bourien, J., Tang, Y., Batrel, C., Huet, A., Lenoir, M., Ladrech, S., Desmadryl, G., et al. (2014).
        “Contribution of auditory nerve fibers to compound action potential of the auditory nerve,” J. Neurophysiol.,
        112, 1025–1039. doi:10.1152/jn.00738.2013
        """
        # The SR cutoff used by Temchin et. al. for "low SR" is 18.
        # The Verhulst model's medium and low SR fibers are both below that threshold, so we assign half weight to each.
        # scale the percentages to "fiber counts" by multiplying by how many fibers are present on a healthy IHC.
        # getting non-integer values for "number of fibers" is OK here; we're modeling population-level behavior.
        return (total_fiber_scaling_factor * np.array([self.percent_sr(c) / 2 for c in self.cf]),
                total_fiber_scaling_factor * np.array([self.percent_sr(c) / 2 for c in self.cf]),
                total_fiber_scaling_factor * np.array([1 - self.percent_sr(c) for c in self.cf]))

    def percent_sr(self, cf):
        """
        Returns the  percentage of AN fibers with a SR < 18 s/s as a function of CF, per Temchin and Ruggero (2008).  Distribution is modeled as a logistic function.
        """
        # k r and t0 were optimized externally.
        k = 22
        r = .0009
        cf0 = 2500
        return (21 + k / (1 + np.exp(-r * (cf - cf0)))) / 100

    def degrade_an_components(self, low: np.ndarray, medium: np.ndarray, high: np.ndarray, degradation: ()):
        return (low * degradation[0],
                medium * degradation[1],
                high * degradation[2])


ModelType = Enum('ModelType', "NelsonCarney04, Carney2015")


class CentralAuditoryResponse:
    """
    This class implements the midbrain and brainstem models developed by Laurel Carney et al, and set forth in
    - Nelson, P. C., and Carney, L. H. (2004). “A phenomenological model of peripheral and central
    neural responses to amplitude-modulated tones,” J. Acoust. Soc. Am., 116, 2173. doi:10.1121/1.1784442
    - Carney, L. H., Li, T., and McDonough, J. M. (2015). “Speech Coding in the Brain: Representation of Vowel
    Formants by Midbrain Neurons Tuned to Sound Fluctuations,” eNeuro, 2, 1–12. doi:10.1523/ENEURO.0004-15.2015
    """

    LowFrequencyCutoff = 175.0  # in Hz.  CFs below this threshold will not be used to estimate the compound action potential

    def __init__(self, an: PeripheryOutput, anr: np.ndarray):
        self.anr = anr
        self.anfOut = an
        self.Fs = an.conf.Fs
        self.cf = an.output[p.CenterFrequency]
        dur = an.conf.stimulus.shape[1]
        self.time = np.linspace(0, dur / self.Fs, num=dur)
        self.cf = self.anfOut.output[p.CenterFrequency]
        self.cutoffCf = [index for index, value in enumerate(self.cf) if value >= self.LowFrequencyCutoff][-1]

    def run(self, saveFlag: bool, modelType: ModelType = ModelType.NelsonCarney04) -> {}:
        """
        Simulate the brainstem and midbrain according to the single IC component system given in
        Nelson, P. C., and Carney, L. H. (2004). “A phenomenological model of peripheral and central
        neural responses to amplitude-modulated tones,” J. Acoust. Soc. Am., 116, 2173. doi:10.1121/1.1784442
        :param saveFlag: If true, output will be saved to disk.
        """

        output = self._simulate(modelType)
        if saveFlag:
            self._save(output)
        return output

    def _save(self, output: {}) -> None:
        name = runtime_consts.NelsonCarneyOutputFilePrefix + "{0}dB".format(self.anfOut.stimulusLevel)
        outpath = self.anfOut.outputFolder
        # save the data out to a npz file whose keys are the field names of output.
        np.savez(path.join(outpath, name), **output)
        logging.log(logging.INFO, "wrote {0:<10} to {1}".format(name, path.relpath(outpath, os.getcwd())))

    def _shift(self, delay: float) -> int:
        return int(round(delay * self.Fs))

    def __alpha(self, scalingFactor: float) -> np.ndarray:
        """Make an alpha function of the form
        $\frac{1}{sF^2}*\vec{t}*e^{\frac{-\vec{t}}{sF}}$
        """
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
        Aic = 1
        Sic = 1.5
        Dic = 2e-3
        Tex = 0.5e-3
        Tin = 2e-3
        return self._ic(rcn, Aic, Sic, Dic, Tin, Tex)

    def _ic_lowpass(self, rcn):
        Aic = 1
        Sic = 1.5
        Dic = 2e-3
        Tex = 2e-3
        Tin = 5e-3
        return self._ic(rcn, Aic, Sic, Dic, Tin, Tex)

    def _ic_band_reject(self, rcn):
        Aic = 1
        Sic = 1.5
        Dic = 2e-3
        Tex = 0.5e-3
        Tin = 2e-3
        return self._ic(rcn, Aic, Sic, Dic, Tin, Tex)

    def __simulate_IC(self, modelType: ModelType, rcn: np.ndarray, weights=(.5, .25, .25)) -> np.ndarray:
        M5 = (2 * 0.15e-6) / 0.0033  # idem with scaling W1 & 3

        if modelType == ModelType.NelsonCarney04:
            retval = self._ic_bandpass(rcn)
        elif modelType == ModelType.Carney2015:
            retval = (self._ic_bandpass(weights[0] * rcn) +
                      self._ic_band_reject(weights[1] * rcn) +
                      self._ic_lowpass(weights[2] * rcn))
        else:
            raise NotImplementedError

        return retval * M5

    def _simulate(self, modelType: ModelType = ModelType.NelsonCarney04, weights: [(float, float, float)] = None) -> {}:
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
                    Ric = self.__simulate_IC(modelType, Rcn, weights)
                else:
                    Ric = self.__simulate_IC(modelType, Rcn)

                if i <= self.cutoffCf:
                    W1 += AN[:, i]
                    CN += Rcn[0:timeLen]
                    IC += Ric[0:timeLen]

                RanF[i, :] = AN[:, i]
                RicF[i, :] = Ric[0:timeLen]  # chop off the duplicated convolution side
                RcnF[i, :] = Rcn[0:timeLen]  # chop off the duplicated convolution side
                bar.update(i)
        return {
            b.Wave1_AN    : W1,
            b.Wave3_CN    : CN,
            b.Wave5_IC    : IC,
            b.ANPopulation: RanF,
            b.CNPopulation: RcnF,
            b.ICPopulation: RicF
        }
