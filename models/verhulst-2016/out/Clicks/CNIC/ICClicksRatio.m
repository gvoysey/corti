
close all
clear all

%this is the Nelson and Carney CN and IC model:
%
%Nelson, P. C. and Carney, L.H. (2004) A phenomenological model of peripheral and central neural responses
%to amplitude-modulated tones." The Journal of the Acoustical Society of America 116, no. 4 (2004): 2173-2186.
%
%as implemented and scaled using the parameters in Verhulst et al.,2015
%
%Verhulst S, Bharadwaj H, Mehraei G, Shera CA, Shinn-Cunningham, BG. (2015). Functional modeling of the 
% human auditory brainstem response to broadband stimulation. 
% Journal of the Acoustical Society of America 138 (3): 1637-1659.


%the scaling factors
M1=0.15e-6./2.7676e+07; %last value is uncompensated at 100 dB
M3=(1.5*0.15e-6)/0.0036; %idem with scaling W1
M5=(2*0.15e-6)/0.0033; %idem with scaling W1&3

TF=19; %total no of fibers on each IHC
HSnormal=13;
MSnormal=3;
LSnormal=3;

L=[60 80];
FS=100000;


eval(['load(''../NHClicks.mat'')']);
for r=1:numel(L);
display(['Level ',num2str(L(r))]);

ANHS=out(r).anfH(:,1:2:end);
ANMS=out(r).anfM(:,1:2:end);
ANLS=out(r).anfL(:,1:2:end);

Acn=1.5;
Aic=1;
Scn=0.6;
Sic=1.5;
Dcn=1e-3;
Dic=2e-3;
Tex=0.5e-3;
Tin=2e-3;
t=[0:size(ANHS,1)-1]/FS';

Inhcn=[zeros(1,round(Dcn*FS))  Scn*(1/Tin^2)*(t).*exp(-(t)/Tin)];
Inhcn(end-round(Dcn*FS)+1:end)=[];

Inhic=[zeros(1,round(Dic*FS))  Sic*(1/Tin^2)*(t).*exp(-(t)/Tin)];
Inhic(end-round(Dic*FS)+1:end)=[];


IC=0; W1=0; CN=0; %set the vectors to 0!!
AN=repmat(LSnormal*ones(1,500),size(ANLS,1),1).*ANLS...
     +repmat(MSnormal*ones(1,500),size(ANMS,1),1).*ANMS...
         +repmat(HSnormal*ones(1,500),size(ANHS,1),1).*ANHS;

%scaling    
AN=AN*M1;    
   for n=1:500 
        Rcn=Acn*(conv((1/Tex^2)*t.*exp(-t/Tex),AN(:,n))-conv(Inhcn,circshift(AN(:,n),round(Dcn*FS))));
        Rcn=Rcn*M3;
        Ric=Aic*(conv((1/Tex^2)*t.*exp(-t/Tex),Rcn)-conv(Inhic,circshift(Rcn,round(Dic*FS))));
        Ric=Ric*M5;
        %% here only summed until 175Hz
        %population responses
        if n<=433 %the summed response for the case
            W1=W1+AN(1:size(AN,1),n); %add them up one by one
            CN=CN+Rcn(1:size(AN,1)); %add them up one by one
            IC=IC+Ric(1:size(AN,1)); %add them up one by one
        end
        RanF(n,:)=AN(:,n);
        RicF(n,:)=Ric(1:size(AN,1));
        RcnF(n,:)=Rcn(1:size(AN,1));
   end

   save(['L',num2str(L(r)),'waves.mat'],'IC','CN','W1')
   save(['L',num2str(L(r)),'SUresp.mat'],'RicF','RcnF','RanF')
end


