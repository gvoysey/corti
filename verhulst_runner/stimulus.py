import math
from logging import error

import numpy as np
import yaml
from os import path
from scipy.io import wavfile

from verhulst_runner.base import stimulusTemplatePath, stim_consts as sc


class Stimulus:
    FS = 100e3  # todo this is a magic number...
    P0 = 2e-5  # 20 micropascals

    def __init__(self, prestimulus_time: float = None, stimulus_time: float = None, poststimulus_time: float = None):
        self.poststimulus_time = poststimulus_time
        self.stimulus_time = stimulus_time
        self.prestimulus_time = prestimulus_time

    def seconds_to_samples(self, time: str):
        time = float(time)
        return int(round(self.FS * time))

    def _to_pascals(self, waveform: np.ndarray, levels: []) -> np.ndarray:
        """ Rescales a given waveform so that the values are in units of pascals.
        :parameter waveform:  The waveform.
        :parameter level:     The desired resulting intensity, in dB re 20 uPa.
        """
        normalized = waveform / max(waveform)
        scaling = 2 * math.sqrt(2) * self.P0 * 10 ** (levels / 20)
        return normalized * scaling

    def make_click(self, config: {}) -> np.ndarray:
        pre = self.seconds_to_samples(config[sc.PrestimTime])
        stim = self.seconds_to_samples(config[sc.StimTime])
        post = self.seconds_to_samples(config[sc.PoststimTime])
        template = np.hstack([np.zeros(pre), np.ones(stim), np.zeros(post)])
        levels = np.array(config[sc.Levels])[:, None]
        return self._to_pascals(template, levels)

    def make_chirp(self, config: {}) -> np.ndarray:
        pass

    def make_am(self, config: {}) -> np.ndarray:
        pass

    def custom_stimulus_template(self, templatePath: str):
        return yaml.load(open(templatePath, "r"))

    def default_stimulus_template(self):
        return yaml.load(open(stimulusTemplatePath, "r"))

    def generate_stimulus(self, stimulus_config: {}) -> {}:
        if sc.Stimulus in stimulus_config:
            return stimulus_config
        stim_type = stimulus_config[sc.StimulusType]

        stimului = {
            sc.Click: self.make_click(stimulus_config),
            sc.Chirp: self.make_chirp(stimulus_config),
            sc.AM: self.make_am(stimulus_config),
        }
        if stim_type in stimului:
            stimulus_config[sc.Stimulus] = stimului[stim_type]
            return stimulus_config
        else:
            error("Cannot generate stimulus, wrong parameters given.")

    def load_stimulus(self, wav_path: str, level: [float]) -> {}:
        """ Loads and returns the specified wav file.
        """
        if not path.isfile(wav_path):
            raise FileNotFoundError
        fs, data = wavfile.read(wav_path)
        if fs != self.FS:
            raise NotImplementedError("Wav files must be sampled at {0}".format(self.FS))
        else:
            return {
                sc.Levels: level,
                sc.StimulusType: "custom",
                sc.Stimulus: self._to_pascals(data, level)
            }
