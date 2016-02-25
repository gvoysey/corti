"""
This is the container class that replaces input.mat.
"""
import yaml
import base
from os import path
from itertools import chain
import numpy as np
import math


class PeripheryConfiguration:
    """
        A PODS holding all the parameters that used to be in input.mat  and fully define what's
        needed to run the model.  Default values come from RUN_BMAN.m
    """

    # Magic Constants.
    Fs = 100000  # Sampling frequency. No idea why Fs is so high, but i guess we'll find out.
    Implementation = 0  # no idea what this does.
    p0 = 2e-05  # no idea what this even _is_

    # Operational Constants
    PolesDirectoryName = "sysfiles"
    PolesFileName = "StartingPoles.dat"
    DataFolder = "output"

    def __init__(self):
        # model parameters
        # these are used in making the stimulus waveform
        self.postDuration = round(self.Fs * 50e-3)  # a magic number
        self.preDuration = round(self.Fs * 20e-3)  # a magic number
        self.cDur = round(80e-6 * self.Fs)  # number of elements that have a 1 in them.
        # these are more general
        self.channels = 2
        self.probeString = ProbeType.All
        self.subject = 1
        # this might be unused.
        self.normalizedRMS = np.zeros((1, self.channels))
        self.stimulusLevels = [60, 80]
        assert len(self.stimulusLevels == self.channels), "A stimulus level must be given for each channel"
        self.irregularities = [True] * self.channels

        # operational parameters
        self.polePath = path.join(base.rootPath, self.PolesDirectoryName, self.PolesFileName)
        self.dataFolder = path.join(base.rootPath, self.DataFolder)

        self.stimulus = None

    def generate_stimulus(self):
        # we can synthesize the stimulus here, somehow(..?!)
        sc = list(chain([0] * self.preDuration, [1] * self.cDur, [0] * self.postDuration))
        stim = np.empty([len(self.stimulusLevels), len(sc)])

        for i in range(len(self.stimulusLevels)):
            stim[i, :] = np.multiply(2 * math.sqrt(2) * 2e0 - 5 * pow(10, self.stimulusLevels[i] / 20.0), sc)
            # todo : stim[1,:] seems empty ?
        # and define the stimulus here.
        self.stimulus = stim

    @staticmethod
    def from_yaml(yamlPath: str):
        """
        Factory method for returning a configuration.
        :param yamlPath: a fully qualified path the the stored configuration file.
        :return: An instance of a configuration class
        """
        assert path.isfile(yamlPath), "no configuration found."
        with open(yamlPath) as _:
            conf = yaml.load(_)
        # read out the dict into a new object here
        retval = PeripheryConfiguration()

        # parse in model parameters
        # todo: more rigorous input checking here.
        retval.channels = conf[Constants.Channels]
        probe = conf[Constants.ProbeType]
        if probe.lower() == "all":
            retval.probeString = ProbeType.All
        elif probe.lower() == "half":
            retval.probeString = ProbeType.Half
        else:
            raise SyntaxError("probe string not recognized; must be `half` or `all`")
        retval.subject = conf[Constants.Subject]
        retval.normalizedRMS = np.zeros((1, retval.channels))
        retval.stimulusLevels = conf[Constants.StimulusLevels]
        retval.irregularities = [conf[Constants.Irregularities]] * retval.channels

        # stimulus generation
        retval.generate_stimulus()
        return retval


class Constants:
    """
    This is a class that holds constant string values that define the YAML syntax for storing a periphery configuration.
    """
    Channels = "channels"
    ProbeType = "probeType"
    Subject = "subject"
    StimulusLevels = "stimulusLevels"
    Irregularities = "irregularities"

    # operational parameter defaults (optional)


class ProbeType:
    All = "all"
    Half = "half"


class PeripheryOutput:
    def __init__(self):
        """

        :return:
        """

        pass
