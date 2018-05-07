from datetime import datetime
from typing import Union
import attr
import numpy as np
from enum import Enum

from corti.base import stim_consts as sc, PeripheryType


class ProbeType(Enum):
    ALL = "all"
    HALF = "half"


class PeripheryConfiguration:
    """
        A PODS holding all the parameters that used to be in input.mat and fully define what's
        needed to run the model.  Default values come from RUN_BMAN.m
        :parameter self.Fs: Model sampling frequency. (default 100 kHz)
        :parameter self.Implementation: unknown, default 0
        :parameter self.NumberOfSections: number of basilar membrane sections to simulate (1000)
        :parameter self.PolesDirectoryName: relative path to PolesFileName
        :parameter self.PolesFileName: name of file containing starting Shera poles
    """

    # Magic Constants.
    Fs = 100000  # Sampling frequency. No idea why Fs is so high.
    Implementation = 0  # no idea what this does (it's not used as of commit 43bf3be01)
    NumberOfSections = 1000  # possibly also "number of frequency bands", if there's a 1:1 between section and cf.

    def __init__(self, dataFolder: str, storeFlag: str, stimuli: dict, modelType: PeripheryType,
                 degradation: Union[tuple, list], pypet: str):
        # model parameters from RUN_BMAN
        # these are used in making the stimulus waveform
        self.modelType = modelType
        self.stimulus_configuration = stimuli
        self.stimulusLevels = stimuli[sc.Levels]
        self.stimulus = stimuli[sc.Stimulus]
        if modelType == PeripheryType.VERHULST:
            # this might be unused.  todo
            self.normalizedRMS = np.zeros(len(self.stimulusLevels))
            self.irregularities = [1] * len(self.stimulusLevels)
            # these are more general
            self.probeString = ProbeType.ALL.name  # sometimes called "Fc".
            self.random_seed = 1
            self.irrPct = 0.05
            self.nonlinearType = "vel"  # todo this is defined in two places
        if modelType == PeripheryType.ZILANY:
            pass
        # operational parameters
        self.dataFolder = dataFolder
        self.storeFlag = storeFlag
        self.degradation = degradation
        self.run_timestamp = datetime.now()
        self.pypet = pypet


@attr.s
class PeripheryOutput:
    """
        PeripheryOutput:
            :parameter self.output: a dict containing the output from the periphery.
            :parameter self.conf: the configuration that generated these outputs
            :type self.conf: PeripheryConfiguration
        :return:
    """
    output = attr.ib(default=None)
    conf = attr.ib(default=None)
    outputFolder = attr.ib(default=None)
