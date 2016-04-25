function FMchirp(Fs,stimdb,noiselevel,gp)
Fs=100e3;
stimulus=[0];
dur=round(100e-3*Fs)
p0=20e-6;

gap=zeros(round(gp*Fs),1);




noise=randn([1,dur]);
noise=noise./rms(noise);

sig=bmchirp(80,20e3,Fs,12e-3,0);
fltsig=flatspec(sig,80,20e3,Fs);
pinnoise = 20e-6*10^(noiselevel/20)*noise;
pinclick = sqrt(2)*20e-6*10^(stimdb/20)*fltsig; % unramped stimulus

stim=[zeros(round(50e-3*Fs),1)', pinnoise*0, gap', pinclick,zeros(round(50e-3*Fs),1)'];

channels = numel(stimdb);




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

%save (['FM',num2str(gp*1000),'ms_70noise.mat'],'Fs','channels','stim','subject','irregularities','probes','sheraPo','spl','storeflag','sectionsNo','data_folder');
save (['FMcontrol.mat'],'Fs','channels','stim','subject','irregularities','probes','sheraPo','spl','storeflag','sectionsNo','data_folder');

%StimGain=sqrt(2)*(10^((80-Lcal)/20))/(0.95); %Gain value of click
%stimulus(2,:)=0;