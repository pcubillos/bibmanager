# Copyright (c) 2018-2019 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

topdir = os.path.dirname(os.path.realpath(__file__))
import bibmanager as bm


class Init_Bibmanager_Develop(develop):
  """Script to execute after 'python setup.py develop' call."""
  def run(self):
      bm.init()


class Init_Bibmanager_Install(install):
  """Script to execute after 'python setup.py install' call."""
  def run(self):
      bm.init()


setup(name         = "bibmanager",
      version      = bm.__version__,
      author       = "Patricio Cubillos",
      author_email = "patricio.cubillos@oeaw.ac.at",
      url          = "https://github.com/pcubillos/bibmanager",
      packages     = ["bibmanager"],
      install_requires = ['numpy>=1.15.1',
                          'requests>=2.19.1',
                          'prompt_toolkit>=2.0.5',
                          'pygments>=2.2.0',],
      cmdclass     = {'develop':Init_Bibmanager_Develop,
                      'install':Init_Bibmanager_Install},
      license      = "MIT",
      description  = "A manager of BibTeX entries for your Latex projects.",
      #scripts      = ['bibmanager/bibm.py'],
      entry_points = {"console_scripts": ['bibm = bibmanager.__main__:main']},
      )
