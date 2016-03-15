"""
Verhulst Model.

Usage: verhulst_model

Options:
    -h --help:  Show this screen
    --version:  Display the version and exit
"""
import logging
import subprocess
import sys

from docopt import docopt

from brainstem import NelsonCarney04
from run_periphery import RunPeriphery


def main():
    try:
        label = subprocess.check_output(["git", "describe"])
    except subprocess.CalledProcessError:
        label = "unknown"
        logging.log(logging.ERROR, "version broken until i write setup.py")
    args = docopt(__doc__, version=label.decode("utf-8"))

    # todo : extract output folder, other operational shit to this class, not run_periphery.   Redo NPZ saving so it sucks less.

    anResults = RunPeriphery().run()
    brainResults = []
    for result in anResults:
        brainResults.append(NelsonCarney04(result).run())

    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main())
