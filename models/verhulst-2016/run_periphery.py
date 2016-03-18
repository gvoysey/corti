import logging
import multiprocessing as mp
from datetime import datetime, timedelta
from os import path

import yaml

from ANF_Sarah import *
from Sarah_ihc import *
from base import const
from cochlear_model_old import *
from periphery_configuration import PeripheryConfiguration, PeripheryOutput


class RunPeriphery:
    def __init__(self, conf: PeripheryConfiguration):
        self.conf = conf
        self.probes = self.conf.probeString
        self.storeFlag = self.conf.storeFlag
        self.stimulus = self.conf.stimulus
        self.Fs = self.conf.Fs
        self.channels = self.conf.channels
        self.sectionsNo = self.conf.NumberOfSections
        self.subject = self.conf.subject
        self.irrPct = self.conf.irrPct
        self.nonlinearType = self.conf.nonlinearType
        self.sheraPo = np.loadtxt(self.conf.polePath)
        self.irregularities = self.conf.irregularities
        self.irr_on = self.conf.irregularities

        self.output_folder = path.join(self.conf.dataFolder, datetime.now().strftime(const.ResultDirectoryNameFormat))
        if not path.isdir(self.output_folder):
            os.makedirs(self.output_folder)
        self.cochlear_list = [[CochleaModel(), self.stimulus[i], self.irr_on[i], i, (0, i + 1)] for i in
                              range(self.channels)]

    def run(self) -> [PeripheryOutput]:
        """Simulates sound propagation up to the auditory nerve.
        :return:
        """
        s1 = datetime.now()
        p = mp.Pool(mp.cpu_count(), maxtasksperchild=1)
        results = p.map(self.solve_one_cochlea, self.cochlear_list)
        p.close()
        p.join()
        self.save_model_configuration()
        print("\ncochlear simulation of {} channels finished in {:0.3f}s".format(self.channels, timedelta.total_seconds(
            datetime.now() - s1)))
        return results

    def solve_one_cochlea(self, model: []) -> PeripheryOutput:
        ii = model[3]
        coch = model[0]
        stimulus = model[1]
        coch.init_model(stimulus,
                        self.Fs,
                        self.sectionsNo,
                        self.probes,
                        Zweig_irregularities=model[2],
                        sheraPo=self.sheraPo,
                        subject=self.subject,
                        IrrPct=self.irrPct,
                        non_linearity_type=self.nonlinearType)
        # This right here is the rate limiting step.
        coch.solve(location=model[4])
        fs = self.Fs
        rp = ihc(coch.Vsolution, fs)
        anfH = anf_model(rp, coch.cf, fs, 'high')
        anfM = anf_model(rp, coch.cf, fs, 'medium')
        anfL = anf_model(rp, coch.cf, fs, 'low')
        # save intermediate results out to the output container (and possibly to disk)
        out = PeripheryOutput()
        out.bmVelocity = coch.Vsolution
        out.bmDisplacement = coch.Ysolution
        out.emission = coch.oto_emission
        out.cf = coch.cf
        out.ihc = rp
        out.anfH = anfH
        out.anfM = anfM
        out.anfL = anfL
        out.conf = self.conf
        out.stimulusLevel = self.conf.stimulusLevels[ii]
        out.outputFolder = self.output_folder

        self.save_model_results(ii, coch, anfH, anfM, anfL, rp)
        return out

    def save_model_results(self, ii: int, coch: CochleaModel, anfH: np.ndarray, anfM: np.ndarray, anfL: np.ndarray,
                           rp: np.ndarray) -> None:
        # let's store every run along with a serialized snapshot of its parameters in its own directory.
        # mf makes a fully qualified file path to the output file.
        mf = lambda x: x + str(self.conf.stimulusLevels[ii]) + 'dB'

        # saveMap makes a dict of tuples. the key is the storeFlag character, [1] is the prefix to the file name,
        # and [2] is the function that saves the data. todo add handing for "a" here.
        saveMap = {
            'v': (mf('bmvel'), coch.Vsolution),
            'y': (mf('bmpos'), coch.Ysolution),
            'c': (mf('cf'), coch.cf),
            'e': (mf('emission'), coch.oto_emission),
            'h': (mf('anfH'), anfH),
            'm': (mf('anfM'), anfM),
            'l': (mf('anfL'), anfL),
            'i': (mf('ihc'), rp),
            's': (mf('stim'), self.conf.stimulus[ii])
        }
        # walk through the map and save the stuff we said we should.
        saveDict = {}
        for flag in set(self.storeFlag):
            if flag in saveMap:
                name, value = saveMap[flag]
                saveDict[name] = value
        if saveDict:
            np.savez(path.join(self.output_folder, mf(const.PeripheryOutputFilePrefix)), **saveDict)
            logging.info("wrote {0} to {1}".format(mf(const.PeripheryOutputFilePrefix),
                                                   path.relpath(self.output_folder, os.getcwd())))

    def save_model_configuration(self) -> None:
        # and store the configuration parameters so we know what we did.
        with open(path.join(self.output_folder, "conf.yaml"), "w") as _:
            yaml.dump(self.conf, _)
            logging.info("wrote conf.yaml to {}".format(path.relpath(self.output_folder, os.getcwd())))
