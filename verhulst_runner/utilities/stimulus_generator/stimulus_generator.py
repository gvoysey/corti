"""
Stimulus Generator.  This tool generates stimuli of different shapes to use as inputs to auditory models.

Usage:
    stimulus_generator -h | --help
    stimulus_generator --version
    stimulus_generator  [-v | --verbose] [--out <outpath>] (--type (click|chirp|am) | --from-wav <wavfile>) --level <soundlevel>

Options:
    -h --help               Show this screen and exit.
    --version               Display the version and exit.
    --out=<outpath>         Specify the output location for saved data. [default: ~/stimulus-output]
    -v --verbose            Display detailed debug log output to STDOUT.
    --type                  Type of stimulus to generate.
    --level=<soundlevel>    Peak stimulus intensity, in dB SPL
    --from-wav=<wavfile>    Load a custom stimulus from the supplied path.
"""

import sys
from logging import basicConfig, INFO, ERROR, getLogger

import numpy as np
import os
from docopt import docopt
from os import path
from scipy.io import wavfile

from . import __version__

# By default, log INFO and up.
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)

FS = 100e3  # todo this is a magic number...


def _return_stimulus(stimulus: np.ndarray, level: float):
    """ Prints the generated stimulus and its sound level to STDOUT
    """
    np.savetxt(sys.stdout.buffer, [stimulus, level])


def load_stimulus(wav_path: str) -> np.ndarray:
    """ Loads and returns the specified wav file, resampled with a hamming window to a sample rate useable by
    the Verhulst model of the auditory periphery.
    """
    if not path.isfile(wav_path):
        raise FileNotFoundError
    fs, data = wavfile.read(wav_path)
    if fs != FS:
        raise NotImplementedError("Wav files need to be sampled at {0}".format(FS))
    else:
        return data
        # duration = len(data) / fs
        # len_at_FS = round(duration * FS)
        # return signal.resample(_zero_pad(data), len_at_FS, 'blackman')


#
# def _zero_pad(wav: np.ndarray) -> np.ndarray:
#     n = wav.shape[0]
#     y = np.floor(np.log2(n))
#     nextpow2 = np.power(2, y + 1)
#     return np.pad(wav, (0, int(nextpow2 - n)), mode='constant')


def generate_stimulus(stim_type: str, level: float) -> np.ndarray:
    pass


def main():
    # get the command line args
    args = docopt(__doc__, version=__version__)

    # configure the log level appropriately
    if not args["--verbose"]:
        getLogger().setLevel(ERROR)

    # barf if the level isn't a float
    level = args["--level"]
    try:
        level = float(level)
    except ValueError:
        print("Level must be a number.")
        exit(1)

    stim_type = args["--type"]
    if stim_type:
        stimulus = generate_stimulus(stim_type, level)
    else:
        stimulus = load_stimulus(args["--from-wav"])

    out = args["--out"]
    if out:
        _save_stimulus(stimulus, stim_type, level, _set_output_dir(out))
    else:
        _return_stimulus(stimulus, level)

    sys.exit(0)


def _set_output_dir(temp: str) -> str:
    """ Returns a fully qualified path to output root directory.
    The directory is created if it does not exist.
    """
    # just in case we're on windows.
    temp.replace("\\", "\\\\")

    retval = path.realpath(path.join(*path.split(path.expanduser(temp))))
    if path.isfile(retval):
        retval = path.dirname(retval)
    # if the output path exists and is empty, make it the output root and return it.
    if path.exists(retval):
        return retval
    # if it doesn't exist, make it, make it the root, and return it.
    elif not path.exists(retval):
        os.makedirs(retval)
        return retval


def _save_stimulus(stimulus: np.ndarray, stim_type: str, level: float, outPath: str):
    outName = stim_type + str(level) + "dB"
    np.savez(path.join(_set_output_dir(outPath), outName), {"stimulus": stimulus, "level": level})


if __name__ == "__main__":
    sys.exit(main())
