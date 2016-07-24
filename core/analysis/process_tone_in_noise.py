from logging import error

from os import path, walk
from pypet import Trajectory


# import matplotlib.pyplot as plt



def make_plots(resultsPath):
    traj = Trajectory('tone-in-noise', add_time=False)

    traj.f_load(load_parameters=2, load_derived_parameters=0, load_results=1,
                load_other_data=0, filename=resultsPath)
    traj.v_auto_load = True

    for run in traj.res.runs:
        w5 = run.brainstem.wave5['wave5']
        peak = max(w5)

    return 0


if __name__ == "__main__":
    basepath = path.join(path.expanduser('~'), "pypet-output")
    result = next(walk(basepath))
    try:
        make_plots(path.join(basepath, result[2][0]))
    except IndexError:
        error("No simulations found to plot.")
