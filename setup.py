# Copyright (c) 2018-2020 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

from datetime import date

long_description = f"""

.. image:: https://raw.githubusercontent.com/pcubillos/bibmanager/master/docs/logo_bibmanager.png
   :width: 60%

|Build Status|  |docs|  |PyPI|  |License|  |DOI|

``bibmanager`` is a command-line based application to facilitate the management of BibTeX entries, allowing the user to:

* Unify all BibTeX entries into a single database
* Automate .bib file generation when compiling a LaTeX project
* Automate duplicate detection and updates from arXiv to peer-reviewed
* Clean up (remove duplicates, ADS update) any external bibfile (since version 1.1.2)
* Keep a database of the entries' PDFs and fetch PDFs from ADS (since version 1.2)

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
* Fetch PDF files from ADS (via their bibcode, new since version 1.2)

:copyright: Copyright 2018-{date.today().year} Patricio Cubillos.
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

import bibmanager as bibm
from bibmanager.utils import ignored


setup(name         = "bibmanager",
      version      = bibm.__version__,
      author       = "Patricio Cubillos",
      author_email = "patricio.cubillos@oeaw.ac.at",
      url          = "https://github.com/pcubillos/bibmanager",
      packages     = setuptools.find_packages(),
      package_data = {'bibmanager':['config', 'examples/*']},
      install_requires = ['numpy>=1.15.1',
                          'requests>=2.19.1',
                          'packaging>=17.1',
                          'prompt_toolkit>=2.0.7',
                          'pygments>=2.2.0',],
      tests_require = ['requests-mock',],
      license      = "MIT",
      description  = "A BibTeX manager for LaTeX projects",
      long_description = long_description,
      long_description_content_type="text/x-rst",
      entry_points = {"console_scripts": ['bibm = bibmanager.__main__:main']},
      )
