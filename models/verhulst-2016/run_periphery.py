import multiprocessing as mp
from datetime import datetime
from os import path, makedirs
import jsonpickle
import base
from ANF_Sarah import *
from Sarah_ihc import *
from cochlear_model_old import *
from periphery_configuration import PeripheryConfiguration, Constants


class RunPeriphery:
    def __init__(self, yamlPath=None):
        if yamlPath is not None:
            self.conf = PeripheryConfiguration(yamlPath)
        else:
            self.conf = PeripheryConfiguration()

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
        self.output_folder = path.join(base.rootPath, self.conf.dataFolder, datetime.now().strftime('%d %b %y %H %M'))
        if not path.isdir(self.output_folder):
            os.makedirs(self.output_folder)
        self.cochlear_list = [[CochleaModel(), self.stimulus[i], self.irr_on[i], i] for i in range(self.channels)]

    def run(self):
        s1 = time.clock()
        p = mp.Pool(mp.cpu_count(), maxtasksperchild=1)
        p.map(self.solve_one_cochlea, self.cochlear_list)
        p.close()
        p.join()
        print("cochlear simulation: done")

    def solve_one_cochlea(self, model: CochleaModel):

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
        fs = self.Fs
        coch.solve()
        rp = ihc(coch.Vsolution, fs)
        anfH = anf_model(rp, coch.cf, fs, 'high')
        anfM = anf_model(rp, coch.cf, fs, 'medium')
        anfL = anf_model(rp, coch.cf, fs, 'low')
        storeFlag = self.storeFlag

        # let's store every run along with a serialized snapshot of its parameters in its own directory.
        output_folder = self.output_folder
        partial = str(ii + 1) + ".np"
        saveMap = [('v', 'v' + partial, coch.Vsolution.tofile),
                   ('y', 'y' + partial, coch.Ysolution.tofile),
                   ('cf', 'cf' + partial, coch.cf.tofile),
                   ('e', 'emission' + partial, coch.oto_emission.tofile),
                   ('h', 'anfH' + partial, anfH.tofile),
                   ('m', 'anfM' + partial, anfM.tofile),
                   ('l', 'anfL' + partial, anfL.tofile),
                   ('i', 'ihc' + partial, rp.tofile)]
        storeFlag += "cf"  # always store CFs

        for thisFlag in saveMap:
            if thisFlag[0] in storeFlag:
                with open(path.join(output_folder, thisFlag[1]), "w") as _:
                    thisFlag[2](_)
        # and store the configuration parameters so we know what we did.
        with open(path.join(output_folder, "configuration.pickle"), "w") as _:
            # jsonpickle.dumps(self.conf, _)


if __name__ == "__main__":
    # todo: pass in yaml here in a more sane way?
    yamlPath = path.join(base.rootPath, Constants.DefaultYamlName)
    if path.isfile(yamlPath):
        RunPeriphery(yamlPath).run()
    else:
        RunPeriphery().run()
