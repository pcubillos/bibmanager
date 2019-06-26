# Copyright (c) 2018-2019 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

long_description = """

.. image:: https://raw.githubusercontent.com/pcubillos/bibmanager/master/docs/logo_bibmanager.png
   :width: 60%

|Build Status|  |docs|  |PyPI|  |License|  |DOI|

``bibmanager`` is a command-line based application to facilitate the management of BibTeX entries, allowing the user to:

* Unify all BibTeX entries into a single database
* Automate .bib file generation when compiling a LaTeX project
* Automate duplicate detection and updates from arXiv to peer-reviewed

``bibmanager`` also simplifies many other BibTeX-related tasks:

* Add or modify entries into the ``bibmanager`` database:

  * Merging user's .bib files
  * Manually adding or editing entries
  * Add entries from ADS bibcodes

* entry adding via your default text editor
* Querry entries in the ``bibmanager`` database by author, year, or title keywords
* Generate .bib or .bbl build from your .tex files
* Compile LaTeX projects with the ``latex`` or ``pdflatex`` directives
* Perform querries into ADS and add entries by bibcode

:copyright: Copyright 2018-2019 Patricio Cubillos.
:license:   bibmanager is open-source software under the MIT license
:URL:       https://bibmanager.readthedocs.io/

.. |Build Status| image:: https://travis-ci.com/pcubillos/bibmanager.svg?branch=master
    :target: https://travis-ci.com/pcubillos/bibmanager

.. |docs| image:: https://readthedocs.org/projects/bibmanager/badge/?version=latest
    :target: https://bibmanager.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |PyPI| image:: https://img.shields.io/pypi/v/bibmanager.svg
    :target:      https://pypi.org/project/bibmanager/

.. |License| image:: https://img.shields.io/github/license/pcubillos/bibmanager.svg?color=blue
    :target: https://pcubillos.github.io/bibmanager/license.html

.. |DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.2547042.svg
    :target: https://doi.org/10.5281/zenodo.2547042

"""

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
      tests_require = ['requests-mock',],
      cmdclass     = {'develop':Init_Bibmanager_Develop,
                      'install':Init_Bibmanager_Install},
      license      = "MIT",
      description  = "A BibTeX manager for LaTeX projects",
      long_description = long_description,
      entry_points = {"console_scripts": ['bibm = bibmanager.__main__:main']},
      )
