# a (mostly)direct port of periphery.m

from periphery_output import PeripheryOutput
from typing import List


def configure_periphery(sign: List[float], fs: float, fc: List[float],  dataFolder: str, irregularities: List[float], storeFlag: str="avihlme",clean: bool=True,
                        subject: int = 1, sheraPo:float = 0.06, irrPct:float = 0.05,
                        nonlinear_type:str="vel") -> PeripheryOutput:
    # declare our magic constants
    sectionsNo = 1e3

    #set the channel count
    channels=len(sign)
    if len(irregularities) <=1:
        irregularities = [1]*channels

    # parse the storeflag string.  This looks for pre-written files on disk in the dataFolder,
    # and optionally reads them back in and makes them part of PeripheryOutput.
    for i in range(1,channels):  #todo: remember that this is one-indexed (FOR NOW)
     if(storeFlag.__contains__('a')):

