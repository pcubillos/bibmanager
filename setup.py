# Copyright (c) 2018-2019 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import setuptools
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

import bibmanager as bibm
from bibmanager.utils import ignored


class Init_Bibmanager_Develop(develop):
  """Script to execute after 'python setup.py develop' call."""
  def run(self):
      develop.run(self)
      with ignored(OSError):
          bibm.bib_manager.init()


class Init_Bibmanager_Install(install):
  """Script to execute after 'python setup.py install' call."""
  def run(self):
      install.run(self)
      with ignored(OSError):
          bibm.bib_manager.init()


setup(name         = "bibmanager",
      version      = bibm.__version__,
      author       = "Patricio Cubillos",
      author_email = "patricio.cubillos@oeaw.ac.at",
      url          = "https://github.com/pcubillos/bibmanager",
      packages     = setuptools.find_packages(),
      package_data = {'bibmanager':['config', 'examples/*']},
      install_requires = ['numpy>=1.15.1',
                          'requests>=2.19.1',
                          'prompt_toolkit>=2.0.7',
                          'pygments>=2.2.0',],
      cmdclass     = {'develop':Init_Bibmanager_Develop,
                      'install':Init_Bibmanager_Install},
      license      = "MIT",
      description  = "A manager of BibTeX entries for your Latex projects.",
      #scripts      = ['bibmanager/bibm.py'],
      entry_points = {"console_scripts": ['bibm = bibmanager.__main__:main']},
      )
