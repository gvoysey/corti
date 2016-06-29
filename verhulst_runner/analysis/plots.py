import glob
from datetime import datetime
from logging import info

import matplotlib
from os import path, walk

matplotlib.use('PDF')
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import yaml
from matplotlib.backends.backend_pdf import PdfPages

from verhulst_runner.base import runtime_consts as r, periph_consts as p
from verhulst_runner.periphery_configuration import PeripheryOutput, PeripheryConfiguration


def plot_periphery(periph: {}, conf: PeripheryConfiguration, pdf: PdfPages) -> plt.Figure:
    figure = plt.figure(1, (8.5, 11), dpi=300)
    figure.suptitle("Verhulst Model Output. Stimulus level {0}dB SPL".format(periph[p.StimulusLevel]),
                    fontsize=18)

    gs = gridspec.GridSpec(6, 4)

    # plot stimulus, top left.
    stimulus = periph[p.Stimulus]
    pointCount = len(stimulus)
    time = np.linspace(0, pointCount / conf.Fs, num=pointCount)
    stimt = plt.subplot(gs[0, :-3])
    stimt.plot(time, stimulus, lw=2)
    stimt.set_xlabel("Time, s")
    stimt.set_ylabel("Amplitude ")
    stimt.set_title("Stimulus")

    # plot FFT of stimulus, top right
    # stimf = plt.subplot(gs[1, 3:-1])


    #Plot


    pdf.savefig(figure)


def plot_brainstem(brainstem_output: {}, conf: PeripheryConfiguration, pdf: PdfPages) -> plt.Figure:
    pass


def plot_anr(anr, conf, pdf):
    pass


def save_summary_pdf(periphery: [], brain: [], anr: [], conf: PeripheryConfiguration, fileName: str, outputPath: str):
    """Make canned summary plots for the provided periphery and brainstem responses, and save them as a PDF.
    """
    if isinstance(periphery[0], PeripheryOutput):
        periph = [x.output for x in periphery]
    else:
        periph = periphery

    # description = """ A {0} dB SPL {1} stimulus with duration {2} was used to simulate the response of the auditory periphery, auditory nerve"""

    # plot the stimulus, a summary of the configuration as a title and text block,
    # different SR fiber responses at some CFs
    # population response of AN, CN, IC ...
    with PdfPages(path.join(outputPath, fileName)) as pdf:
        for i in range(len(periph)):
            plot_periphery(periph[i], conf, pdf)

        if anr is not None:
            for i in range(len(anr)):
                plot_anr(anr[i], conf, pdf)

        if brain is not None:
            for i in range(len(brain)):
                plot_brainstem(brain[i], conf, pdf)

        d = pdf.infodict()
        d['Title'] = 'Auditory Periphery Model Output'
        d['Author'] = "Graham Voysey <gvoysey@bu.edu>"
        d['Keywords'] = 'ABR auditory model periphery'
        d['CreationDate'] = datetime.today()
        d['ModDate'] = datetime.today()


def plot_directory(dirPath: str):
    """Generate summary plots for a stored model simulation"""
    peripheryFiles = glob.glob(path.join(dirPath, r.PeripheryOutputFilePrefix + "*"))
    brainstemFiles = glob.glob(path.join(dirPath, r.NelsonCarneyOutputFilePrefix + "*"))
    configFile = glob.glob(path.join(dirPath, r.PeripheryConfigurationName))[0]

    if not configFile:
        info("No configuration file was found in the directory to be plotted.  Returning.")
        return

    if len(peripheryFiles) != len(brainstemFiles):
        info("Files in the model output directory {0} appear to be missing".format(dirPath))
        return

    save_summary_pdf([np.load(x) for x in peripheryFiles], [np.load(x) for x in brainstemFiles],
                     None, yaml.load(open(configFile)), "summary-plots.pdf", dirPath)


if __name__ == "__main__":
    basepath = path.join(path.expanduser('~'), r.DefaultModelOutputDirectoryRoot)
    result = next(walk(basepath))
    plot_directory(path.join(basepath, result[1][0]))