from logging import error

import pandas as pd
from os import path, walk
from pypet import Trajectory


# import matplotlib.pyplot as plt


def plot_w5_vs_neuropathy(traj):
    d = []
    for run in traj.res.runs:
        d.append({
            'neuropathy': run.periphery.config.neuropathy,
            'peakwave5' : max(run.brainstem.wave5.wave5),
        })
    df = pd.DataFrame(d)
    df.plot()


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
