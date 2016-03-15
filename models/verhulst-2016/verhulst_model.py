"""
Verhulst Model.

Usage:
    verhulst_model -h | --help
    verhulst_model --version
    verhulst_model --out <outpath>
    verhulst_model [--out <outpath>]  [-c | --clean]  [-v | --verbose]
    verhulst_model --clean | -c
    verhulst_model --verbose | -v

Options:
    -h --help   Show this screen and exit.
    --version   Display the version and exit.
    --out=<outpath>     Specify the output location for saved data. [default: verhulst-output]
    -c --clean  Previous runs will be deleted to save disk space.
    -v --verbose    Display detailed debug log output to STDOUT.
"""
import logging
import subprocess
import sys
import warnings

from docopt import docopt

from brainstem import NelsonCarney04
from run_periphery import RunPeriphery

warnings.simplefilter(action="ignore", category=FutureWarning)
logging.basicConfig(format='%(levelname)s %(asctime)s-%(message)s', datefmt='%d %b %H:%M:%S', level=logging.INFO)


def main():
    try:
        label = subprocess.check_output(["git", "describe"])
    except subprocess.CalledProcessError:
        label = "unknown"
        logging.log(logging.ERROR, "version broken until i write setup.py")
    args = docopt(__doc__, version="verhulst_model version " + label.decode("utf-8"))

    if not args["--verbose"]:
        logging.getLogger().setLevel(logging.CRITICAL)

    # todo : extract output folder, other operational shit to this class, not run_periphery.

    anResults = RunPeriphery().run()
    brainResults = []
    for result in anResults:
        brainResults.append(NelsonCarney04(result).run())

    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main())
