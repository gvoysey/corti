function clicklevelexp(sID,modality,runs,TDT,trl,blockint)
%sID= subject ID which would 'ABR#'
%modality='ABR'
%runs=10 
%TDT=1
%trl=1
%blockint is the block at which you want to start at so the default=1



%
%
% Input:
% sID = subject ID number(within the group)
% modality = recording mode (e.g.'Demo','BEH')
% TDT = if TDT is used to generate sound
%runs=total number of blocks in the batch -BEH=8 and Demo=4
%trl=number of trials in each block-> BEH=50 and Demo-12

%blockint= the block at which you would like to start the experiment


%

global file_ID;         % string for file tag
global TDTon;           % if TDT is used
global Noise_Amp;       % background noise level
global IAC;             % interaural correlation of the background noise
global ABR;
global FS;



%Noise_Amp =1;

%10^(-50/20)*1.15; % This represents 25dB Tokens-to-noise ratio (with 1.15 being a factor to adjust the token window in RMS calculation)
IAC = -1;



ABR= strcmp (modality,'ABR');

TDTon = TDT;




if nargin < 3
    desiredRuns = [];
    TDTon = 0;
end

% Must be one of the predefined modalities.
if ~(ABR)
    fprintf('Currently defined modalities are: ABR \n');
    return
end



file_ID = strcat('Sub',num2str(sID),'_ABR');


% Use optseq to define block of runs
paradigm_optseq(modality);

% Start runs
StimPresent(modality, runs,trl,sID,blockint);


end % of Test
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function  paradigm_optseq(modality)


global TDTon;
global Noise_Amp;
global IAC;
global f1;
global RP;
global FS;
global ABR;


ABR = strcmp(modality,'ABR');
% Hide Cursor
%HideCursor;

if TDTon
    % Perform basic initialization of the TDT
    FS_tag=3;
    fig_num=99;
    USB_ch=1;
    %display ('BLOOP')
    [f1,RP,FS]=load_play_circuit(FS_tag,fig_num,USB_ch);
else
    % Perform basic initialization of the sound driver
    InitializePsychSound;
end

end % of paradigm_optseq

%#######################################################################%

function StimPresent(modality, runs,trl,sID,blockint)

%global w;           % Window Pointer defined by OpenWindow in PTB
global file_ID;     % string for file tag
global TDTon;
global f1;
global RP;
global FS;
global ABR;
global Noise_Amp;
global IAC;

batchfile=[file_ID '-clickbatch.mat'];
cd OAE/
mkdir (file_ID);
cd ..

%batchfile='ABR01-clickbatch.mat';
FS=48828.125;

conditions=load(batchfile);
conditions=conditions.conditions;
starteeg=253;
stop=254;
Lcal=71.3316; %calibrated level of click with amplitude  close to 1 
LNcal=80.3209; %calibrated level of noise with a rms of 1


% start of blocks
for k=blockint:runs
       WaitKeyInputs();
        invoke (RP,'SetTagVal','trgname',starteeg);  %eeg to start
        invoke (RP,'SoftTrg',6);
        WaitSecs (15e-3);
    cndblock=[];
    
   
    condtyp=conditions(k,1); %noise+click block or isolated click
    cndblock=conditions(k,2);% level of either the sound or noise
    %earp=conditions(ind,3); % which ear to present to
 %condtyp=1;
 %cndblock=70;
    if condtyp==1
        
        %for j=1:trl
        %wavedata(1:2,1:6)=0; %initializing sound channels
        %add 90 db click alone condition
        switch cndblock
            case 50 %changed from 40 db
                
                stimTrigger = 1;
                Lstim=50;
                %need to change click level here
            case 60
                stimTrigger = 2;
                Lstim=60;
            case 70
                stimTrigger = 3;
                Lstim=70;
            case 80
                stimTrigger = 4;
                Lstim=80;
            case 90
                stimTrigger = 5;
                Lstim=90;
                
            otherwise
                fprintf(2,'No such Level');
        end
        for z=1:6 %gives total 3000 clicks
            %create click train of 500 clicks
            stimulus=[0];
            for d=1:500
                dur=(randi([90 110]))./1000;
                num_samplesforclick=floor(FS*80e-6); %duration of click about 80 microseconds
                num_samplesp=floor(FS*dur);
                stimp=[];
                stimp(1:num_samplesp)=0;
                stim=[];
                stim(1:num_samplesforclick)=0.95;
                %stim(1)=1;
                stimulus=[stimulus,stim,stimp];
                StimGain=sqrt(2)*(10^((Lstim-Lcal)/20))/(0.95); %Gain value calibrated
            end
            stimulus(2,:)=0;
           % stimulus=fliplr(stimulus')'; %present in right ear. 
            %assigning Stimulus gain of the clicks
            invoke(RP, 'SetTagVal', 'clickatten',StimGain);
            
            wavedata=stimulus;
            flname=[file_ID,'_cndt' num2str(condtyp) '_lvl' num2str(cndblock) '_blk' num2str(z) '.mat'];
            
            playsnd(stimTrigger,wavedata,TDTon,flname);
            
            
            WaitSecs (100e-3); %200 ms pause between subsection so of the block
      

        end
        
    elseif condtyp==2
        
        
        switch cndblock %determine the level of the noise
            case 42
                stimTrigger = 6;
                LNStim=42;
                
            case 52
                stimTrigger = 7;
                LNStim=52;
            case 62
                stimTrigger = 8;
                LNStim=62;
            case 72
                stimTrigger = 9;
                LNStim=72;
            case 82
                stimTrigger=10;
                LNStim=82;
                
            otherwise
                fprintf(2,'No such Level');
        end
        
        %%%%%%%%%%%%%%%%
        %change noise levels to 82, 72, 62,52,42,32(?) -- maybe drop 32
        %out to have another click alone condition
        %click level to be 80 dbSPL if i hear the click add 1 or 2 db in
        %the noise
        %%%%%%%%%%%%%%%%%%
        Noise_Amp=(10^((LNStim-LNcal)/20)); %calibrated amplitude of the noise
        %Noise_Amp=1;
        % Start the noise
        if invoke(RP,'GetStatus')==7  % RP2 circuit status success
            % Set the level of the backgound noise
            invoke(RP, 'SetTagVal', 'noiselev',Noise_Amp);
            invoke(RP, 'SetTagVal', 'phase', IAC);
            
            
            
            
           
           
            % num_samplesp=floor(FS*20); %duration of click about 80 microseconds
            %num_samplesp=floor(FS*dur);
            %          stimTrigger=1;
            %      stim(1:num_samplesp)=0;
            %      stim(2,:)=0;
            %      wavedata=stim;
            %playsnd(stimTrigger,wavedata,TDTon);
        else
            error('RP2 circuit status failure')
        end
        
        
        
        
        for z=1:6 %gives total 3000 clicks
            %create click train of 1500 clicks
            %Noise_Amp=(10^((LNStim-LNcal)/20));
            stimulus=[0];
            for d=1:500
                dur=(randi([90 110]))./1000;
                num_samplesforclick=floor(FS*80e-6); %duration of click about 80 microseconds
                num_samplesp=floor(FS*dur);
                stimp=[];
                stimp(1:num_samplesp)=0;
                stim=[];
                stim(1:num_samplesforclick)=0.95;
                %stim(1)=1;
                stimulus=[stimulus,stim,stimp];
            end
            StimGain=sqrt(2)*(10^((80-Lcal)/20))/(0.95); %Gain value of click
            stimulus(2,:)=0;
            %stimulus=fliplr(stimulus')'; %present i right ear
            invoke(RP, 'SetTagVal', 'clickatten',StimGain);
             
            
            wavedata=stimulus;
            flname=[file_ID,'_cndt' num2str(condtyp) '_lvl' num2str(cndblock) '_blk' num2str(z) '.mat'];
            
            invoke(RP, 'SoftTrg', 3); %Playback noise trigger
             WaitSecs(50e-3); %wait before starting clicks
            
            playsnd(stimTrigger,wavedata,TDTon,flname);
            
            
            WaitSecs (100e-3); %200 ms pause between subsection so of the block
        
        end
        
       %WaitSecs (50e-3); %delay before stopping the noise
        
        %Backgound noise is turned off
        invoke(RP, 'SoftTrg', 4); %Stop noise trigger

    end
invoke (RP,'SetTagVal','trgname',stop);  %eeg to stop
invoke (RP,'SoftTrg',6);
WaitSecs (15e-3);     
    
end % of run loops




if TDTon
    close_play_circuit(f1,RP);
end



sca;
ShowCursor;
ListenChar(0);


end % of StimPresent




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%              SUB SUB FUNCTIONS:                                      %
%              playsnd,SetShapeRect, RenderTrialFrame, RenderShape,            %
%              WaitKeyInputs, KeyPressedCorrect, KbOSXNum              %
%              load_play_circuit, sound_sys3, close_play_circuit       %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function playsnd(stimTrigger,wavedata,TDTon,flname)
global RP;
global file_ID;
%dur=(randi([90 110]))./1000;
if TDTon
    
    %
    %Load the 2ch variable 'x' into the RP2:
    invoke(RP, 'WriteTagVEX', 'datain', 0, 'I16', (wavedata*2^15));
    invoke (RP,'SetTagVal','trgname',stimTrigger);
    %Set the delay of the sound
    invoke(RP, 'SetTagVal', 'onsetdel',0); % onset delay is in ms
    %Start playing from the buffer:
    
    
    invoke(RP, 'SoftTrg', 1); %Playback trigger
    
    
    curindex=invoke(RP, 'GetTagVal', 'indexin');
    while(curindex<length(wavedata))
        curindex=invoke(RP, 'GetTagVal', 'indexin');
    end
    invoke(RP, 'SoftTrg', 2); %Stop trigger
    OAE=invoke(RP, 'ReadTagVex', 'dataout', 0, curindex,'F32','F64',1);
    if max(max(abs(OAE)))>2^31/0.96542
        disp('Clipping!!!')
    end
    pth=['OAE/' file_ID];
    cd (pth)
    
    save(flname,'OAE')
    
    cd ../..
    
    
    
else
    % Open the default audio device [], with default mode [] (==Only playback),
    % and a required latencyclass of zero 0 == no low-latency mode
    pause(600e-3);
    pahandle = PsychPortAudio('Open', [], [], 0, freq, nrchannels);
    % Fill the audio playback buffer with the audio data
    PsychPortAudio('FillBuffer', pahandle, wavedata);
    % Start playing the audio
    AudioOnsetTime = PsychPortAudio('Start',pahandle,1,CueOnsetTime);
end



invoke(RP, 'SoftTrg', 5); %Reset Trigger

%WaitSecs(dur);
%invoke(RP, 'SoftTrg', 2); %Stop trigger
% Reset the play index to zero:
%Clearing I/O memory buffers:

invoke(RP, 'SoftTrg', 8); %Reset Trigger
invoke(RP,'ZeroTag','datain');
end

function WaitKeyInputs
if ~IsOSX
    KbWait([], 3);
else
    key_expect = [];
    KeyPressedCorrect(key_expect);
end
end % of WaitKeyInputs
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function KeyPressedCorrect(key_expect)
keyIsDown = 0;
correct_key = false;
loop = ~(keyIsDown && correct_key);
while loop
    [keyIsDown,secs,keyCode] = KbCheck;
    key_pressed = find(keyCode==1);
    if isempty(key_expect)
        correct_key = 1;
    else
        if ~isempty(key_pressed)
            correct_key = (key_pressed == key_expect);
        else
            correct_key = 0;
        end
    end
    loop = ~(keyIsDown && correct_key);
end
end % of KeyPressedCorrect
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function KeyPressed = KbOSXNum(cc)
KeyPressed = NaN;
if cc >= 30 && cc < 40
    KeyPressed = cc - 29;
end
end % of KbOSXNum
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [f1,RP,FS]=load_play_circuit(FS_tag,fig_num,USB_ch,Noise_Amp,IAC,RespTime)

CIR_PATH='ABR_EEG.rcx'; %The *.rco circuit used to play the files

%Generate the actx control window in a specified figure:
%-------------------------------------------------------
f1=figure(fig_num);
set(f1,'Position',[5 5 30 30],'Visible','off'); %places and hides the ActX Window
RP=actxcontrol('RPco.x',[5 5 30 30],f1); %loads the actx control for using rco circuits
invoke(RP,'ConnectRP2','USB',USB_ch); % opens the RP2 device *** CHANGED 'USB' to 'GB' TMS 6/2005 ***
% (the USB channel may change for other computer configurations)

% The rco circuit can be run at the following set of discrete sampling
% frequencies (in Hz): 0=6k, 1=12k, 2=25k, 3=50k, 4=100k, 5=200k.
% Use the tags listed above to specify below:
%--------------------------------------------------------------------------
invoke(RP,'LoadCOFsf',CIR_PATH,FS_tag); %loads the circuit using the specified sampling freq.
FS_vec=[6 12 25 50 100 200]*1e3;
FS=FS_vec(FS_tag+1);

invoke(RP,'Run'); %start running the circuit

Status = double(invoke(RP,'GetStatus'));
if bitget(double(Status),1)==0
    error('Error connecting to RP2');
elseif bitget(double(Status),2)==0
    error('Error loading circuit');
elseif bitget(double(Status),3)==0
    error('Error running circuit');
end


end % of load_play_circuit
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function close_play_circuit(f1,RP)

%At the end of an experiment, the circuit is removed
invoke(RP,'ClearCOF'); %clear the circuit from the RP2
close(f1); %close the ActX control window
end % of close_play_circuit
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%