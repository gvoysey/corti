# some really basic plotting for now

import glob
from os import path

import base
from periphery_configuration import PeripheryConfiguration


def make_plots(basePath: str):
    files = glob.glob(path.join(basePath, '*.np'), recursive=True)
    print(len(files))
    for file in files:
        print(file)


if __name__ == "__main__":
    make_plots(path.join(base.rootPath, PeripheryConfiguration.DataFolder))
