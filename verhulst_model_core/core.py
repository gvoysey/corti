import os
from collections import namedtuple

OperationalConstants = namedtuple("OperationalConstants", "ResourcesDirectory PolesFileName")
core_const = OperationalConstants(ResourcesDirectory="resources",
                                  PolesFileName="StartingPoles.dat",
                                  )

core_root = os.path.dirname(os.path.abspath(__file__))
resources_root = os.path.join(core_root, core_const.ResourcesDirectory)
polesPath = os.path.join(core_root, core_const.ResourcesDirectory, core_const.PolesFileName)
