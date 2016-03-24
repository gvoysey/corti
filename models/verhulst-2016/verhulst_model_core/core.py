import os
from collections import namedtuple

OperationalConstants = namedtuple("OperationalConstants", "PolesDirectoryName PolesFileName TridiagName")
core_const = OperationalConstants(PolesDirectoryName="sysfiles",
                                  PolesFileName="StartingPoles.dat",
                                  TridiagName="tridiag.so"
                                  )

rootPath = os.path.dirname(os.path.abspath(__file__))
polesPath = os.path.join(rootPath, core_const.PolesDirectoryName, core_const.PolesFileName)
