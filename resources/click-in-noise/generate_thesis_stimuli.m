
%% This generates the stimuli from Section 4.1.2 of Mehraei, G. (2015). Auditory brainstem response latency in noise as a marker of cochlear synaptopathy Massachusetts Institute of Technology.
snrs = [ 42, 52, 62, 72, 82];
Fs = 100e3;
level = 80;
rt = 100;

for i = 1:length(snrs)
    clickstimuliwithnoise(Fs,level, snrs(i), rt);
end

clicktrainstimuli(Fs, level, rt);