function sigout = flatspec(sigin,f1,f2,fsamp)
% flatspec returns the signal with its absolute value of the spectrum equal to 1.0
%
%	sigout = flatspec(sigin,f1,f2,fsamp)
%
%	1. zeros padding (number of samples before and after signal)
%	2. set absolute value of the spectrum to 1
%	3. butterworth bandpass filter (order=6, Zero-phase forward and reverse
%	   digital filtering)
%	4. remove the padded zeros
%
%	This function assumes real input signals!
%
%	sigin	input signal
%	f1	lower cutoff frequency
%	f2	higher cutoff frequency
%	fsamp	sampling frequency
%	sigout	output signal

% (c) 01/00 Oliver Wegner and Torsten Dau; Universitaet Oldenburg

if nargin < 3 help flatspec; return; end
if nargin < 4 fsamp = 25000; end			% default for fsamp

dim = find( max(size(sigin)) == size(sigin) );		% along which dimension
zerosize = size(sigin);					% number of zeros to pad
sigin = cat(dim,zeros(zerosize),sigin,zeros(zerosize));	% zero-padding
[vAbs,vPhs] = c2ap(fft(sigin));				% get absolute value and phase
vAbs = vAbs * 0.0 + 1.0;				% set absolute value to 1.0
sigout = real(ifft(ap2c(vAbs,vPhs)));			% build the resulting signal
							% real due to numerical errors
[B,A] = butter(5,[f1,f2]/fsamp*2);			% compute filter coefficients
sigout = filtfilt(B,A,sigout);				% filtering
sigout = sigout(max(zerosize)+1:2*max(zerosize));	% cut out the signal

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [vAbs, vPhs] = c2ap(vCmplx)
%C2AP	converts from complex to absolute value with phase
%
%usage: [vAbs,vPhs] = c2ap(vCmplx)
%		vCmplx:	vector of complex values
%		vAbs  :	vector with absolute values
%		vPhs  : vector with wrapped phases

if exist('vCmplx') ~= 1
   help c2ap
   return
end

vAbs = abs(vCmplx);
vPhs = angle(vCmplx);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function vCmplx = ap2c(vAbs, vPhs)
%AP2C	converts from absolute value with phase to complex
%
%usage: vCmplx = ap2c(vAbs,vPhs)
%		vAbs  :	vector with absolute values
%		vPhs  : vector with wrapped phases
%		vCmplx:	vector of complex values

if exist('vAbs') ~= 1 | exist('vPhs') ~= 1
   help ap2c
   return
end

vCmplx = vAbs .* ( cos(vPhs) + i*sin(vPhs) );
