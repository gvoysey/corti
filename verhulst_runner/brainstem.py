import logging
import multiprocessing as mp
import os
from os import path

import numpy as np
import numpy.matlib
import progressbar

from verhulst_runner.base import runtime_consts, brain_consts as b, periph_consts as p
from .periphery_configuration import PeripheryOutput


def simulate_brainstem(anResults: [(PeripheryOutput, np.ndarray, bool)]) -> [{}]:
    pool = mp.Pool(mp.cpu_count(), maxtasksperchild=1)
    retval = pool.map(solve_one, anResults)
    pool.close()
    pool.join()
    return retval


def solve_one(periphery: (PeripheryOutput, np.ndarray, bool)) -> {}:
    return CentralAuditoryResponse(periphery[0], periphery[1]).run_nc04(periphery[2])


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


NelsonCarney04 = 0
Carney2015 = 1


class CentralAuditoryResponse:
    """
    This class ports the Verhulst implementation of the Nelson and Carney (2004) brainstem and IC model.
    """
    M3 = (1.5 * 0.15e-6) / 0.0036  # idem  with scaling W1
    M5 = (2 * 0.15e-6) / 0.0033  # idem with scaling W1 & 3

    Acn = 1.5
    Aic = 1
    Scn = 0.6
    Sic = 1.5
    Dcn = 1e-3
    Dic = 2e-3
    Tex = 0.5e-3
    Tin = 2e-3

    LowFrequencyCutoff = 175.0  # hz

    def __init__(self, an: PeripheryOutput, anr: np.ndarray):
        self.anr = anr
        self.anfOut = an
        self.Fs = an.conf.Fs
        self.cf = an.output[p.CenterFrequency]
        dur = an.conf.stimulus.shape[1]
        self.time = np.linspace(0, dur / self.Fs, num=dur)
        self.cf = self.anfOut.output[p.CenterFrequency]
        self.cutoffCf = [index for index, value in enumerate(self.cf) if value >= self.LowFrequencyCutoff][-1]

    def run_nc04(self, saveFlag: bool) -> {}:
        """
        Simulate the brainstem and midbrain according to the single IC component system given in
        Nelson, P. C., and Carney, L. H. (2004). “A phenomenological model of peripheral and central
        neural responses to amplitude-modulated tones,” J. Acoust. Soc. Am., 116, 2173. doi:10.1121/1.1784442
        :param saveFlag: If true, output will be saved to disk.
        """
        inhCn = self._make_inhibition_component(self.Scn, self.Dcn)
        inhIc = self._make_inhibition_component(self.Sic, self.Dic)

        output = self._simulate_nelson_carney_04(inhCn, inhIc)
        if saveFlag:
            self._save(output)
        return output

    def run(self, saveFlag: bool) -> {}:

        pass

    def _save(self, output: {}) -> None:
        name = runtime_consts.NelsonCarneyOutputFilePrefix + "{0}dB".format(self.anfOut.stimulusLevel)
        outpath = self.anfOut.outputFolder
        # save the data out to a npz file whose keys are the field names of output.
        np.savez(path.join(outpath, name), **output)
        logging.log(logging.INFO, "wrote {0:<10} to {1}".format(name, path.relpath(outpath, os.getcwd())))

    def _shift(self, delay: float) -> int:
        return int(round(delay * self.Fs))

    def _weight_and_shift_exponential(self, scalingFactor: float) -> np.ndarray:
        """Make a shifted exponential
        Returns $\frac{1}{sF^2}*\vec{t}*e^{\frac{-\vec{t}}{sF}}$
        """
        return np.multiply((1 / (scalingFactor ** 2)) * self.time, np.exp((-1 * self.time) / scalingFactor))

    def _make_inhibition_component(self, s: float, delay: float) -> np.ndarray:
        """ Make the DCN or ICN inhibition component.
        Returns $S_{cn}*\frac{1}{t_{in}^2}*\vec{t}*e^{\frac{-\vec{t}}{t_{in}}}$ time shifted by delay
        :param s: some weighting factor
        :param delay: time period, in units of (Fs^-1)s.  This value will be converted to an integer number of samples.
        """
        lag = self._shift(delay)
        inhibition = s * self._weight_and_shift_exponential(self.Tin)
        return np.pad(inhibition, (lag, 0), 'constant')[:-lag]

    def _simulate_cn(self, cf) -> np.ndarray:
        AN = self.anr
        inhCn = self._make_inhibition_component(self.Scn, self.Dcn)
        Rcn1 = self.Acn * np.convolve(self._weight_and_shift_exponential(self.Tex), AN[:, cf])
        Rcn2 = np.convolve(inhCn, np.roll(AN[:, cf], self._shift(self.Dcn)))
        Rcn = (Rcn1 - Rcn2) * self.M3
        return Rcn

    def _simulate_IC_bandpass(self, rcn):
        """
        Returns the UNWEIGHTED IC modeled as a bank of band-pass filters.
        :param rcn:
        :return:
        """
        inhIc = self._make_inhibition_component(self.Sic, self.Dic)
        Ric1 = self.Aic * np.convolve(self._weight_and_shift_exponential(self.Tex), rcn)
        Ric2 = np.convolve(inhIc, np.roll(rcn, self._shift(self.Dic)))
        Ric = (Ric1 - Ric2)
        return Ric

    def _simulate_IC_lowpass(self, rcn):
        pass

    def _simulate_IC_band_reject(self, rcn):
        pass

    def __simulate_IC(self, modelType: int, rcn: np.ndarray) -> np.ndarray:
        if modelType == NelsonCarney04:
            return self._simulate_IC_bandpass(rcn) * self.M5
        elif modelType == Carney2015:
            pass
        else:
            raise NotImplementedError

    def _simulate_nelson_carney_04(self, inhCn: np.ndarray,
                                   inhIc: np.ndarray) -> {}:
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

                Rcn = self._simulate_cn(i)
                Ric = self.__simulate_IC(NelsonCarney04, Rcn)

                if i <= self.cutoffCf:
                    W1 += AN[:, i]
                    CN += Rcn[0:timeLen]
                    IC += Ric[0:timeLen]

                RanF[i, :] = AN[:, i]
                RicF[i, :] = Ric[0:timeLen]  # chop off the duplicated convolution side
                RcnF[i, :] = Rcn[0:timeLen]  # chop off the duplicated convolution side
                bar.update(i)
        return {
            b.Wave1_AN: W1,
            b.Wave3_CN: CN,
            b.Wave5_IC: IC,
            b.ANPopulation: RanF,
            b.CNPopulation: RcnF,
            b.ICPopulation: RicF
        }
