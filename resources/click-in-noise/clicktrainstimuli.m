function [stimulus,indcl]=clicktrainstimuli(Fs,spl,rt)
Fs=100e3;
stimulus=[0];
stimdur=50e-3;
stimulus=zeros(round(stimdur*Fs),1);
stimulus=stimulus';
for d=1:10
    dur= (1/rt);           
    %dur=(randi([90 210]))./1000;
                %dur=500./1000;
                num_samplesforclick=floor(Fs*80e-6); %duration of click about 80 microseconds
                num_samplesp=floor(Fs*dur);
                stimp=[];
                stimp(1:num_samplesp)=0;
                stimt=[];
                stimt(1:num_samplesforclick)=1;
                %stim(1)=1;
                stimulus=[stimulus,stimt,stimp];
end
            
%% find onset of each click
indcl=[];
ind=find(stimulus==max(stimulus));
for i=1:length(ind)
    if (stimulus(ind(i)-1)==0)
        indcl=[indcl;ind(i)];
    end
    
    
end




channels = numel(spl);
for k = 1:channels
    
    Amp=p0*10^(spl(k)/20);
     stim(k,:)=Amp*sqrt(2)*stimulus; 
end

normalizeRMS=zeros(1,channels);
subject=1;
irregularities=ones(1,channels);

sheraPo=0.0610;
probes = 'all';

save (['inputclick_train10Hz_60dB'],'Fs','channels','stim','normalizeRMS','subject','irregularities','probes','sheraPo','indcl','spl');

            %StimGain=sqrt(2)*(10^((80-Lcal)/20))/(0.95); %Gain value of click
            %stimulus(2,:)=0;