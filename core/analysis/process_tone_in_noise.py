from logging import error

import matplotlib
import pandas as pd
from os import path, walk
from pypet import Trajectory

matplotlib.use('PDF')


def plot_w5_vs_neuropathy(traj):
    d = []
    runs_42_snr = [run for run in traj.res.runs if run.periphery.snr.snr == 42.0]
    for run in runs_42_snr:
        d.append({
            'neuropathy' : run.periphery.config.neuropathy,
            'peakwave5'  : max(run.brainstem.wave5.wave5),
            'peaklatency': run.brainstem.wave5.wave5.argmax()
        })
    df = pd.DataFrame(d)
    df.plot()

def plot_w5peaklatency_vs_snr(traj):
    verhulst_healthy_no_weight_nc04 = [run for run in traj.res.runs if run.periphery.modelType.casefold() == "verhulst" and
                                                                       not run.periphery.cf_weighting and
                                                                       run.brainstem.modeltype.modeltype.casefold() == "nelsoncarney04"]




def make_plots(resultsPath):
    traj = Trajectory('tone-in-noise', add_time=False)

    traj.f_load(load_parameters=2, load_derived_parameters=0, load_results=1,
                load_other_data=0, filename=resultsPath)
    traj.v_auto_load = True

    plot_w5_vs_neuropathy(traj)

    return 0


if __name__ == "__main__":
    basepath = path.join(path.expanduser('~'), "pypet-output")
    result = next(walk(basepath))
    try:
        make_plots(path.join(basepath, result[2][0]))
    except IndexError:
        error("No simulations found to plot.")
