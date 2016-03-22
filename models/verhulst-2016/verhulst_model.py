"""
Verhulst Model.

Usage:
    verhulst_model -h | --help
    verhulst_model --version
    verhulst_model [--out <outpath>]  [-c | --clean]  [-v | --verbose] [--pSave <peripheryFlag>] [--bSave]

Options:
    -h --help   Show this screen and exit.
    --version   Display the version and exit.
    --out=<outpath>     Specify the output location for saved data. [default: ~/verhulst-output]
    --pSave=<peripheryFlag>      Which components of the peripheral response to save.  [default: cavihlmes]
    --bSave      Brainstem output will be saved if set.
    -c --clean  Previous runs will be deleted to save disk space.
    -v --verbose    Display detailed debug log output to STDOUT.
"""
import os
import shutil
import subprocess
import sys
import warnings
from datetime import datetime
from logging import info, error, basicConfig, getLogger, ERROR, INFO
from os import path, system, name

from docopt import docopt

#from analysis.plots import make_summary_plots
from base import const
from brainstem import simulate_brainstem
from periphery_configuration import PeripheryConfiguration
from run_periphery import RunPeriphery

warnings.simplefilter(action="ignore", category=FutureWarning)
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)


def main():
    try:
        label = subprocess.check_output(["git", "describe"])
        label = label.decode()
    except subprocess.CalledProcessError:
        label = "unknown"
        error("version broken until i write setup.py")
    # get the command line args
    args = docopt(__doc__, version="verhulst_model version " + label)

    # configure the log level appropriately
    if not args["--verbose"]:
        getLogger().setLevel(ERROR)

    system('cls' if name == 'nt' else 'clear')
    print("Simulating periphery and auditory nerve...")
    info("output directory set to {0}".format(__set_output_dir(args["--out"])))
    conf = PeripheryConfiguration(__set_output_dir(args["--out"]), args["--pSave"])
    anResults = RunPeriphery(conf).run()
    print("Simulating brainstem response")
    brainResults = simulate_brainstem([(anr, args["--bSave"]) for anr in anResults])
    print("Generating summary figure")
    #make_summary_plots(anResults, brainResults)
    if args["--clean"]:
        print("Cleaning old model runs ... ")
        __clean(conf.dataFolder, anResults[0].outputFolder)
    print("Finshed.")
    sys.exit(0)


def __clean(rootDir: str, current_results: str) -> None:
    """
    Removes all the previous model runs except the current one found in the current base output directory
    """
    contents = os.listdir(rootDir)
    if const.ModelDirectoryLabelName not in contents:
        info("Specified directory was not a model output directory. No data removed.")
        return
    info("cleaning up...")
    for d in contents:
        if (not d == path.basename(current_results)) and \
                path.isdir(path.join(rootDir, d)) and \
                datetime.strptime(d, const.ResultDirectoryNameFormat):
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
    """ Return the fully qualified path to store model output, and creates it if it does not exist.
    """
    # just in case we're on windows.
    temp.replace("\\", "\\\\")

    retval = path.realpath(path.join(*path.split(path.expanduser(temp))))
    dirname = path.split(retval)[1]
    # if the output path exists and is empty, make it the output root and return it.
    if path.exists(retval) and not os.listdir(retval):
        __touch(path.join(retval, const.ModelDirectoryLabelName))
        return retval
    # if it exists and has stuff in it, make a subdirectory in it, make IT the root, and return it.
    elif path.exists(retval) and os.listdir(retval):
        if dirname != const.DefaultModelOutputDirectoryRoot:
            retval = path.join(retval, const.DefaultModelOutputDirectoryRoot)
        if not path.exists(retval):
            os.makedirs(retval, exist_ok=True)
        __touch(path.join(retval, const.ModelDirectoryLabelName))
        return retval
    # if it doesn't exist, make it, make it the root, and return it.
    elif not path.exists(retval):
        os.makedirs(retval)
        __touch(path.join(retval, const.ModelDirectoryLabelName))
        return retval


if __name__ == "__main__":
    sys.exit(main())
