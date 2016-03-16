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
    --pSave=<peripheryFlag>      Which components of the peripheral response to save.  [default: avihlmes]
    --bSave      Brainstem output will be saved if set.
    -c --clean  Previous runs will be deleted to save disk space.
    -v --verbose    Display detailed debug log output to STDOUT.
"""
import os
from logging import log, basicConfig, INFO, ERROR, getLogger
import subprocess
import sys
import warnings
from os import path, system, name

from docopt import docopt

import base
from brainstem import simulate_brainstem
from periphery_configuration import PeripheryConfiguration
from run_periphery import RunPeriphery

warnings.simplefilter(action="ignore", category=FutureWarning)
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)



def main():
    try:
        label = subprocess.check_output(["git", "describe"])
    except subprocess.CalledProcessError:
        label = "unknown"
        log(ERROR, "version broken until i write setup.py")
    # get the command line args
    args = docopt(__doc__, version="verhulst_model version " + label)

    # configure the log level appropriately
    if not args["--verbose"]:
        getLogger().setLevel(ERROR)

    system('cls' if name == 'nt' else 'clear')
    print("Simulating periphery and auditory nerve...")
    log(INFO, "output directory set to {0}".format(__get_output_path(args["--out"])))
    conf = PeripheryConfiguration(__get_output_path(args["--out"]), args["--pSave"], args["--clean"])
    anResults = RunPeriphery(conf).run()
    print("Simulating brainstem response")
    brainResults = simulate_brainstem(anResults)
    print("Finshed.")
    sys.exit(0)


def __touch(fname, times=None):
    with open(fname, 'a+'):
        os.utime(fname, times)

def __get_output_path(temp: str) -> str:
    """ Return the fully qualified path to store model output.
    """
    # just in case we're on windows.
    temp.replace("\\", "\\\\")
    if temp[0] == "~":
        retval = path.expanduser(path.join(*path.split(temp)))
    else:
        retval = path.realpath(path.join(*path.split(temp)))
    # if the output path exists and is empty, make it the output root and return it.
    if path.exists(retval) and not os.listdir(retval):
        __touch(path.join(retval,base.ModelDirectoryLabelName))
        return retval
    # if it exists and has stuff in it, make a subdirectory in it, make IT the root, and return it.
    elif path.exists(retval) and os.listdir(retval):
        retval = path.join(retval, "verhulst output")
        os.makedirs(retval)
        __touch(path.join(retval, base.ModelDirectoryLabelName))
        return retval
    # if it doesn't exist, make it, make it the root, and return it.
    elif not path.exists(retval):
        os.makedirs(retval)
        __touch(path.join(retval, base.ModelDirectoryLabelName))
        return retval

if __name__ == "__main__":
    sys.exit(main())
