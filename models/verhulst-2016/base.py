import os
from collections import namedtuple

rootPath = os.path.dirname(os.path.abspath(__file__))

RuntimeConstants = namedtuple("Const", "ModelDirectoryLabelName\
                                  DefaultModelOutputDirectoryRoot\
                                  ResultDirectoryNameFormat\
                                  PeripheryOutputFilePrefix\
                                  NelsonCarneyOutputFilePrefix\
                              ")

const = RuntimeConstants(ModelDirectoryLabelName=".verhulst-model-output-root",
                         DefaultModelOutputDirectoryRoot="verhulst-output",
                         ResultDirectoryNameFormat="%d %b %y - %H%M",
                         PeripheryOutputFilePrefix="periphery-output-",
                         NelsonCarneyOutputFilePrefix="nelson-carney-output-"
                         )
