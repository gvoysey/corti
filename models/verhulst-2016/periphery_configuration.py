"""
This is the container class that replaces input.mat.
"""
import math
from os import path

import numpy as np
import yaml

import base


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
        :parameter self.DataFolder: base relative directory name to where model output directories are stored.
        :parameter self.preDuration:
        :parameter self.postDuration:

    """

    # Magic Constants.
    Fs = 100000  # Sampling frequency. No idea why Fs is so high, but i guess we'll find out.
    Implementation = 0  # no idea what this does.
    p0 = 2e-5  # no idea what this even _is_
    NumberOfSections = 1000
    # Operational Constants
    PolesDirectoryName = "sysfiles"
    PolesFileName = "StartingPoles.dat"
    DataFolder = "output"

    def __init__(self):
        # model parameters from RUN_BMAN
        # these are used in making the stimulus waveform
        self.postDuration = int(round(self.Fs * 50e-3))  # a magic number
        self.preDuration = int(round(self.Fs * 20e-3))  # a magic number
        self.cDur = int(round(80e-6 * self.Fs))  # number of elements that have a 1 in them.
        self.stimulus = None  # init as null, we'll make it on demand.
        # these are more general
        self.channels = 2
        self.probeString = ProbeType.All  # sometimes called "Fc".
        self.subject = 1
        # this might be unused.  todo
        self.normalizedRMS = np.zeros(self.channels)
        self.stimulusLevels = [60, 80]
        assert len(self.stimulusLevels) == self.channels, "A stimulus level must be given for each channel"
        self.irregularities = [1] * self.channels
        # operational parameters
        self.polePath = path.join(base.rootPath, self.PolesDirectoryName, self.PolesFileName)
        self.dataFolder = path.join(base.rootPath, self.DataFolder)
        self.clean = True
        self.savePeripheryData = True
        # these come from periphery.m
        self.storeFlag = "avihlmes"
        self.irrPct = 0.05
        self.nonlinearType = "vel"

        # make the stimulus
        self.generate_stimulus()

    def generate_stimulus(self):
        # we can synthesize the stimulus here, somehow(..?!)
        sc = np.hstack([np.zeros(self.preDuration), np.ones(self.cDur), np.zeros(self.postDuration)])
        levels = np.array(self.stimulusLevels)[:, None]
        self.stimulus = 2 * math.sqrt(2) * sc * self.p0 * 10 ** (levels / 20.0)

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


class PeripheryOutput:
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
            :parameter self.conf: the configuration that generated these outputs
            :type self.conf: PeripheryConfiguration
            :parameter self.stimulusLevel: the sound level for this response, dB re 20 uPa
        :return:
    """

    def __init__(self):
        self.bmAcceleration = None
        self.bmVelocity = None
        self.bmDisplacement = None
        self.emission = None
        self.cf = None
        self.ihc = None
        self.anfH = None
        self.anfM = None
        self.anfL = None
        self.conf = None
        self.stimulusLevel = None
        self.outputFolder = None
