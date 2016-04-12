# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile

#Stimulus parameters

fs = 100000
amp = 0.1
fc = 2005
fm = 93
m = np.array([85, 25])/100
dur = 300e-3
dur_ramp = 5e-3

#Stimulus generation

t_vect = np.arange(0, dur, 1/fs)

sam_25 = amp*( ( 1 + m[1]*np.sin(2*np.pi*fm*t_vect) )/2 ) * np.sin(2*np.pi*fc*t_vect)
sam_85 = amp*( ( 1 + m[0]*np.sin(2*np.pi*fm*t_vect) )/2 ) * np.sin(2*np.pi*fc*t_vect)

#Add ramps

ramp_samples = dur_ramp*fs
stim_samples = len(t_vect)

win_bkman = np.blackman(2*ramp_samples)
win_bkman_asc   = win_bkman[:ramp_samples]
win_bkman_desc  = win_bkman[ramp_samples:]

ramp_sig = np.concatenate( (win_bkman_asc, np.ones(stim_samples - len(win_bkman)), win_bkman_desc) )

sam_25 = sam_25*ramp_sig
sam_85 = sam_85*ramp_sig

#Write the stimuli as .wav files

scipy.io.wavfile.write('stim_sam_25.wav', fs, sam_25)
scipy.io.wavfile.write('stim_sam_85.wav', fs, sam_85)