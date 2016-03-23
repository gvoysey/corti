from numpy import *


def anf_model(ihcout, cf, fs, ftype):
    size = len(cf)
    # Pmax=0.6
    if (ftype == 'high'):
        spont = 60.0

    elif (ftype == 'medium'):
        spont = 10.0
    else:
        spont = 1.0

    tdres = 1.0 / fs
    # fth and srth change the relative threshholds of spontaneous rate fibers.  "always 40dB above SR fibers"
    FTH = 50e-6
    # SRTH = FTH + 2e-3
    # per goldie, induces 20dB threshold difference between low/high SR fibers for pure tone threshold at 1kHz.
    SRTH = FTH + (0.2e-3) * 4
    Vsatmax = 1e-3
    spont = spont / (1 - 0.75e-3 * spont) * ones(
        size)  # to compensate fot the division at the end of the processing chain
    Ass = 150. + (cf / 100.0)   # Only frequency dependence here, comes from Liberman1978 */

    TauR = 2e-3   # Rapid Time Constant eq.10 */
    TauST = 60e-3   # Short Time Constant eq.10 */
    Ar_Ast = spont   # Ratio of Ar/Ast, free parameter */

    PTS = 1 + (6 * spont / (6 + spont)) 

    AR = (Ar_Ast / (1 + Ar_Ast)) * (PTS * Ass - Ass) 
    AST = (1 / (1 + Ar_Ast)) * (PTS * Ass - Ass) 
    PI1 = spont * (PTS * Ass - spont) / (PTS * Ass * (1 - spont / Ass)) 
    PI2 = (PTS * Ass - spont) / (1 - spont / Ass)   # from original Westerman
    CG = 1 

    gamma1 = CG / spont 
    gamma2 = CG / Ass 
    k1 = -1 / TauR 
    k2 = -1 / TauST 

    VI0 = (1 - ((PTS * Ass) / spont)) * 1 / (
    gamma1 * ((AR * (k1 - k2) / (CG * PI2)) + (k2 / (PI1 * gamma1)) - (k2 / (PI2 * gamma2)))) 
    VI1 = (1 - ((PTS * Ass) / spont)) * 1 / (
    gamma1 * ((AST * (k2 - k1) / (CG * PI2)) + (k1 / (PI1 * gamma1)) - (k1 / (PI2 * gamma2)))) 
    VI = (VI0 + VI1) / 2 

    alpha = (CG * TauR * TauST) / Ass 
    beta = (1 / TauST + 1 / TauR) * alpha 
    theta1 = (alpha * PI2) / VI 
    theta2 = VI / PI2 
    theta3 = 1 / Ass - 1 / PI2 

    PL = (((beta - theta2 * theta3) / theta1) - 1) * PI2 
    PG = 1 / (theta3 - 1 / PL) 
    VL = theta1 * PL * PG 
    CI = spont / PI1 
    CL = CI * (PI1 + PL) / PL 

    Asusmax = PL * PG * CG / (PL + PG) 
    Asus = (AR + AST) / (PTS - 1) 
    Asus = (AR + AST) / (PTS - 1.0) 
    anfout = zeros_like(ihcout)
    for i in range(len(ihcout[:, 1])):
        PPI = ((PI2 - PI1) / (Vsatmax)) * (ihcout[i, :] - (SRTH / exp(spont))) + PI1 
        PPI_rest_indx = where((ihcout[i, :] < (FTH + (SRTH / exp(spont)))))
        # PPI[(ihcout[i,:]<(FTH+(SRTH/exp(spont))))]=PI1[0] #equivalente to below but vectorized
        PPI[PPI_rest_indx] = PI1[PPI_rest_indx]  # equivalente to below but vectorized

        # if(ihcout[i]<=FTH+(SRTH/exp(spont))):
        #  PPI=PI1  #if below threshold, at PI2rest, so that firing is constant at SR */
        if (i == 0):
            PPI[:] = PI1 
        CIlast = CI 
        CI = CI + (tdres / VI) * (-PPI * CI + PL * (CL - CI)) 
        CL = CL + (tdres / VL) * (-PL * (CL - CIlast) + PG * (CG - CL)) 
        # if(CI<0) #comes from Westerman and smith neg values */
        temp = 1 / PG + 1 / PL + 1 / PPI 
        CI_n = where(CI < 0)
        # CI[CI<0] = CG/(PPI[CI<0]*temp[CI<0]) 
        CI[CI_n] = CG / (PPI[CI_n] * temp[CI_n]) 

        CL[CI_n] = CI[CI_n] * (PPI[CI_n] + PL[CI_n]) / PL[CI_n] 
        anfout[i, :] = PPI * CI
    return anfout
