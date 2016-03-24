import os
from collections import namedtuple

OperationalConstants = namedtuple("OperationalConstants", "PolesDirectoryName PolesFileName TridiagName")
core_const = OperationalConstants(PolesDirectoryName="sysfiles",
                                  PolesFileName="StartingPoles.dat",
                                  TridiagName="tridiag.so"
                                  )

core_root = os.path.dirname(os.path.abspath(__file__))
polesPath = os.path.join(core_root, core_const.PolesDirectoryName, core_const.PolesFileName)
