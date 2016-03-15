"""
Verulst Model.

Usage: verhulst_model

Options:
    -h --help:  Show this screen
    --version:  Display the version and exit
"""
import sys
from docopt import docopt
import subprocess

def main():
    label = subprocess.check_output(["git", "describe"])
    args = docopt(__doc__, version=)


if __name__ == "__file__":
    sys.exit(main())