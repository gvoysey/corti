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
import numpy as np

plt.style.use("ggplot")


def print_relevant_properties(runs):
    for r in runs:
        ptype = r.periphery.modelType.casefold()
        btype = r.brainstem.modeltype.modeltype.casefold()
        weighting = "constant" if not r.periphery.cf_weighting else "logistic"
        neuropathy = r.periphery.config.neuropathy
        snr = r.periphery.snr.snr
        print(
                "{0} has periphery: {1}; brainstem {2}; with {3} weighting and neuropathy: {4}.  Stimulus snr was {5}".format(
                        r.v_name, ptype, btype, weighting, neuropathy, snr))


def plot_condition(runs_tuple, pdf, pagenum):
    run_name, runs = runs_tuple

    lines = {
        'healthy'    : [r for r in runs if r.periphery.config.neuropathy == "none"],
        'moderate'   : [r for r in runs if r.periphery.config.neuropathy == "moderate"],
        'severe'     : [r for r in runs if r.periphery.config.neuropathy == "severe"],
        'ls_moderate': [r for r in runs if r.periphery.config.neuropathy == "ls-moderate"],
        'ls_severe'  : [r for r in runs if r.periphery.config.neuropathy == "ls-severe"],
    }
    fig = plt.figure(num=pagenum, figsize=(11, 8.5), dpi=400)
    # plt.hold(True)
    legend_text = []
    max = -float("inf")
    min = float("inf")

    for l in lines.items():
        for run in l:
            val = run.brainstem.wave5.wave5.argmax()
            if val < min:
                min = val
            if val > max:
                max = val

    for name, l in lines.items():
        print("\t neuropathy {0} had {1} runs".format(name, len(l)))
        d = []
        for run in l:
            d.append({
                'snr'           : run.periphery.snr.snr,
                'peaklatency'   : (run.brainstem.wave5.wave5.argmax() / 100e3) * 1e3,
                'wave1amplitude': run.brainstem.wave1.wave1.max()
            })
        legend_text.append(name)
        df = pd.DataFrame(d)
        df = df.replace(np.inf, 0)
        df.sort_values('snr', inplace=True)
        print(df)
        plt.plot(df.snr, df.wave1amplitude)
        ax = plt.gca()
        ax.set_xticks(df.snr)
        ax.set_xticklabels(df.snr)
        ax.set_xlabel("SNR")
        ax.set_ylabel("Peak Wave V Latency")
        ax.set_ylim([min, max])
        ax.yaxis.set_major_formatter(FormatStrFormatter('%2.2f'))
    plt.legend(legend_text)
    plt.title(run_name)
    pdf.savefig(fig)


def plot_w5peaklatency_vs_snr(traj: Trajectory, pdf):
    # containing many SNRs and many neuropathies
    conditions = {
        'verhulst_no_weight_nc04'  : [run for run in traj.res.runs if
                                      run.periphery.modelType.casefold() == "verhulst" and
                                      not run.periphery.cf_weighting and
                                      run.brainstem.modeltype.modeltype.casefold() == "nelsoncarney04"],
        'verhulst_no_weight_carney': [run for run in traj.res.runs if
                                      run.periphery.modelType.casefold() == "verhulst" and
                                      not run.periphery.cf_weighting and
                                      run.brainstem.modeltype.modeltype.casefold() == "carney2015"],
        'verhulst_weighted_nc04'   : [run for run in traj.res.runs if
                                      run.periphery.modelType.casefold() == "verhulst" and
                                      run.periphery.cf_weighting and
                                      run.brainstem.modeltype.modeltype.casefold() == "nelsoncarney04"],
        'verhulst_weighted_carney' : [run for run in traj.res.runs if
                                      run.periphery.modelType.casefold() == "verhulst" and
                                      run.periphery.cf_weighting and
                                      run.brainstem.modeltype.modeltype.casefold() == "carney2015"],
        'zilany_no_weight_nc04'    : [run for run in traj.res.runs if run.periphery.modelType.casefold() == "zilany" and
                                      not run.periphery.cf_weighting and
                                      run.brainstem.modeltype.modeltype.casefold() == "nelsoncarney04"],
        'zilany_no_weight_carney'  : [run for run in traj.res.runs if run.periphery.modelType.casefold() == "zilany" and
                                      not run.periphery.cf_weighting and
                                      run.brainstem.modeltype.modeltype.casefold() == "carney2015"],
        'zilany_weighted_nc04'     : [run for run in traj.res.runs if run.periphery.modelType.casefold() == "zilany" and
                                      run.periphery.cf_weighting and
                                      run.brainstem.modeltype.modeltype.casefold() == "nelsoncarney04"],
        'zilany_weighted_carney'   : [run for run in traj.res.runs if run.periphery.modelType.casefold() == "zilany" and
                                      run.periphery.cf_weighting and
                                      run.brainstem.modeltype.modeltype.casefold() == "carney2015"],
    }

    for i, c in enumerate(conditions.items()):
        print("{0}, got {1} runs to plot".format(i, len(c[1])))
        plot_condition(c, pdf, i)

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
        plot_w5peaklatency_vs_snr(traj, pdf)

    return 0


if __name__ == "__main__":
    basepath = path.join(path.expanduser('~'), "Desktop")
    try:
        make_plots(glob.glob(path.join(basepath, '*.hdf5'))[0])
    except IndexError:
        error("No simulations found to plot.")
