import os
import sys
from setuptools import setup

topdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(topdir + "/bibmanager")
import VERSION as v

setup(name         = "bibmanager",
      version      = "{:d}.{:d}.{:d}".format(v.BM_VER, v.BM_MIN, v.BM_REV),
      author       = "Patricio Cubillos",
      author_email = "patricio.cubillos@oeaw.ac.at",
      url          = "https://github.com/pcubillos/bibmanager",
      packages     = ["bibmanager"],
      license      = "MIT",
      description  = "A manager of BibTeX entries for your Latex projects.",
      #scripts      = ['bibmanager/bibm.py'],
      entry_points = {"console_scripts": ['bibm = bibmanager.__main__:main']},
      )
