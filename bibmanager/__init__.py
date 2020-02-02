# Copyright (c) 2018-2020 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = [
    "bib_manager",
    "config_manager",
    "latex_manager",
    "ads_manager",
    "pdf_manager",
    "utils",
]

from . import bib_manager
from . import config_manager
from . import latex_manager
from . import ads_manager
from . import pdf_manager
from . import utils

from . import VERSION as ver


__version__ = f"{ver.BM_VER}.{ver.BM_MIN}.{ver.BM_REV}"

# Clean up top-level namespace--delete everything that isn't in __all__
# or is a magic attribute, and that isn't a submodule of this package
for varname in dir():
    if not ((varname.startswith('__') and varname.endswith('__')) or
            varname in __all__):
        del locals()[varname]
del(varname)
