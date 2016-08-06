from logging import error

import matplotlib

matplotlib.use('PDF')
import pandas as pd
from os import path
from datetime import datetime
import glob

from matplotlib.backends.backend_pdf import PdfPages

from matplotlib.ticker import FormatStrFormatter
from pypet import Trajectory
import matplotlib.pyplot as plt

plt.style.use("ggplot")


def print_relevant_properties(runs):
    for r in runs:
        ptype = r.periphery.modelType.casefold()
        btype = r.brainstem.modeltype.modeltype.casefold()
        weighting = "constant" if not r.periphery.cf_weighting else "logistic"
        neuropathy = r.periphery.config.neuropathy
        snr = r.periphery.snr.snr
        print("{0} has periphery: {1}; brainstem {2}; with {3} weighting and neuropathy: {4}.  Stimulus snr was {5}".format(r.v_name, ptype, btype, weighting, neuropathy, snr))


def set_up_plot(runs):
    healthy = [r for r in runs if r.periphery.config.neuropathy == "none"]
    moderate = [r for r in runs if r.periphery.config.neuropathy == "moderate"]
    severe = [r for r in runs if r.periphery.config.neuropathy == "severe"]
    ls_moderate = [r for r in runs if r.periphery.config.neuropathy == "ls-moderate"]
    ls_severe = [r for r in runs if r.periphery.config.neuropathy == "ls-severe"]



def plot_w5peaklatency_vs_snr(traj: Trajectory, pdf, pagenum: int):
    fig = plt.figure(num=pagenum, figsize=(11, 8.5), dpi=400)
    # containing many SNRs and many neuropathies
    verhulst_no_weight_nc04 = [run for run in traj.res.runs if run.periphery.modelType.casefold() == "verhulst" and
                               not run.periphery.cf_weighting and
                               run.brainstem.modeltype.modeltype.casefold() == "nelsoncarney04"]

    d = []
    for run in verhulst_no_weight_nc04:
        d.append({
            'neuropathy' : run.periphery.config.neuropathy,
            'snr'        : run.periphery.snr.snr,
            'peaklatency': (run.brainstem.wave5.wave5.argmax() / 100e3) * 1e3
        })
    df = pd.DataFrame(d)

    ax = df.snr.plot(xticks=df.index)
    ax.set_xticklabels(df.neuropathy)
    ax.set_xlabel("neuropathy type")
    ax.set_ylabel("SNR")
    ax.set_title("foo")
    ax.yaxis.set_major_formatter(FormatStrFormatter('%2.2f'))
    pdf.savefig(fig)
    d = pdf.infodict()
    d['Title'] = 'Auditory Periphery Model Output'
    d['Author'] = "Graham Voysey <gvoysey@bu.edu>"
    d['Keywords'] = 'ABR auditory model periphery'
    d['CreationDate'] = datetime.today()
    d['ModDate'] = datetime.today()


def make_plots(resultsPath):
    traj = Trajectory('tone-in-noise', add_time=False)

    traj.f_load(load_parameters=2, load_derived_parameters=0, load_results=1,
                load_other_data=0, filename=resultsPath)
    traj.v_auto_load = True
    with PdfPages(path.join(path.expanduser('~'), "pypet-output", 'summary.pdf')) as pdf:
        plot_w5peaklatency_vs_snr(traj, pdf, 1)

    return 0


if __name__ == "__main__":
    basepath = path.join(path.expanduser('~'), "pypet-output")
    try:
        make_plots(glob.glob(path.join(basepath, '*.hdf5'))[0])
    except IndexError:
        error("No simulations found to plot.")
