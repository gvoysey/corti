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
import logging
import multiprocessing as mp
import subprocess
import sys
import warnings
from os import path, getcwd, system, name

from docopt import docopt

from brainstem import NelsonCarney04, BrainstemOutput
from periphery_configuration import PeripheryConfiguration, PeripheryOutput
from run_periphery import RunPeriphery

warnings.simplefilter(action="ignore", category=FutureWarning)
logging.basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=logging.INFO)


class BrainstemRunner:
    @staticmethod
    def solve_one(periphery: PeripheryOutput) -> BrainstemOutput:
        return NelsonCarney04(periphery).run()


def main():
    try:
        label = subprocess.check_output(["git", "describe"])
    except subprocess.CalledProcessError:
        label = "unknown"
        logging.log(logging.ERROR, "version broken until i write setup.py")
    # get the command line args
    args = docopt(__doc__, version="verhulst_model version " + label.decode("utf-8"))
    # configure the log level appropriately
    if not args["--verbose"]:
        logging.getLogger().setLevel(logging.ERROR)

    system('cls' if name == 'nt' else 'clear')
    print("Simulating periphery and auditory nerve ...")
    conf = PeripheryConfiguration(__get_output_path(args["--out"]), args["--pSave"], args["--clean"])
    anResults = RunPeriphery(conf).run()
    print("Simulating brainstem response")
    brainResults = __simulate_brainstem(anResults)
    print("Finshed.")
    sys.exit(0)


def __simulate_brainstem(anResults: [PeripheryOutput]) -> [BrainstemOutput]:
    p = mp.Pool(mp.cpu_count(), maxtasksperchild=1)
    retval = p.map(BrainstemRunner.solve_one, anResults)
    p.close()
    p.join()
    return retval


def __get_output_path(temp: str) -> str:
    """ Return the fully qualified path to store model output.
    """
    if temp == "~/verhulst-output":  # ugh, string comparisons.
        return path.expanduser(temp)
    if path.isabs(temp):
        return temp
    else:
        return path.join(getcwd(), temp)


if __name__ == "__main__":
    sys.exit(main())
