import logging
from typing import Union

import numpy as np
import numpy.matlib
from os import path

from corti import PeripheryOutput, PeripheryType, periph_consts as p, runtime_consts as r, an_consts as a


class AuditoryNerveResponse:
    """Synthesizes an Auditory Nerve population response from the output of a periphery model
    """

    TotalFiberPerIHC = 19  # to match the verhulst model scaling.
    M1 = 0.15e-6 / 2.7676e+07  # last value is uncompensated at 100 dB
    # Z1 = 2.05400E-15  # determined by running `find_v1.py`
    Z1 = 0.15e-6 / 7.30282e+07

    def __init__(self, an: PeripheryOutput, degradation: str):
        """

        :param an:
        :param degradation: a tuple representing how much each fiber type should be degraded.
                            Values should be either scalar or ndarrays of the same shape as each fiber
                            type component, and contain values between zero and one.
        """
        self.periph = an
        self.Fs = an.conf.Fs
        self.cf = an.output[p.CenterFrequency]
        self.anfh = an.output[p.AuditoryNerveFiberHighSpont]
        self.anfm = an.output[p.AuditoryNerveFiberMediumSpont]
        self.anfl = an.output[p.AuditoryNerveFiberLowSpont]
        self.timeLen, self.cfCount = self.anfh.shape
        self.degradation = self.parse_degradation(degradation)
        self.lowSR = None
        self.medSR = None
        self.highSR = None
        self.ANR = None

    def save(self):
        if self.periph.conf.pypet:
            return
        # todo: make this follow the naming conventions in base.py.
        name = r.AuditoryNerveOutputFilePrefix + "{0}dB".format(self.periph.output[p.StimulusLevel])
        outpath = self.periph.outputFolder
        # save the data out to a npz file whose keys are the field names of output.
        np.savez(path.join(outpath, name), **{
            a.LowSR : self.lowSR,
            a.MedSR : self.medSR,
            a.HighSR: self.highSR,
            a.SumANR: self.ANR
        })
        logging.info("wrote {0:<10} to {1}".format(name, path.abspath(outpath)))

    def unweighted_an_response(self, ls_normal: float = 3, ms_normal: float = 3, hs_normal: float = 13) -> np.ndarray:
        """Create an auditory nerve population response with a fixed distribution of fiber types per hair cell.
        Contains the contributions of low, medium, and high spontaneous rate fibers individually weighted by fiber count.
        An optional parameter for modeling hair cell loss is available.
        :param ls_normal: The number of low spont rate fibers per IHC
        :param ms_normal: The number of medium spont rate fibers per IHC
        :param hs_normal: The number of high spont rate fibers per IHC

        :return: the AN population response.
        """
        if (ls_normal + ms_normal + hs_normal) - self.TotalFiberPerIHC > 0.0001:
            logging.error("More fibers per IHC were specified than the Verhulst model currently supports!")

        return self.sum_fibers(ls_normal, ms_normal, hs_normal, self.degradation)

    def cf_weighted_an_response(self) -> np.ndarray:
        """Create an auditory nerve population response with a logistic distribution of fiber types per hair cell.
        Contains the contributions of low, medium, and high spontaneous rate fibers individually weighted by fiber count.

        :return: the AN population response
        """
        lsr_weight, msr_weight, hsr_weight = self._map_cf_dependent_distribution(self.TotalFiberPerIHC)

        return self.sum_fibers(lsr_weight, msr_weight, hsr_weight, self.degradation)

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
        if self.periph.conf.modelType == PeripheryType.verhulst:
            self.ANR = (lsr + msr + hsr) * self.M1
        elif self.periph.conf.modelType == PeripheryType.zilany:
            self.ANR = (lsr + msr + hsr) * self.Z1
        else:
            raise TypeError("periphery type {} not found".format(self.periph.conf.modelType.name))
        self.save()
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
        # The Verhulst model's medium and low SR fibers (10 and 1 ) are both below that threshold, so we assign half weight to each.
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

    def parse_degradation(self, d: str) -> Union[tuple, list]:
        """
        Converts user input strings into neuropathy degradation parameters.
        :param d:
        :return:
        """
        if d is None:
            return 1, 1, 1
        else:
            return {
                "none"       : (1, 1, 1),
                "mild"       : (0.9, 0.9, 0.9),
                "moderate"   : (0.75, 0.75, 0.75),
                "severe"     : (0.50, 0.50, 0.50),
                "ls-mild"    : (1, 0.9, 0.9),
                "ls-moderate": (1, 0.75, 0.75),
                "ls-severe"  : (1, 0.5, 0.5),
            }.get(d.casefold(), (1, 1, 1))
