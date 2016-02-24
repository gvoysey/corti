"""
This is the container class that replaces input.mat.
"""
import yaml
import base
from os import path
import numpy as np

class ProbeType:
    All = "all"
    Half = "half"


class PeripheryConfiguration:



    def __init__(self):
        """
        A PODS holding all the parameters that used to be in input.mat  and fully define what's
        needed to run the model.  Default values come from RUN_BMAN.m
        :return:
        """

        self.polePath = path.join(base.rootPath,"sysfiles","StartingPoles.dat")
        self.Fs = 10000
        self.channels = 2
        self.normalizedRMS = np.zeros((1,self.channels))
        self.subject = 1
        self.stimulusLevels = [60, 80]
        self.irregularities  = [True]*self.channels
        self.probeString = ProbeType.All

    @staticmethod
    def from_yaml(yamlPath: str):
        """
        Factory method for returning a configuration.
        :return:
        """
        assert path.isfile(yamlPath), "no configuration found."
        with open(yamlPath) as _:
            conf = yaml.load(_)
        # read out the dict into a new object here
        retval = PeripheryConfiguration()

        return

class PeripheryOutput:

    def __init__(self):
        """

        :return:
        """

        pass