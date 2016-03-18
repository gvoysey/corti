from os import path


import numpy as np

from brainstem import NelsonCarney04Output
from periphery_configuration import PeripheryOutput, PeripheryConfiguration


def make_summary_plots(periphery: [PeripheryOutput], nc04: [NelsonCarney04Output], fname=None):
    if fname is None:
        fname = path.join(periphery[0].outputFolder, "summary plots.pdf")
    # plot the stimulus, a summary of the configuration as a title and text block,
    # different SR fiber responses at some CFs
    # population response of AN, CN, IC ...
    assert len(periphery) == len(nc04)

    for i in range(len(periphery)):
        periph = periphery[i]
        brain = nc04[i]

        conf = periph.conf
        pointCount = conf.stimulus.shape[1]
        time = np.linspace(0, pointCount / conf.Fs, num=pointCount)

def from_files(dirPath: str):
    pass

def make_title(config: [PeripheryConfiguration]) -> str:
    pass
