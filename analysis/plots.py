from datetime import datetime

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from periphery_configuration import PeripheryConfiguration


def make_summary_plots(periphery: [], brain: [], fname):
    assert len(periphery) > 0 and len(brain) > 0 and len(periphery) == len(brain)
    if periphery[0].output is dict:
        pass

    # plot the stimulus, a summary of the configuration as a title and text block,
    # different SR fiber responses at some CFs
    # population response of AN, CN, IC ...
    with PdfPages(fname) as pdf:
        for i in range(len(periphery)):
            figure = plt.figure(1, (8.5, 11), dpi=300)
            gs = gridspec.GridSpec(6, 4)
            periph = periphery[i]
            conf = periph.conf
            pointCount = conf.stimulus.shape[1]
            time = np.linspace(0, pointCount / conf.Fs, num=pointCount)

            # plot stimulus
            stimt = plt.subplot(gs[0, :-3])
            stimt.plot(time, conf.stimulus, lw=2)
            stimt.set_xlabel("Time, s")
            stimt.sey_ylabel("Amplitude ")
            stimt.title()
            stimf = plt.subplot(gs[1, 3:-1])

            # brain = nc04[i]

            figure.suptitle("Verhulst Model Output. Stimulus level {0}dB SPL".format(periph.stimulusLevel), fontsize=18)

        d = pdf.infodict()
        d['Title'] = 'Verhulst Model Output'
        # d['Author'] = ""
        d['Subject'] = 'How to create a multipage pdf file and set its metadata'
        # d['Keywords'] = 'PdfPages multipage keywords author title subject'
        d['CreationDate'] = datetime.today()
        d['ModDate'] = datetime.today()


def from_files(dirPath: str):
    pass

def make_title(config: [PeripheryConfiguration]) -> str:
    pass
