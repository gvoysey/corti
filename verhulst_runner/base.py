import os
from collections import namedtuple
from os import path

# This is the tuple that contains operational constants
RuntimeConstants = namedtuple("Const", " ModelDirectoryLabelName \
                                  DefaultModelOutputDirectoryRoot \
                                  ResultDirectoryNameFormat \
                                  PeripheryOutputFilePrefix \
                                  NelsonCarneyOutputFilePrefix \
                                  SummaryPlotFileName \
                                  PeripheryConfigurationName \
                                  ResourceDirectoryName \
                                  StimulusTemplateName")

runtime_consts = RuntimeConstants(ModelDirectoryLabelName=".verhulst-model-output-root",
                                  DefaultModelOutputDirectoryRoot="verhulst-output",
                                  ResultDirectoryNameFormat="%d %b %y - %H%M",
                                  PeripheryOutputFilePrefix="periphery-output-",
                                  NelsonCarneyOutputFilePrefix="nelson-carney-output-",
                                  PeripheryConfigurationName="simulation-configuration.yaml",
                                  SummaryPlotFileName="summary-plots.pdf",
                                  ResourceDirectoryName="resources",
                                  StimulusTemplateName="default_stimulus.yaml"
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
                                                        ICPopulation")

brain_consts = BrainstemConstants(Wave1_AN="wave1_an",
                                  Wave3_CN="wave3_cn",
                                  Wave5_IC="wave3_ic",
                                  ANPopulation="an_pop_resp",
                                  CNPopulation="cn_pop_resp",
                                  ICPopulation="ic_pop_resp")

# This is the path of __this file__, which we can then base location on
rootPath = os.path.dirname(os.path.abspath(__file__))

# other paths relative to root

stimulusTemplatePath = path.join(rootPath, runtime_consts.ResourceDirectoryName
                                 , runtime_consts.StimulusTemplateName)
