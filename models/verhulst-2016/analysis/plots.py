from os import path

from brainstem import NelsonCarney04Output
from periphery_configuration import PeripheryOutput


def make_summary_plots(periphery: [PeripheryOutput], nc04: [NelsonCarney04Output], fname=None):
    if fname is None:
        fname = path.join(periphery[0].outputFolder, "summary plots.pdf")
        # plot the stimulus, a summary of the configuration as a title and text block,
        # different SR fiber responses at some CFs
        # population response of AN, CN, IC ...
