import scipy.io as sio
from cochlear_model_old import *
from Sarah_ihc import *
from ANF_Sarah import *
import multiprocessing as mp
import time

par=sio.loadmat('input.mat')

probes=np.array(par['probes']) 
storeflag_in=np.array(par['storeflag'],dtype=str)
storeflag=storeflag_in[0]
probe_points=probes
Fs=par['Fs']
Fs=Fs[0][0]
stim=par['stim']
channels=par['channels']
channels=channels[0][0]
subjectNo=int(par['subject'])
sectionsNo=int(par['sectionsNo'])
t_f=(par['data_folder'])
output_folder=str(t_f[0])
lgt=len(stim[0])
sheraPo=par['sheraPo']
if(max(shape(sheraPo))==1):
    sheraPo=sheraPo[0][0]
else:
    sheraPo=sheraPo[:,0]    
IrrPct=par['IrrPct']
IrrPct=IrrPct[0][0]
nl=np.array(par['non_linear_type'])
#print(IrrPct)
#print(sheraPo)
irr_on=np.array(par['irregularities'])
d=len(stim[0].transpose())
print("running cochlear simulation")
sig=stim

cochlear_list=[[CochleaModel(), sig[i], irr_on[0][i], i] for i in range(channels)]
#sheraPo = np.loadtxt('StartingPoles.dat', delimiter=',')
#print(sheraPo)

def solve_one_cochlea(model): #definition here, to have all the parameter implicit
    ii=model[3]
    coch=model[0]
    sig=model[1]
    coch.init_model(model[1],Fs,sectionsNo,probe_points,Zweig_irregularities=model[2],sheraPo=sheraPo,subject=subjectNo,IrrPct=IrrPct,non_linearity_type=nl) #model needs to be init here because if not pool.map crash
#    coch.init_model(model[1],Fs,sectionsNo,probe_points,Zweig_irregularities=model[2],sheraPo=sheraPo,subject=subjectNo,non_linearity_type=nl) #model needs to be init here because if not pool.map crash

    coch.solve()
    rp=ihc(coch.Vsolution,Fs)
    anfH=anf_model(rp,coch.cf,Fs,'high')
    anfM=anf_model(rp,coch.cf,Fs,'medium')
    anfL=anf_model(rp,coch.cf,Fs,'low')

    if 'v' in storeflag:
        f=open(output_folder+"v"+str(ii+1)+".np",'w')
        coch.Vsolution.tofile(f)
        f.close()
    if 'y' in storeflag:
        f=open(output_folder+"y"+str(ii+1)+".np",'w')
        coch.Ysolution.tofile(f)
        f.close()
    f=open(output_folder+"cf"+str(ii+1)+".np",'w')
    coch.cf.tofile(f)
    f.close()
    if 'e' in storeflag:
        f=open(output_folder+"emission"+str(ii+1)+".np",'w')
        coch.oto_emission.tofile(f)
        f.close()
    if 'h' in storeflag:
        f=open(output_folder+"anfH"+str(ii+1)+".np",'w')
        anfH.tofile(f)
        f.close()
    if 'm' in storeflag:
        f=open(output_folder+"anfM"+str(ii+1)+".np",'w')
        anfM.tofile(f)
        f.close()
    if 'l' in storeflag:
        f=open(output_folder+"anfL"+str(ii+1)+".np",'w')
        anfL.tofile(f)
        f.close()
    if 'i' in storeflag:
        f=open(output_folder+"ihc"+str(ii+1)+".np",'w')
        rp.tofile(f)
        f.close()



if __name__ == "__main__":
    s1=time.clock()
    p=mp.Pool(mp.cpu_count(),maxtasksperchild=1)
    #p = mp.Pool(1, maxtasksperchild=1)
    p.map(solve_one_cochlea,cochlear_list)
    p.close()
    p.join()
    print("cochlear simulation: done")