from numpy import *

# define global constants
Mvel = 41e-6
Mu = 200e-9
Fcut = 1000.0
Fgain = Mu / Mvel
F_LPC = 1000.0
gain = 1.0


def ihc(input1, fs):
    """Compute IHC voltages
    :parameter input1: the BM Velocity solution (?)
    :parameter fs: the sampling frequency
    """
    dim_in = shape(input1)
    size = (dim_in[1])
    FS = fs
    LPk = 2  # order of the lowpass filter
    C = 2.0 * FS
    C1LP = (C - (2 * pi * F_LPC)) / (C + (2 * pi * F_LPC))
    C2LP = (2 * pi * F_LPC) / ((2 * pi * F_LPC) + C)
    yc = zeros(size)
    past_input1 = zeros(size)
    past_output1 = zeros(size)
    past_output2 = zeros(size)
    v = zeros(size)  # v stands for voltage
    VihcNF = zeros(size)
    A0 = 0.008  # %0.1 scalar in IHC nonlinear function
    B = 2000 * 6000  # 2000 par in IHC nonlinear function
    C = 0.33 # 1.74 par in IHC nonlinear function
    D = 200e-9
    ihcout = zeros_like(input1)
    for i in range(dim_in[0]):
        yc = array(Fgain * input1[i, :])
        yc_negative = where(yc < 0)
        yc_positive = where(yc > 0)
        #     VihcNF[yc>0]=A0*log(1+B*abs(yc[yc>0]));
        # VihcNF[yc<0]=-A0*(((abs(yc[yc<0])**C)+D)/((3*abs(yc[yc<0])**C)+D))*log(1+B*abs(yc[yc<0]));
        VihcNF[yc_positive] = A0 * log(1 + B * abs(yc[yc_positive]))
        VihcNF[yc_negative] = -A0 * (((abs(yc[yc_negative]) ** C) + D) / ((3 * abs(yc[yc_negative]) ** C) + D)) * log(1 + B * abs(yc[yc_negative]))

        #    #cascade of iir filters vectorized (all sections at once)
        y1 = C1LP * past_output1 + C2LP * (VihcNF + past_input1)  # intermediate output of the iir cascade
        v = C1LP * past_output2 + C2LP * (y1 + past_output1)
        #    # update filters' past values
        past_input1 = VihcNF
        past_output1 = y1
        #    #the output is store on the v variable
        past_output2 = v
        ihcout[i, :] = v
    return ihcout
