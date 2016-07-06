from enum import Enum
from logging import basicConfig, INFO

import os
import warnings
from collections import namedtuple
from os import path

ProbeType = Enum("ProbeType", "all, half")
PeripheryType = Enum("PeripheryType", "verhulst, zilany")
BrainstemType = Enum('BrainstemType', "nelsoncarney04, carney2015")

# This is the tuple that contains operational constants
RuntimeConstants = namedtuple("Const", " ModelDirectoryLabelName \
                                  DefaultModelOutputDirectoryRoot \
                                  ResultDirectoryNameFormat \
                                  PeripheryOutputFilePrefix \
                                  BrainstemOutputFilePrefix \
                                  AuditoryNerveOutputFilePrefix \
                                  SummaryPlotFileName \
                                  PeripheryConfigurationName \
                                  ResourceDirectoryName \
                                  StimulusTemplateName")

runtime_consts = RuntimeConstants(ModelDirectoryLabelName=".corti-output-root",
                                  DefaultModelOutputDirectoryRoot="corti-output",
                                  ResultDirectoryNameFormat="%d %b %y - %H%M",
                                  PeripheryOutputFilePrefix="periphery-output-",
                                  BrainstemOutputFilePrefix="central-output-",
                                  AuditoryNerveOutputFilePrefix="auditory-nerve-response-",
                                  PeripheryConfigurationName="simulation-configuration.yaml",
                                  SummaryPlotFileName="summary-plots.pdf",
                                  ResourceDirectoryName="resources",
                                  StimulusTemplateName="default_stimulus_template.yaml"
                                  )

# This is the tuple that contains the naming conventions for Periphery output
PeripheryConstants = namedtuple("PeripheryConstants", "BMVelocity \
                                                    BMDisplacement \
                                                    CenterFrequency \
                                                    OtoacousticEmission \
                                                    AuditoryNerveFiberHighSpont \
                                                    AuditoryNerveFiberMediumSpont \
                                                    AuditoryNerveFiberLowSpont \
                                                    InnerHairCell \
                                                    Stimulus \
                                                    StimulusLevel")

periph_consts = PeripheryConstants(BMVelocity="bm_velocity",
                                   BMDisplacement="bm_position",
                                   CenterFrequency="cf",
                                   OtoacousticEmission="emission",
                                   AuditoryNerveFiberHighSpont="an_high_spont",
                                   AuditoryNerveFiberMediumSpont="an_medium_spont",
                                   AuditoryNerveFiberLowSpont="an_low_spont",
                                   InnerHairCell="ihc",
                                   Stimulus="stimulus",
                                   StimulusLevel="stimulus_level")

# This is the tuple that contains the naming conventions for Brainstem output
BrainstemConstants = namedtuple("BrainstemConstants", " Wave1_AN \
                                                        Wave3_CN \
                                                        Wave5_IC \
                                                        ANPopulation \
                                                        CNPopulation \
                                                        ICPopulation \
                                                        BrainstemModelType")

brain_consts = BrainstemConstants(Wave1_AN="wave1_an",
                                  Wave3_CN="wave3_cn",
                                  Wave5_IC="wave5_ic",
                                  ANPopulation="an_pop_resp",
                                  CNPopulation="cn_pop_resp",
                                  ICPopulation="ic_pop_resp",
                                  BrainstemModelType="brainstem-model")

# This is the tuple that contains the naming conventions for the Auditory Nerve output
AuditoryNerveConstants = namedtuple("AuditoryNerveConstants", "LowSR \
                                                               MedSR \
                                                               HighSR \
                                                               SumANR")

an_consts = AuditoryNerveConstants(LowSR="low-sr",
                                   MedSR="med-sr",
                                   HighSR="high-sr",
                                   SumANR="sum-anr")

# This is the tuple that contains the naming conventions for Stimulus specification
StimulusConstants = namedtuple("StimulusConstants", "Click \
                                                     Chirp \
                                                     AM \
                                                     Custom \
                                                     Levels \
                                                     StimulusType \
                                                     Stimulus \
                                                     PrestimTime \
                                                     StimTime \
                                                     PoststimTime ")

stim_consts = StimulusConstants(Click="click",
                                Chirp="chirp",
                                AM="am",
                                Custom="custom",
                                Levels="levels",
                                StimulusType="stimulus_type",
                                Stimulus="stimulus",
                                PrestimTime="prestim_time",
                                StimTime="stim_time",
                                PoststimTime="poststim_time")

# This is the path of __this file__, which we can then base location on
modulePath = os.path.dirname(os.path.abspath(__file__))

# other paths relative to root
stimulusTemplatePath = path.join(modulePath, runtime_consts.ResourceDirectoryName
                                 , runtime_consts.StimulusTemplateName)

# PyYAML and blessed have some warnings we'll suppress
warnings.simplefilter(action="ignore", category=(FutureWarning, UserWarning))
# By default, log INFO and up.
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)