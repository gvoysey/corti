import logging
from datetime import datetime, timedelta
from os import path

import yaml
from verhulst_model_core.ANF_Sarah import *
from verhulst_model_core.Sarah_ihc import *
from verhulst_model_core.cochlear_model_old import *

from verhulst_runner.base import runtime_consts, periph_consts as p, PeripheryType
from verhulst_runner.periphery_configuration import PeripheryConfiguration, PeripheryOutput
from verhulst_runner.zilany2014 import run_zilany2014


class Periphery:
    """ A front-end for running the verhulst periphery model
    """

    def __init__(self, conf: PeripheryConfiguration):
        self.conf = conf
        if self.conf.modelType == PeripheryType.verhulst:
            self.probes = self.conf.probeString
            self.irregularities = self.conf.irregularities
            self.irr_on = self.conf.irregularities
            self.random_seed = self.conf.random_seed
            self.irrPct = self.conf.irrPct
            self.nonlinearType = self.conf.nonlinearType
            self.sheraPo = np.loadtxt(polesPath)
            self.cochlear_list = [[CochleaModel(), self.stimulus[i], self.irr_on[i], i, (0, i + 1)] for i in
                                  range(len(self.stimulus))]
            self.sectionsNo = self.conf.NumberOfSections

        self.storeFlag = self.conf.storeFlag
        self.stimulus = self.conf.stimulus
        self.Fs = self.conf.Fs
        self.output_folder = path.join(self.conf.dataFolder,
                                       datetime.now().strftime(runtime_consts.ResultDirectoryNameFormat))
        if not path.isdir(self.output_folder):
            os.makedirs(self.output_folder)

    def run(self) -> [PeripheryOutput]:
        """Simulate sound propagation up to the auditory nerve for many stimulus levels
        :return: A list of output data, one for each stimulus level
        """
        s1 = datetime.now()
        # results = Parallel(n_jobs=-1)(delayed(self.solve_one_cochlea)(xx) for xx in self.cochlear_list)
        results = []
        if self.conf.modelType == PeripheryType.verhulst:
            for i, v in enumerate(self.cochlear_list):
                results.append(self.solve_one_cochlea(v))
                self.save_model_results(i, results[i].output)
        elif self.conf.modelType == PeripheryType.zilany:
            for i, v in enumerate(self.conf.stimulus):
                results.append(run_zilany2014(sound=v,
                                              fs=self.conf.Fs,
                                              anf_num=(1, 1, 1),
                                              species="human",
                                              seed=0,
                                              conf=self.conf,
                                              output=self.output_folder,
                                              level=self.conf.stimulusLevels[i],
                                              cf=(125, 20e3, 1e3)))
                self.save_model_results(i, results[i].output)

        else:
            raise NotImplementedError("Peripheral model '{0}' was not recognized".format(self.conf.modelType))

        self.save_model_configuration()
        print("\tPeripheral simulation of {} stimulus levels finished in {:0.3f}sec".format(len(self.stimulus),
                                                                                            timedelta.total_seconds(
                                                                                                datetime.now() - s1)))
        return results

    def solve_one_cochlea(self, model: []) -> PeripheryOutput:
        """Compute unweighted periphery and AN output for one stimulus level
        :return: a periphery output container
        """
        ii = model[3]
        coch = model[0]
        stimulus = model[1]
        coch.init_model(stimulus,
                        self.Fs,
                        self.sectionsNo,
                        self.probes,
                        Zweig_irregularities=model[2],
                        sheraPo=self.sheraPo,
                        subject=self.random_seed,
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
        out.output = {
            p.BMVelocity                   : coch.Vsolution,
            p.BMDisplacement               : coch.Ysolution,
            p.OtoacousticEmission          : coch.oto_emission,
            p.CenterFrequency              : coch.cf,
            p.InnerHairCell                : rp,
            p.AuditoryNerveFiberLowSpont   : anfL,
            p.AuditoryNerveFiberMediumSpont: anfM,
            p.AuditoryNerveFiberHighSpont  : anfH,
            p.Stimulus                     : stimulus,
            p.StimulusLevel                : self.conf.stimulusLevels[ii]
        }
        out.conf = self.conf
        out.stimulusLevel = self.conf.stimulusLevels[ii]
        out.outputFolder = self.output_folder

        return out

    def save_model_results(self, ii: int, periph: {}) -> None:
        """ store the parts of the periphery output specified in storeflag.
        """
        if not self.storeFlag:
            return
        tm = lambda x: (x, periph[x] if x in periph else None)
        # saveMap makes a dict of tuples. the key is the storeFlag character,
        # [0] is the key that will be used in the npz file,
        # [1] is the value saved to that key.
        # todo add handing for "a" here.
        saveMap = {
            'v': tm(p.BMVelocity),
            'y': tm(p.BMDisplacement),
            'c': tm(p.CenterFrequency),
            'e': tm(p.OtoacousticEmission),
            'h': tm(p.AuditoryNerveFiberHighSpont),
            'm': tm(p.AuditoryNerveFiberMediumSpont),
            'l': tm(p.AuditoryNerveFiberLowSpont),
            'i': tm(p.InnerHairCell),
            's': tm(p.Stimulus),
            'd': tm(p.StimulusLevel)
        }
        # {k:v for k,v in bar.items() if k in foo}
        # walk through the map and save the stuff we said we should.
        tosave = {key: value for key, value in saveMap.items() if key in self.storeFlag and value[1] is not None}
        if not tosave:
            return
        outfile = runtime_consts.PeripheryOutputFilePrefix + str(self.conf.stimulusLevels[ii]) + "dB"
        np.savez(path.join(self.output_folder, outfile), **{name: data for name, data in tosave.values()})
        logging.info("wrote {0} to {1}".format(outfile, path.relpath(self.output_folder, os.getcwd())))

    def save_model_configuration(self) -> None:
        # and store the configuration parameters so we know what we did.
        with open(path.join(self.output_folder, runtime_consts.PeripheryConfigurationName), "w") as _:
            yaml.dump(self.conf, _)
            logging.info("wrote {} to {}".format(runtime_consts.PeripheryConfigurationName,
                                                 path.relpath(self.output_folder, os.getcwd())))
