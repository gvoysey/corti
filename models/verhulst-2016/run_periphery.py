import scipy.io as sio
from cochlear_model_old import *
from Sarah_ihc import *
from ANF_Sarah import *
import multiprocessing as mp
import time
from os import path
import base
from periphery_configuration import PeripheryConfiguration, Constants


#
# par = sio.loadmat('input.mat')
#
# probes = np.array(par['probes']) # a string
# probe_points = probes # a string
# storeflag_in = np.array(par['storeflag'], dtype=str)
# storeFlag = storeflag_in[0] #also a string
# fs = par['Fs']
# Fs = fs[0][0] #float/int
# stim = par['stim']
# channels = par['channels']
# channels = channels[0][0]
# subjectNo = int(par['subject'])
# sectionsNo = int(par['sectionsNo'])
# t_f = (par['data_folder'])
# output_folder = str(t_f[0])
# lgt = len(stim[0])
# sheraPo = par['sheraPo']
# if (max(shape(sheraPo)) == 1):
#     sheraPo = sheraPo[0][0]
# else:
#     sheraPo = sheraPo[:, 0]
# IrrPct = par['IrrPct']
# IrrPct = IrrPct[0][0]
# nl = np.array(par['non_linear_type'])
# # print(IrrPct)
# # print(sheraPo)
# irr_on = np.array(par['irregularities'])
# d = len(stim[0].transpose())
# print("running cochlear simulation")
# sig = stim
#
# cochlear_list = [[CochleaModel(), sig[i], irr_on[0][i], i] for i in range(channels)]
#

# sheraPo = np.loadtxt('StartingPoles.dat', delimiter=',')
# print(sheraPo)

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
        self.sheraPo = np.fromfile(self.conf.polePath)
        self.irregularities = self.conf.irregularities
        self.irr_on = self.conf.irregularities

        self.cochlear_list = [[CochleaModel(), self.stimulus[i], self.irr_on[i], i] for i in range(self.channels)]

    def run(self):
        s1 = time.clock()
        p = mp.Pool(mp.cpu_count(), maxtasksperchild=1)
        p.map(self.solve_one_cochlea,self.cochlear_list)
        p.close()
        p.join()
        print("cochlear simulation: done")

    def solve_one_cochlea(self,model: CochleaModel):
        ii = model[3]
        coch = model[0]
        stimulus = model[1]
        coch.init_model(stimulus, self.Fs, self.sectionsNo, self.probes, Zweig_irregularities=model[2], sheraPo=self.sheraPo,
                        subject=self.subject, IrrPct=self.irrPct, non_linearity_type=self.nonlinearType)  # model needs to be init here because if not pool.map crash
        #    coch.init_model(model[1],Fs,sectionsNo,probe_points,Zweig_irregularities=model[2],sheraPo=sheraPo,subject=subjectNo,non_linearity_type=nl) #model needs to be init here because if not pool.map crash
        fs = self.Fs
        coch.solve()
        rp = ihc(coch.Vsolution, fs)
        anfH = anf_model(rp, coch.cf, fs, 'high')
        anfM = anf_model(rp, coch.cf, fs, 'medium')
        anfL = anf_model(rp, coch.cf, fs, 'low')
        storeFlag = self.storeFlag
        output_folder = path.join(base.rootPath, self.conf.dataFolder)  # maybe unnecessary
        if 'v' in storeFlag:
            f = open(output_folder + "v" + str(ii + 1) + ".np", 'w')
            coch.Vsolution.tofile(f)
            f.close()
        if 'y' in storeFlag:
            f = open(output_folder + "y" + str(ii + 1) + ".np", 'w')
            coch.Ysolution.tofile(f)
            f.close()
        f = open(output_folder + "cf" + str(ii + 1) + ".np", 'w')
        coch.cf.tofile(f)
        f.close()
        if 'e' in storeFlag:
            f = open(output_folder + "emission" + str(ii + 1) + ".np", 'w')
            coch.oto_emission.tofile(f)
            f.close()
        if 'h' in storeFlag:
            f = open(output_folder + "anfH" + str(ii + 1) + ".np", 'w')
            anfH.tofile(f)
            f.close()
        if 'm' in storeFlag:
            f = open(output_folder + "anfM" + str(ii + 1) + ".np", 'w')
            anfM.tofile(f)
            f.close()
        if 'l' in storeFlag:
            f = open(output_folder + "anfL" + str(ii + 1) + ".np", 'w')
            anfL.tofile(f)
            f.close()
        if 'i' in storeFlag:
            f = open(output_folder + "ihc" + str(ii + 1) + ".np", 'w')
            rp.tofile(f)
            f.close()


if __name__ == "__main__":
    # todo: pass in yaml here in a more sane way?
    yamlPath = path.join(base.rootPath, Constants.DefaultYamlName)
    if path.isfile(yamlPath):
        RunPeriphery(yamlPath).run()
    else:
        RunPeriphery().run()
