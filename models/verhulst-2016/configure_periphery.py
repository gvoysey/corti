"""Configure Verhulst Model.

Usage:
    configure_periphery.py -
"""

from periphery_configuration import PeripheryConfiguration
from typing import List
from docopt import docopt

class ConfigurePeriphery :

    def __init__(self):#, sign: List[float], fs: float, fc: List[float],  dataFolder: str, irregularities: List[float], storeFlag: str="avihlme",clean: bool=True,
                      #      subject: int = 1, sheraPo:float = 0.06, irrPct:float = 0.05,
                      #     nonlinear_type:str="vel") -> PeripheryConfiguration:
        # declare our magic constants
        sectionsNo = 1e3

        #parse args
        args = docopt(__doc__)
        #set the channel count
        channels=len(sign)
        if len(irregularities) <=1:
            irregularities = [1]*channels

        # parse the storeflag string.  This looks for pre-written files on disk in the dataFolder,
        # and optionally reads them back in and makes them part of PeripheryConfiguration.
      #  for i in range(1,channels):  #todo: remember that this is one-indexed (FOR NOW)
        # if(storeFlag.__contains__('a')):

