import warnings
from enum import Enum, auto
from logging import basicConfig, INFO
from pathlib import Path

import attr


def sanitize_level(levels: str, delim=','):
    """ Takes a string list of level parameters and converts them to a list of floats.
    """
    if levels is None:
        return
    return [float(f) for f in levels.split(delim) if levels and f]


class PeripheryType(Enum):
    """The model to use for the auditory periphery simulations"""
    VERHULST = auto()
    ZILANY = auto()


class BrainstemType(Enum):
    """The model to use for the auditory brainstem simulations"""
    NELSON_CARNEY_2004 = auto()
    CARNEY_2015 = auto()


@attr.s
class RuntimeConstants:
    """Naming conventions for operational constants"""
    ModelDirectoryLabelName = attr.ib(default=".corti-output-root")
    DefaultModelOutputDirectoryRoot = attr.ib(default="corti-output")
    ResultDirectoryNameFormat = attr.ib(default="%d %b %y - %H%M")
    PeripheryOutputFilePrefix = attr.ib(default="periphery-output-")
    BrainstemOutputFilePrefix = attr.ib(default="central-output-")
    AuditoryNerveOutputFilePrefix = attr.ib(default="auditory-nerve-response-")
    SummaryPlotFileName = attr.ib(default="simulation-configuration.yaml")
    PeripheryConfigurationName = attr.ib(default="summary-plots.pdf")
    ResourceDirectoryName = attr.ib(default="resources")
    StimulusTemplateName = attr.ib(default="default_stimulus_template.yaml")


runtime_consts = RuntimeConstants()


@attr.s
class PeripheryConstants:
    """Naming conventions for Periphery output"""
    BMVelocity = attr.ib(default="bm_velocity")
    BMDisplacement = attr.ib(default="bm_position")
    CenterFrequency = attr.ib(default="cf")
    OtoacousticEmission = attr.ib(default="emission")
    AuditoryNerveFiberHighSpont = attr.ib(default="an_high_spont")
    AuditoryNerveFiberMediumSpont = attr.ib(default="an_medium_spont")
    AuditoryNerveFiberLowSpont = attr.ib(default="an_low_spont")
    InnerHairCell = attr.ib(default="ihc")
    Stimulus = attr.ib(default="stimulus")
    StimulusLevel = attr.ib(default="stimulus_level")


periph_consts = PeripheryConstants()


@attr.s
class BrainstemConstants:
    """naming conventions for Brainstem output"""
    Wave1_AN = attr.ib(default="wave1_an")
    Wave3_CN = attr.ib(default="wave3_cn")
    Wave5_IC = attr.ib(default="wave5_ic")
    ANPopulation = attr.ib(default="an_pop_resp")
    CNPopulation = attr.ib(default="cn_pop_resp")
    ICPopulation = attr.ib(default="ic_pop_resp")
    BrainstemModelType = attr.ib(default="brainstem-model")


brain_consts = BrainstemConstants()


@attr.s
class AuditoryNerveConstants:
    """naming conventions for the Auditory Nerve output"""
    LowSR = attr.ib(default="low-sr")
    MedSR = attr.ib(default="med-sr")
    HighSR = attr.ib(default="high-sr")
    SumANR = attr.ib(default="sum-anr")


an_consts = AuditoryNerveConstants()


@attr.s
class StimulusConstants:
    """naming conventions for Stimulus specification"""
    Click = attr.ib(default="click")
    Chirp = attr.ib(default="chirp")
    AM = attr.ib(default="am")
    Custom = attr.ib(default="custom")
    Levels = attr.ib(default="levels")
    StimulusType = attr.ib(default="stimulus_type")
    Stimulus = attr.ib(default="stimulus")
    PrestimTime = attr.ib(default="prestim_time")
    StimTime = attr.ib(default="stim_time")
    PoststimTime = attr.ib(default="poststim_time")


stim_consts = StimulusConstants()

# This is the path of __this file__, which we can then base location on
modulePath = Path(__file__).parent.resolve()

# other paths relative to root
stimulusTemplatePath = modulePath/runtime_consts.ResourceDirectoryName/runtime_consts.StimulusTemplateName

# PyYAML and blessed have some warnings we'll suppress
warnings.simplefilter(action="ignore", category=(FutureWarning, UserWarning))
# By default, log INFO and up.
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)


@attr.s
class PeripheryOutput:
    """
        PeripheryOutput:
            :parameter self.output: a dict containing the output from the periphery.
            :parameter self.conf: the configuration that generated these outputs
            :type self.conf: corti.periphery.PeripheryConfiguration
        :return:
    """
    output = attr.ib(default=None)
    conf = attr.ib(default=None)
    outputFolder = attr.ib(default=None)