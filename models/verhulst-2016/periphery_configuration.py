"""
This is the container class that replaces input.mat.
"""
import math
from itertools import chain
from os import path

import numpy as np
import yaml

import base


class PeripheryConfiguration:
    """
        A PODS holding all the parameters that used to be in input.mat  and fully define what's
        needed to run the model.  Default values come from RUN_BMAN.m
    """

    # Magic Constants.
    Fs = 100000  # Sampling frequency. No idea why Fs is so high, but i guess we'll find out.
    Implementation = 0  # no idea what this does.
    p0 = 2e-05  # no idea what this even _is_
    NumberOfSections = 1000
    # Operational Constants
    PolesDirectoryName = "sysfiles"
    PolesFileName = "StartingPoles.dat"
    DataFolder = "output"

    def __init__(self):
        # model parameters from RUN_BMAN
        # these are used in making the stimulus waveform
        self.postDuration = round(self.Fs * 50e-3)  # a magic number
        self.preDuration = round(self.Fs * 20e-3)  # a magic number
        self.cDur = round(80e-6 * self.Fs)  # number of elements that have a 1 in them.
        self.stimulus = None  # init as null, we'll make it on demand.
        # these are more general
        self.channels = 2
        self.probeString = ProbeType.All  # sometimes called "Fc".
        self.subject = 1
        # this might be unused.  todo
        self.normalizedRMS = np.zeros((1, self.channels))
        self.stimulusLevels = [60, 80]
        assert len(self.stimulusLevels) == self.channels, "A stimulus level must be given for each channel"
        self.irregularities = [1] * self.channels
        # operational parameters
        self.polePath = path.join(base.rootPath, self.PolesDirectoryName, self.PolesFileName)
        self.dataFolder = path.join(base.rootPath, self.DataFolder)
        self.clean = True
        self.savePeripheryData = True
        # these come from periphery.m
        self.storeFlag = "avihlme"
        self.irrPct = 0.05
        self.nonlinearType = "vel"

        # make the stimulus
        self.generate_stimulus()

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
        :type yamlPath: str
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
    DefaultYamlName = "input.yaml"


class ProbeType:
    All = "all"
    Half = "half"


# @base.as_namedtuple()
class PeripheryOutput:  # namedtuple("Periphery Output",
    #          "bmAcceleration bmVelocity bmDisplacement emission cf ihc anfH anfM anfL")):
    """
        PeripheryOutput:
            :parameter self.bmAcceleration: BM acceleration (store 'a')
            :parameter self.bmVelocity: BM velocity     (store 'v')
            :parameter self.bmDisplacement: BM displacement (store 'y')
            :parameter self.emission: pressure output from the middle ear (store 'e')
            :parameter self.cf: center frequencies (always stored)
            :parameter self.ihc: IHC receptor potential (store 'i')
            :parameter self.anfH: HSR fiber spike probability [0,1] (store 'h')
            :parameter self.anfM: MSR fiber spike probability [0,1] (store 'm')
            :parameter self.anfL: LSR fiber spike probability [0,1] (store 'l')
        :return:
    """

    def __init__(self):
        self.bmAcceleration = None  # not used?
        self.bmVelocity = None
        self.bmDisplacement = None
        self.emission = None
        self.cf = None
        self.ihc = None
        self.anfH = None
        self.anfM = None
        self.anfL = None
