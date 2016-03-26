"""
Verhulst Model.

Usage:
    verhulst_model -h | --help
    verhulst_model --version
    verhulst_model [--out <outpath>]  [-c | --clean]  [-v | --verbose] [--pSave <peripheryFlag>] [--bSave] [--noBrainstem]

Options:
    -h --help   Show this screen and exit.
    --version   Display the version and exit.
    --out=<outpath>     Specify the output location for saved data. [default: ~/verhulst-output]
    --pSave=<peripheryFlag>      Which components of the peripheral response to save.  [default: cavihlmesd]
    --bSave      Brainstem output will be saved if set.
    --noBrainstem   Simulate the periphery only.
    -c --clean  Previous runs will be deleted to save disk space.
    -v --verbose    Display detailed debug log output to STDOUT.
"""
import sys
from datetime import datetime
from logging import info, basicConfig, getLogger, ERROR, INFO

import os
import shutil
import warnings
from base import runtime_consts
from docopt import docopt
from os import path, system, name
from periphery_configuration import PeripheryConfiguration
from run_periphery import RunPeriphery

from verhulst_runner.analysis.plots import save_summary_pdf
from verhulst_runner.brainstem import simulate_brainstem
from . import __version__

# PyYAML has some warnings we'll suppress
warnings.simplefilter(action="ignore", category=FutureWarning)
# By default, log INFO and up.
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)


def main():
    # get the command line args
    args = docopt(__doc__, version=__version__)

    # configure the log level appropriately
    if not args["--verbose"]:
        getLogger().setLevel(ERROR)

    # actually run the simulation
    system('cls' if name == 'nt' else 'clear')
    info("output directory set to {0}".format(__set_output_dir(args["--out"])))
    conf = PeripheryConfiguration(__set_output_dir(args["--out"]), args["--pSave"])

    print("Simulating periphery and auditory nerve...")
    anResults = RunPeriphery(conf).run()

    brainResults = None
    if not args["--noBrainstem"]:
        print("Simulating brainstem response")
        brainResults = simulate_brainstem([(anr, args["--bSave"]) for anr in anResults])

    print("Generating summary figures")
    save_summary_pdf(anResults, brainResults, conf, "summary-plots.pdf", anResults[0].outputFolder)

    if args["--clean"]:
        print("Cleaning old model runs ... ")
        __clean(conf.dataFolder, anResults[0].outputFolder)

    print("Simulation finished.")

    sys.exit(0)


def __clean(rootDir: str, current_results: str) -> None:
    """
    Removes all the previous model runs except the current one found in the current base output directory.
    All directories that are named like model output directories are removed recursively; no other files are touched.
    """
    contents = os.listdir(rootDir)
    if runtime_consts.ModelDirectoryLabelName not in contents:
        info("Specified directory was not a model output directory. No data removed.")
        return
    info("cleaning up...")
    for d in contents:
        if (not d == path.basename(current_results)) and \
                path.isdir(path.join(rootDir, d)) and \
                datetime.strptime(d, runtime_consts.ResultDirectoryNameFormat):
            shutil.rmtree(path.join(rootDir, d))
            info("removed " + d)
    info("cleaned.")
    pass


def __touch(fname, times=None):
    """ As coreutils touch; may not work on windows.
    """
    with open(fname, 'a+'):
        os.utime(fname, times)


def __set_output_dir(temp: str) -> str:
    """ Returns a fully qualified path to the model output root directory.
    The directory is created if it does not exist.
    """
    # just in case we're on windows.
    temp.replace("\\", "\\\\")

    retval = path.realpath(path.join(*path.split(path.expanduser(temp))))
    if path.isfile(retval):
        retval = path.dirname(retval)
    # if the output path exists and is empty, make it the output root and return it.
    if path.exists(retval) and not os.listdir(retval):
        __touch(path.join(retval, runtime_consts.ModelDirectoryLabelName))
        return retval
    # if it exists and has stuff in it, make a subdirectory in it, make IT the root, and return it.
    elif path.exists(retval) and os.listdir(retval):
        if path.basename(retval) != runtime_consts.DefaultModelOutputDirectoryRoot:
            retval = path.join(retval, runtime_consts.DefaultModelOutputDirectoryRoot)
        if not path.exists(retval):
            os.makedirs(retval, exist_ok=True)
        __touch(path.join(retval, runtime_consts.ModelDirectoryLabelName))
        return retval
    # if it doesn't exist, make it, make it the root, and return it.
    elif not path.exists(retval):
        os.makedirs(retval)
        __touch(path.join(retval, runtime_consts.ModelDirectoryLabelName))
        return retval


if __name__ == "__main__":
    sys.exit(main())
