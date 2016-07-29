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


def plot_w5peaklatency_vs_snr(traj: Trajectory, pdf, pagenum: int):
    fig = plt.figure(num=pagenum, figsize=(11, 8.5), dpi=400)
    # containing many SNRs and many neuropathies
    verhulst_no_weight_nc04 = [run for run in traj.res.runs if run.periphery.modelType.casefold() == "verhulst" and
                               not run.periphery.cf_weighting and
                               run.periphery.config.neuropathy.casefold() == "none" and
                               run.brainstem.modeltype.modeltype.casefold() == "nelsoncarney04"]

    d = []
    for run in verhulst_no_weight_nc04:
        d.append({
            'neuropathy' : run.periphery.config.neuropathy,
            'snr'        : run.periphery.snr.snr,
            'peaklatency': (run.brainstem.wave5.wave5.argmax() / 100e3) * 1e3
        })
    df = pd.DataFrame(d)

    ax = df.peaklatency.plot(xticks=df.index)
    ax.set_xticklabels(df.neuropathy)
    ax.set_xlabel("neuropathy type")
    ax.set_ylabel("peak latency (ms)")
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
