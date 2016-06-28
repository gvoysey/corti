function [stim,indcl]=clickstimuliwithnoise(Fs,stimdb,noiselevel,rt)
%Fs=100e3;
stimulus=[0];
stimdur=150e-3;
stimulus=zeros(round(stimdur*Fs),1);
stimulus=stimulus';
p0=20e-6;
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

noise=randn([1,length(stimulus)]);
noise(1:round(50e-3*Fs))=0;
noise=[noise,zeros(round(50e-3*Fs),1)'];
noise=noise./rms(noise);
pinnoise = 20e-6*10^(noiselevel/20)*noise;
stimulus=[stimulus,zeros(round(50e-3*Fs),1)'];
pinclick = sqrt(2)*20e-6*10^(stimdb/20)*stimulus; % unramped stimulus



channels = numel(stimdb);

stim=pinclick+pinnoise;
filename = ['clicktrain-with-noise-',num2str(noiselevel),'dbSNR-',num2str(rt),'reprate.wav'];
wavwrite(stim, Fs, 32, filename);
%parameters for model 
subject=1;
irregularities=ones(1,channels);
data_folder=strcat(pwd(),'/');
sheraPo=0.0610;
data_folder=strcat(pwd(),'/');
probes = 'all';
storeflag='vahml';
sectionsNo=1000;
spl=stimdb;

%save (['inputclick_',num2str(noiselevel),'noise.mat'],'Fs','channels','stim','subject','irregularities','probes','sheraPo','indcl','spl','storeflag','sectionsNo','data_folder');

            %StimGain=sqrt(2)*(10^((80-Lcal)/20))/(0.95); %Gain value of click
            %stimulus(2,:)=0;