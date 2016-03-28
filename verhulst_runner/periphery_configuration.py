import math
from datetime import datetime

import numpy as np


class PeripheryConfiguration:
    """
        A PODS holding all the parameters that used to be in input.mat  and fully define what's
        needed to run the model.  Default values come from RUN_BMAN.m
        :parameter self.Fs: Model sampling frequency. (default 100 kHz)
        :parameter self.Implementation: unknown, default 0
        :parameter self.p0: no idea.
        :parameter self.NumberOfSections: number of basilar membrane sections to simulate (1000)
        :parameter self.PolesDirectoryName: relative path to PolesFileName
        :parameter self.PolesFileName: name of file containing starting Shera poles
        :parameter self.preDuration:
        :parameter self.postDuration:
    """

    # Magic Constants.
    Fs = 100000  # Sampling frequency. No idea why Fs is so high.
    Implementation = 0  # no idea what this does (it's not used as of commit 43bf3be01)
    p0 = 2e-5  # 20 uPa for dB conversion in stimulus making.
    NumberOfSections = 1000  # possibly also "number of frequency bands", if there's a 1:1 between section and cf.

    def __init__(self, dataFolder: str, storeFlag: str):
        # model parameters from RUN_BMAN
        # these are used in making the stimulus waveform
        self.postDuration = int(round(self.Fs * 50e-3))  # a magic number
        self.preDuration = int(round(self.Fs * 20e-3))  # a magic number
        self.cDur = int(round(80e-6 * self.Fs))  # number of elements that have a 1 in them.
        self.stimulus = None  # init as null, we'll make it on demand.
        # these are more general
        self.probeString = ProbeType.All  # sometimes called "Fc".
        self.subject = 1
        # this might be unused.  todo
        self.stimulusLevels = [60, 80]
        self.normalizedRMS = np.zeros(len(self.stimulusLevels))
        self.irregularities = [1] * len(self.stimulusLevels)
        # operational parameters
        self.dataFolder = dataFolder
        self.storeFlag = storeFlag
        # these come from periphery.m
        self.irrPct = 0.05
        self.nonlinearType = "vel"  # todo this is defined in two places

        self.run_timestamp = datetime.now()

        # make the stimulus
        self.generate_stimulus()

    def generate_stimulus(self) -> None:
        # we can synthesize the stimulus here, somehow(..?!)
        sc = np.hstack([np.zeros(self.preDuration), np.ones(self.cDur), np.zeros(self.postDuration)])
        levels = np.array(self.stimulusLevels)[:, None]
        self.stimulus = 2 * math.sqrt(2) * sc * self.p0 * 10 ** (levels / 20.0)


class ProbeType:
    All = "all"
    Half = "half"


class PeripheryOutput:
    """
        PeripheryOutput:
            :parameter output: a dict containing the output from the periphery.
            :parameter self.conf: the configuration that generated these outputs
            :type self.conf: PeripheryConfiguration
            :parameter self.stimulusLevel: the sound level for this response, dB re 20 uPa
        :return:
    """

    def __init__(self):
        self.output = None
        self.conf = None
        self.stimulusLevel = None
        self.outputFolder = None
