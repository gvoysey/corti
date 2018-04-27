import glob
from datetime import datetime
from logging import info, error

import matplotlib
from os import path, walk

matplotlib.use('PDF')
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import yaml
from matplotlib.backends.backend_pdf import PdfPages

from corti.base import runtime_consts as r, periph_consts as p, brain_consts as b
from corti.periphery_configuration import PeripheryOutput, PeripheryConfiguration

plt.style.use("seaborn-colorblind")

# noinspection PyUnresolvedReferences
def plot_periphery(periph: {}, conf: PeripheryConfiguration, pdf: PdfPages) -> plt.Figure:
    figure = plt.figure(1, (8.5, 11), dpi=300)
    figure.suptitle(
            "{} Model Output: stimulus level {}dB SPL\n".format(conf.modelType.name.title(), periph[p.StimulusLevel]),
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
    combined_data = [periph[p.AuditoryNerveFiberHighSpont], periph[p.AuditoryNerveFiberMediumSpont],
                     periph[p.AuditoryNerveFiberLowSpont]]
    _high, _low = np.amax(combined_data), np.amin(combined_data)

    # Plot raw  high SR
    highs = plt.subplot(gs[2:-2, :-2])
    axh = highs.imshow(periph[p.AuditoryNerveFiberHighSpont].T, extent=extents, cmap=plt.cm.plasma, vmin=_low,
                       vmax=_high)
    # norm=colors.SymLogNorm(linthresh=0.01,vmin=_low, vmax=_high))
    plt.colorbar(axh).set_label('IFR')
    highs.set_yscale('log')
    highs.invert_yaxis()
    highs.set_xlabel("Time (s)")
    highs.set_ylabel("Frequency, Hz")
    highs.set_title("High SR fibers\n")

    meds = plt.subplot(gs[2:-2, 2:])
    axm = meds.imshow(periph[p.AuditoryNerveFiberMediumSpont].T, extent=extents, cmap=plt.cm.plasma, vmin=_low,
                      vmax=_high)
    # norm=colors.SymLogNorm(linthresh=0.01,vmin=_low, vmax=_high))
    plt.colorbar(axm).set_label('IFR')
    meds.set_yscale('log')
    meds.invert_yaxis()
    meds.set_xlabel("Time (s)")
    meds.set_ylabel("Frequency, Hz")
    meds.set_title("Medium SR fibers\n")

    lows = plt.subplot(gs[5:-1, :-2])
    axl = lows.imshow(periph[p.AuditoryNerveFiberLowSpont].T, extent=extents, cmap=plt.cm.plasma, vmin=_low, vmax=_high)
    # norm=colors.SymLogNorm(linthresh=0.01,vmin=_low, vmax=_high))
    plt.colorbar(axl).set_label('IFR')
    lows.set_yscale('log')
    lows.invert_yaxis()
    lows.set_xlabel("Time (s)")
    lows.set_ylabel("Frequency, Hz")
    lows.set_title("Low SR fibers\n")
    # highs.set_xticklabels(time)
    # highs.set_yticklabels(periph[p.CenterFrequency])

    anrs = plt.subplot(gs[5:-1, 2:])
    summed = periph[p.AuditoryNerveFiberLowSpont] + periph[p.AuditoryNerveFiberMediumSpont] + periph[
        p.AuditoryNerveFiberHighSpont]
    axa = anrs.imshow(summed.T, extent=extents, cmap=plt.cm.plasma,
                      norm=colors.SymLogNorm(linthresh=0.01, vmin=_low, vmax=_high))
    plt.colorbar(axa)
    anrs.set_yscale('log')
    anrs.invert_yaxis()
    anrs.set_xlabel("Time (s)")
    anrs.set_ylabel("Frequency, Hz")
    anrs.set_title("Summed and Normalized ANR\n")
    # Make an axis for the colorbar on the right side
    # ax = figure.add_axes([0.9, 0.1, 0.03, 0.8])
    # plt.colorbar(ax).set_label("IFR, s/sec")
    figure.tight_layout()
    pdf.savefig(figure)


def plot_brainstem(brain: {}, conf: PeripheryConfiguration, pdf: PdfPages) -> plt.Figure:
    figure = plt.figure(2, (8.5, 11), dpi=300)
    # figure.suptitle("{} Model Output: stimulus level {}dB SPL\n".format(conf.modelType.name.title(),
    #    str(brain[b.BrainstemModelType]).title()))
    gs = gridspec.GridSpec(6, 4)

    # Plot the ABR
    abr = brain[b.Wave1_AN] + brain[b.Wave3_CN] + brain[b.Wave5_IC]
    pointCount = len(abr)
    time = np.linspace(0, pointCount / conf.Fs, num=pointCount)
    abr_ax = plt.subplot(gs[0, :])
    # plt.xticks(rotation=-70)
    abr_ax.plot(time, abr, lw=2)
    abr_ax.set_xlabel("Time (s)")
    abr_ax.set_ylabel("Amplitude (uV)")
    abr_ax.set_title("ABR\n")

    figure.tight_layout()
    pdf.savefig(figure)


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
    brainstemFiles = glob.glob(path.join(dirPath, r.BrainstemOutputFilePrefix + "*"))
    anrFiles = glob.glob(path.join(dirPath, r.AuditoryNerveOutputFilePrefix + "*"))
    configFile = glob.glob(path.join(dirPath, r.PeripheryConfigurationName))[0]

    if not configFile:
        info("No configuration file was found in the directory to be plotted.  Returning.")
        return

    save_summary_pdf(periphery=[np.load(x) for x in peripheryFiles],
                     brain=[np.load(x) for x in brainstemFiles],
                     anr=[np.load(x) for x in anrFiles],
                     conf=yaml.load(open(configFile)),
                     fileName="summary-plots.pdf",
                     outputPath=dirPath)


if __name__ == "__main__":
    basepath = path.join(path.expanduser('~'), r.DefaultModelOutputDirectoryRoot)
    result = next(walk(basepath))
    try:
        plot_directory(path.join(basepath, result[1][0]))
    except IndexError:
        error("No simulations found to plot.")
