import glob
from datetime import datetime
from logging import info
from os import path, walk

import matplotlib

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
    figure.suptitle("{} Model Output: stimulus level {}dB SPL".format(conf.modelType.name.title(), periph[p.StimulusLevel]),
                    fontsize=18)

    gs = gridspec.GridSpec(6, 4)

    # Plot the stimulus
    stimulus = periph[p.Stimulus]
    pointCount = len(stimulus)
    time = np.linspace(0, pointCount / conf.Fs, num=pointCount)
    stimt = plt.subplot(gs[1, :-2])
    # plt.xticks(rotation=-70)
    stimt.plot(time, stimulus, lw=2)
    stimt.set_xlabel("Time (s)")
    stimt.set_ylabel("Pressure (Pa)")
    stimt.set_title("Stimulus\n")

    # Plot Stimulus spectrogram
    stim_spec = plt.subplot(gs[1, 2:])
    pxx, f, t, cax = stim_spec.specgram(stimulus, NFFT=1024, Fs=conf.Fs, noverlap=900,
                                        cmap=plt.cm.plasma)
    figure.colorbar(cax).set_label('Energy')
    stim_spec.set_xlabel("Time (s)")
    stim_spec.set_ylabel("Frequency, Hz")
    stim_spec.set_title("Stimulus spectrogram (fft window 1024)\n")

    extents = [0, pointCount, periph[p.CenterFrequency].min(), periph[p.CenterFrequency].max()]
    # Plot raw  high SR
    highs = plt.subplot(gs[2:-2, :-2])
    axh = highs.imshow(periph[p.AuditoryNerveFiberHighSpont].T, extent=extents, cmap=plt.cm.plasma)
    plt.colorbar(axh).set_label('IFR')
    highs.set_yscale('log')
    highs.invert_yaxis()
    highs.set_xlabel("Time (s)")
    highs.set_ylabel("Frequency, Hz")
    highs.set_title("High SR fibers")

    meds = plt.subplot(gs[2:-2, 2:])
    axm = meds.imshow(periph[p.AuditoryNerveFiberMediumSpont].T, extent=extents, cmap=plt.cm.plasma)
    plt.colorbar(axm).set_label('IFR')
    meds.set_yscale('log')
    meds.invert_yaxis()
    meds.set_xlabel("Time (s)")
    meds.set_ylabel("Frequency, Hz")
    meds.set_title("Medium SR fibers")

    lows = plt.subplot(gs[5:-1, :-2])
    axl = lows.imshow(periph[p.AuditoryNerveFiberLowSpont].T, extent=extents, cmap=plt.cm.plasma)
    plt.colorbar(axl).set_label('IFR')
    lows.set_yscale('log')
    lows.invert_yaxis()
    lows.set_xlabel("Time (s)")
    lows.set_ylabel("Frequency, Hz")
    lows.set_title("Low SR fibers")
    # highs.set_xticklabels(time)
    #highs.set_yticklabels(periph[p.CenterFrequency])

    figure.tight_layout()
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