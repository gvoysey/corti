import math

import numpy as np
from os import path
from scipy.io import wavfile


class Stimulus:
    FS = 100e3  # todo this is a magic number...
    P0 = 2e-5  # 20 micropascals

    def __init__(self, prestimulus_time: float = None, stimulus_time: float = None, poststimulus_time: float = None):
        self.poststimulus_time = poststimulus_time
        self.stimulus_time = stimulus_time
        self.prestimulus_time = prestimulus_time

    def _to_pascals(self, waveform: np.ndarray, level: float) -> np.ndarray:
        """ Rescales a given waveform so that the values are in units of pascals.
        :parameter waveform:  The waveform.
        :parameter level:     The desired resulting intensity, in dB re 20 uPa.
        """
        normalized = waveform / max(waveform)
        scaling = 2 * math.sqrt(2) * self.P0 * 10 ** (level / 20)
        return normalized * scaling

    def make_click(self, level: float) -> np.ndarray:
        template = [np.zeros(self.prestimulus_time), np.ones(self.stimulus_time), np.zeros(self.poststimulus_time)]
        return self._to_pascals(template, level)

    def make_chirp(self, level: float) -> np.ndarray:
        pass

    def make_am(self, level: float) -> np.ndarray:
        pass

    def default_stimulus(self):
        pass

    def generate_stimulus(self, stim_type: str, level: float) -> np.ndarray:
        stimului = {
            "click": self.make_click(level),
            "chirp": self.make_chirp(level),
            "am": self.make_am(level)
        }
        if stim_type in stimului:
            return stimului[stim_type]

    def load_stimulus(self, wav_path: str, level: float) -> np.ndarray:
        """ Loads and returns the specified wav file, resampled with a hamming window to a sample rate useable by
        the Verhulst model of the auditory periphery.
        """
        if not path.isfile(wav_path):
            raise FileNotFoundError
        fs, data = wavfile.read(wav_path)
        if fs != self.FS:
            raise NotImplementedError("Wav files must be sampled at {0}".format(self.FS))
        else:
            return self._to_pascals(data, level)
