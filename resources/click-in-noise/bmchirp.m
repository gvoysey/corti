function sig = bmchirp(f1,f2,fs,len,flat)

%  BMCHIRP generates optimized Chirp described in Dau et al. (2000)

%

%	sig = bmchirp(f1,f2,fs,len,flat)

%	generates the ``approximated'' optimized chirp developed by Dau et al.

%	(2000). This chirp compensates for travel-time differences along the

%	cochlear partition. The equations were derived on the basis of a linear

%	cochlea model (de Boer, 1980).

%

%	A vector sig is returned. The vector is filled with zeros to match the

%	length of len. If len equals zero the minimum length for the chirp will

%	be calculated.

%

%	f1  : lower (start) frequency of the chirp (in Hz)

%	f2  : upper (stop) frequncy of the chirp (in Hz)

%	fs  : sampling frequency in Hz (standard: 25000 Hz)

%	len : length of the chirp in s (standard: 0 s)

%	flat: flat spectrum (1) or not (0) (standard: 0)

%	sig : the resulting chirp (output)

%

%	This script is based upon the article by

%	T. Dau, O. Wegner, V. Mellert and B. Kollmeier (2000): "Auditory

%	brainstem response with optimized chirp signals compensating

%	basilar-membrane dispersion." J Acoust Soc Am 107(3): 1530-1540.

%

%	Derivation of traveling wave velocity:

%	E de Boer (1980): "Auditory physics. Physical principles in hearing

%	theory I", Phys Rep (62), 87-274.

%

%	Cochlear frequency-position function:

%	DD Greenwood (1990): "A cochlear frequency-position function for

%	several species -- 29 years later", J Acoust Soc Am (87), 2592-2605.

%

% (c) O. Wegner, T. Dau 09/96

% $Revision: 1.7 $  $Date: 2001/02/19 08:18:15 $



% All numbered equations refer to the corresponding equations in the

% JASA article by Dau et al. (2000).



% check for f1 and f2

if ( nargin < 2 )

  help bmchirp

  return

end



if (f1 > f2)

  error('f1 > f2: not allowed');

end



% standard values:

len_std = 0.0;			 % standard value for len (means minimum length)

flat_std = 0;			 % standard value for flat-spectrum switch

fs_std = 25000.0;		 % standard value for fs



% check for flat

if (exist('flat') ~= 1)

  flat = flat_std;

elseif isempty(flat)

  flat = flat_std;

end



% check for len

if (exist('len') ~= 1)

  len = len_std;

elseif isempty(len)

  len = len_std;

end



% check for fs

if (exist('fs') ~= 1)

  fs = fs_std;

elseif isempty(fs)

  fs = fs_std;

end



len = ceil(len*fs);		 % len in samples (rounded towards next integer)

t0 = bmtime(0);			 % time for 0 Hz (reference)

t1 = t0 - bmtime(f1);		 % time for f1

t2 = t0 - bmtime(f2);		 % time for f2

samples = ceil((t2 - t1) * fs);	 % samples needed (rounded towards next integer)

if (len == 0) len = samples; end % len = 0 => optimal fill

if (samples > len)		 % is len long enough?

  error(sprintf('at least %f s are needed',samples/fs));

end

t = t1 : 1/fs : t2;		 % time-axis

sig = amplitude(t,flat) .* sin(instphas(t)-instphas(t1));	% generate chirp

sig = [sig zeros(1,len-length(t))];				% fill up with zeros



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function time = bmtime(f)

%BMTIME   traveling time on the basilar membrane

%

%	time = bmtime(f)

%	returns the time (in s) a pulse needs to get to the

%	position on the basilar membrane which represents the

%	frequency f (in Hz).

%

% (c) O. Wegner, T. Dau 09/96



% Constants:

% from de Boer (1980):

C0 = 10^9;				% 10^9 g s^(-2) cm^(-2) == 10^4 N cm^(-3)

h = 0.1;				% cm

rho = 1.0;				% g cm^(-3)

alpha = 3.0;				% 1/cm

% from Greenwood (1990):

a = 0.006046;				% 1/Hz

c = 1.67/log(10);			% cm

L = 3.485;				% cm



beta = 2/alpha*sqrt(2*rho/(h*C0));	% s



time = beta*((a*f+1).^-(alpha*c/2)*exp(L*alpha/2)-1);	% rf. eq. (13)



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function phi = instphas(t)

%INSTPHAS instantaneous phase

%

%	phi = instphas(t)

%	calculates the instantaneous phase at a given time t

%	(in s) for a stimulus that should compensate the

%	spatial dispersion on the basilar membrane. It is used

%	by the function bmchirp.

%

% (c) O. Wegner, T. Dau 09/96



% Constants:

%from de Boer (1980):

C0 = 10^9;		% 10^4 N cm^(-3)

h = 0.1;		% cm

rho = 1.0;		% g cm^(-3)

alpha = 3.0;		% 1/cm

% from Greenwood (1990):

a = 0.006046;				% 1/Hz

c = 1.67/log(10);			% cm

L = 3.485;				% cm

%

t0 = bmtime(0);				% time for 0 Hz (reference)

beta = 2/alpha*sqrt(2*rho/(h*C0));

gamma = -2/(alpha*c);

tau0 = t0+beta;	



phi = -2*pi/a * (t+ ( (tau0-t).^(gamma+1) - tau0^(gamma+1) ) /((beta*exp(alpha*L/2))^gamma * (gamma+1)) );





%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function amp = amplitude(t,o_flat)

% AMMPLITUD	calculates the amplitude factors

%

%	amp = amplitude(o_flat)

%	calculates the tiem dependent amplitude factors for the normal chirp

%	(o_flat = 0) or the flat-spectrum chirp (o_flat=1).

%

%	t	time axis

%	o_flat	flat-spectrum (1) or not (0)

%

% (c) O. Wegner 11/00



% Constants:

%from de Boer (1980):

C0 = 10^9;		% 10^4 N cm^(-3)

h = 0.1;		% cm

rho = 1.0;		% g cm^(-3)

alpha = 3.0;		% 1/cm

% from Greenwood (1990):

a = 0.006046;				% 1/Hz

c = 1.67/log(10);			% cm

L = 3.485;				% cm

%

t0 = bmtime(0);				% time for 0 Hz (reference)

beta = 2/alpha*sqrt(2*rho/(h*C0));

gamma = -2/(alpha*c);



if o_flat,

  amp = sqrt(1/a*( -gamma*exp(-L*alpha/2)/beta* (exp(-L*alpha/2)*(1+(t0-t)/beta)).^(gamma-1) -1));

  amp = amp / max(amp);

else

  amp = 1;

end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%

%%	Copyright (C) 1996	Torsten Dau, Oliver Wegner

%%				Carl von Ossietzky Universitaet Oldenburg

%%

%%	Permission to use, copy, and distribute this software/file and its

%%	documentation for any purpose without permission by the author

%%	is strictly forbidden.

%%

%%	Permission to modify the software is granted, but not the right to

%%	distribute the modified code.

%%

%%	This software is provided "as is" without expressed or implied warranty.

%%

%%

%%	AUTHORS

%%

%%		Torsten Dau / Oliver Wegner

%%		Carl von Ossietzky Universitaet Oldenburg

%%		Arbeitsgruppe Medizinische Physik

%%		26111 Oldenburg

%%		Germany

%%

%%		e-mail:		torsten.dau@medi.physik.uni-oldenburg.de

%%				ow@medi.physik.uni-oldenburg.de

%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

