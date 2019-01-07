# Copyright (c) 2018-2019 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
from . import VERSION as ver
from .bib_manager import *

from .bib_manager import __all__ as bm_all

__all__ = bm_all

__version__ = "{:d}.{:d}.{:d}".format(ver.BM_VER, ver.BM_MIN, ver.BM_REV)

# Clean up top-level namespace--delete everything that isn't in __all__
# or is a magic attribute, and that isn't a submodule of this package
for varname in dir():
    if not ((varname.startswith('__') and varname.endswith('__')) or
            varname in __all__ ):
        del locals()[varname]
del(varname)
