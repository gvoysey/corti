import logging
import multiprocessing as mp
from datetime import datetime, timedelta

import yaml
from os import path
from verhulst_model_core.ANF_Sarah import *
from verhulst_model_core.Sarah_ihc import *
from verhulst_model_core.cochlear_model_old import *

from verhulst_runner.base import runtime_consts, periph_consts as p
from verhulst_runner.periphery_configuration import PeripheryConfiguration, PeripheryOutput


class RunPeriphery:
    """ A front-end for running the verhulst periphery model
    """
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
        self.sheraPo = np.loadtxt(polesPath)
        self.irregularities = self.conf.irregularities
        self.irr_on = self.conf.irregularities

        self.output_folder = path.join(self.conf.dataFolder,
                                       datetime.now().strftime(runtime_consts.ResultDirectoryNameFormat))
        if not path.isdir(self.output_folder):
            os.makedirs(self.output_folder)
        self.cochlear_list = [[CochleaModel(), self.stimulus[i], self.irr_on[i], i, (0, i + 1)] for i in
                              range(self.channels)]

    def run(self) -> [PeripheryOutput]:
        """Simulate sound propagation up to the auditory nerve for many stimulus levels
        :return: A list of output data, one for each stimulus level
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
        out.output = {
            p.BMVelocity: coch.Vsolution,
            p.BMDisplacement: coch.Ysolution,
            p.OtoacousticEmission: coch.oto_emission,
            p.CenterFrequency: coch.cf,
            p.InnerHairCell: rp,
            p.AuditoryNerveFiberLowSpont: anfL,
            p.AuditoryNerveFiberMediumSpont: anfM,
            p.AuditoryNerveFiberHighSpont: anfH,
            p.Stimulus: self.conf.stimulus[ii],
            p.StimulusLevel: self.conf.stimulusLevels[ii]
        }
        out.conf = self.conf
        out.stimulusLevel = self.conf.stimulusLevels[ii]
        out.outputFolder = self.output_folder

        self.save_model_results(ii, out.output)
        return out

    def save_model_results(self, ii: int, periph: {}) -> None:
        """ store the parts of the periphery output specified in storeflag.
        """
        if not self.storeFlag:
            return
        tm = lambda x: (x, periph[x])
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
        tosave = {key: value for key, value in saveMap.items() if key in self.storeFlag}
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
