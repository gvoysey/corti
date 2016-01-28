close all;
clear all;

%For more info on the model implementation, and the papers to cite:

% Verhulst S, Bharadwaj H, Mehraei G, Shera CA, Shinn-Cunningham, BG. (2015). Functional modeling of the 
% human auditory brainstem response to broadband stimulation. 
% Journal of the Acoustical Society of America 138 (3): 1637-1659.
%
% Altoé A, Pulkki V, Verhulst S. (2014). Transmission-line Cochlear Models: Improved Accuracy and Efficiency. 
% Journal of the Acoustical Society of America ? 136 EL302.
%
% Verhulst S, Dau T, Shera CA. (2012). Nonlinear time-domain cochlear model 
% for transient stimulation and human otoacoustic emission. 
% Journal of the Acoustical Society of America, 132 (6), 3842-3848.


%BEFORE THIS WILL RUN YOU NEED TO COMPILE THE tridiag.so
%open a terminal: for mac
%gcc -shared -fpic -O3 -ffast-math -o tridiag.so cochlea_utils.c
%for ubuntu
%gcc tridiag.so cochlea_utils.c

%this is very complicated to compile on windows but not impossible..(good luck)


%*************************************************************************
type='NH';
name=[type,'Clicks'];

%move the correct poles to the execution folder
copyfile('./sysfiles/NHPoles/StartingPoles.dat','./sysfiles')
SheraP=load('./sysfiles/StartingPoles.dat');

% Model params
FS=100000; %should be this!! to make sure there are no NL errors in the time-domain computation
channels = 2; %stimulus blocks running in simultaneously
normalizeRMS=zeros(1,channels);
subject=1; %each subject has the same cochlear mechanics, 
%but different BM irregularities and hence reflection source OAEs
L =[60 80]; %stimulus levels in dB
irregularities=ones(1,channels); %if 1, reflections source emissions generated, if 0 then not
probes = 'all'; %can also do 'all','half' ('all= store 1000 sections',
%'half' = store 500 sections even though 1000 are simulated)
implnt=0; %implementation selection, leave this way
n=1;
p0=2e-5; 
data_folder=strcat(pwd(),'/'); %where to store

%generate the stimuli
for k=1:numel(L)
    Cdur=round(80e-6*FS);
    SC=[zeros(1,round(FS*20e-3))  ones(1,Cdur) zeros(1,round(FS*50e-3))];
    %it simulates for as long as you have a stimulus
    stim(k,:)=2*sqrt(2)*SC*p0*10.0^(L(k)/20.0);  
    %model multiplies the 1 with the factor you specify here, so any rms
    %compensation and ptp has to be accounted for here
    %if pure tone: sqrt(2)
    %if 010 click: 2*sqrt(2) to have peSPL
end


%then code in loop so there is storage when it is finished
clear ans
out=periphery(stim,FS,probes,1,data_folder,1,'vyeihlm',1,SheraP,0.05,'vel'); 
%to simulate more or less stuff: add/remove digits from the 
%'vyeihlm' section
%v=BM velocity
%y=BM displacement
%e=otoacoustic emission
%i=inner hair cell receptor potential
%l= LS fiber
%m= MS fiber
%h= HS fiber

save('output.mat','out','-v7.3')
figure,plot(out(1,1).v(:,300))
movefile('output.mat',['./out/Clicks/',name,'.mat'])