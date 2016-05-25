# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 10:16:27 2016

@author: Gerard
"""

# Import modules
import numpy as np
import matplotlib.pyplot as plt
#from matplotlib import cm
# import seaborn as sns
from tkinter import filedialog, Tk
from os import listdir, sep
from os.path import isfile, join
#from mpl_toolkits.axes_grid1 import make_axes_locatable
from math import ceil
from scipy import signal

# Get files to load from model path directory
tk_win = Tk()
tk_win.withdraw()
path_mdl_out = filedialog.askdirectory(**{'initialdir':
                                          '/Volumes/EXT_DISK/encina/2_data_for_scripts/1_modeling/2_model-verhulst-abr/verhulst-output'})
tk_win.destroy()

files_in_dir_list = [f for f in listdir(path_mdl_out) if
                     isfile(join(path_mdl_out, f)) and f.endswith('.npz')]


fs = 100000

idx_fc = 468
fm = 93
fc = 2000

# Cut final vectors to remove onsets and offsets
t_cut_ini = 45e-3
t_cut_end = 25e-3
dur = 300e-3
sampl_cut_ini = int(t_cut_ini * fs)

dur_cut = dur - t_cut_ini - t_cut_end

cycles_in_tvect = np.trunc(dur_cut * fm)
cycles_samp_cut = int(np.trunc(cycles_in_tvect * fs / fm))

# Distribution of different kind of SR fibers (Number of fibers per IHC)
ls_normal = 3
ms_normal = 3
hs_normal = 13

M1_weight_fact = 0.15e-6 / 2.7676e+07


# Loop over files to extract the steady-state part

for idx_files in range(0, len(files_in_dir_list)):

    # Load data from npz files
    periph_xx = np.load(path_mdl_out + sep + files_in_dir_list[idx_files])
    periph_xx_bm = periph_xx['bm_velocity']
    periph_xx_ihc = periph_xx['ihc']
    periph_xx_an_high = periph_xx['an_high_spont']
    periph_xx_an_med = periph_xx['an_medium_spont']
    periph_xx_an_low = periph_xx['an_low_spont']

    periph_xx_an_all = (periph_xx_an_high +
                        periph_xx_an_med + periph_xx_an_low)

    # Result vectors summed across frequency
    periph_xx_an_all_sum = np.sum(periph_xx_an_all[
                                  sampl_cut_ini:sampl_cut_ini + cycles_samp_cut, :], axis=1)  # All fibers
    periph_xx_an_high_sum = np.sum(periph_xx_an_high[
                                   sampl_cut_ini:sampl_cut_ini + cycles_samp_cut, :], axis=1)  # High-SR
    periph_xx_an_med_sum = np.sum(periph_xx_an_med[
                                  sampl_cut_ini:sampl_cut_ini + cycles_samp_cut, :], axis=1)  # Med-SR
    periph_xx_an_low_sum = np.sum(periph_xx_an_low[
                                  sampl_cut_ini:sampl_cut_ini + cycles_samp_cut, :], axis=1)  # Low-SR

    # Result vectors at fc=2000
    periph_xx_an_all_fc = periph_xx_an_all[
        sampl_cut_ini:sampl_cut_ini + cycles_samp_cut, idx_fc]  # All fibers
    periph_xx_an_high_fc = periph_xx_an_high[
        sampl_cut_ini:sampl_cut_ini + cycles_samp_cut, idx_fc]  # High-SR
    periph_xx_an_med_fc = periph_xx_an_med[
        sampl_cut_ini:sampl_cut_ini + cycles_samp_cut, idx_fc]  # Med-SR
    periph_xx_an_low_fc = periph_xx_an_low[
        sampl_cut_ini:sampl_cut_ini + cycles_samp_cut, idx_fc]  # Low-SR

    l = len(periph_xx_an_all_sum)
    nfft = l

    # Bin where fm is
    fm_fft_bin = int(np.round((fm * nfft / fs)))

    periph_xx_an_all_sum_fft = np.fft.fft(periph_xx_an_all_sum, nfft) / (l / 2)
    periph_xx_an_all_sum_magn = 20 * \
        np.log10(np.abs(periph_xx_an_all_sum_fft[fm_fft_bin]))
