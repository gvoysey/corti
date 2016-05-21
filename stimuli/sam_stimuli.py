"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import scipy.io.wavfile

# Stimulus parameters
fs = 100000
amp = 0.1
fc = 2000
fm = 93
m = np.array([85, 50, 25, 12])/100
dur = 0.3
dur_ramp = 1/fm

# Stimulus generation
t_vect = np.arange(0, dur, 1/fs)

tone_fc = amp * np.sin(2*np.pi*fc*t_vect)

sam_85 = amp*( ( 1 + m[0]*np.sin(2*np.pi*fm*t_vect) )/2 ) * np.sin(2*np.pi*fc*t_vect)
sam_50 = amp*( ( 1 + m[1]*np.sin(2*np.pi*fm*t_vect) )/2 ) * np.sin(2*np.pi*fc*t_vect)
sam_25 = amp*( ( 1 + m[2]*np.sin(2*np.pi*fm*t_vect) )/2 ) * np.sin(2*np.pi*fc*t_vect)
sam_12 = amp*( ( 1 + m[3]*np.sin(2*np.pi*fm*t_vect) )/2 ) * np.sin(2*np.pi*fc*t_vect)

# Add ramps
ramp_samples = int(dur_ramp*fs)
stim_samples = len(t_vect)

win_bkman = np.blackman(2*ramp_samples)
win_bkman_asc   = win_bkman[:ramp_samples]
win_bkman_desc  = win_bkman[ramp_samples:]

ramp_sig = np.concatenate( (win_bkman_asc, np.ones(stim_samples - len(win_bkman)), win_bkman_desc) )

tone_fc = tone_fc * ramp_sig
sam_85 = sam_85 * ramp_sig
sam_50 = sam_50 * ramp_sig
sam_25 = sam_25 * ramp_sig
sam_12 = sam_12 * ramp_sig


# Write the stimuli as .wav files
scipy.io.wavfile.write('stim_tone_fc.wav', fs, tone_fc)
scipy.io.wavfile.write('stim_sam_85.wav', fs, sam_85)
scipy.io.wavfile.write('stim_sam_50.wav', fs, sam_50)
scipy.io.wavfile.write('stim_sam_25.wav', fs, sam_25)
scipy.io.wavfile.write('stim_sam_12.wav', fs, sam_12)
