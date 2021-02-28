# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import re
import setuptools
from datetime import date
from setuptools import setup


long_description = f"""

.. image:: https://raw.githubusercontent.com/pcubillos/bibmanager/master/docs/logo_bibmanager.png
   :width: 60%

|Build Status|  |docs|  |PyPI|  |conda|  |License|  |DOI|

``bibmanager`` is a command-line based application to facilitate the management of BibTeX entries, allowing the user to:

* Unify all BibTeX entries into a single database
* Automate .bib file generation when compiling a LaTeX project
* Automate duplicate detection and updates from arXiv to peer-reviewed
* Clean up (remove duplicates, ADS update) any external bibfile (since version 1.1.2)
* Keep a database of the entries' PDFs and fetch PDFs from ADS (since version 1.2)
* Browse interactively through the database (since version 1.3)

``bibmanager`` also simplifies many other BibTeX-related tasks:

* Add or modify entries into the ``bibmanager`` database:

  * Merging user's .bib files
  * Manually adding or editing entries
  * Add entries from ADS bibcodes

* entry adding via your default text editor
* Query entries in the ``bibmanager`` database by author, year, or title keywords
* Generate .bib files built from your .tex files
* Compile LaTeX projects with the ``latex`` or ``pdflatex`` directives
* Perform queries into ADS and add entries by bibcode
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
    :target: https://pypi.org/project/bibmanager/

.. |conda| image:: https://img.shields.io/conda/vn/conda-forge/bibmanager.svg
    :target: https://anaconda.org/conda-forge/bibmanager

.. |License| image:: https://img.shields.io/github/license/pcubillos/bibmanager.svg?color=blue
    :target: https://bibmanager.readthedocs.io/en/latest/license.html

.. |DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.2547042.svg
    :target: https://doi.org/10.5281/zenodo.2547042

"""

def get_version(package):
    """Return package version as listed in __version__ in VERSION.py"""
    path = os.path.join(os.path.dirname(__file__), package, "VERSION.py")
    with open(path, "rb") as f:
        init_py = f.read().decode("utf-8")
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name = "bibmanager",
    version = get_version("bibmanager"),
    author = "Patricio Cubillos",
    author_email = "patricio.cubillos@oeaw.ac.at",
    url = "https://github.com/pcubillos/bibmanager",
    packages = setuptools.find_packages(),
    package_data = {'bibmanager':['config', 'examples/*']},
    install_requires = [
        'numpy>=1.15.1',
        'requests>=2.19.1',
        'packaging>=17.1',
        'prompt_toolkit>=3.0.5',
        'pygments>=2.2.0',
    ],
    tests_require = [
        'requests-mock',
        'prompt_toolkit>=3.0.10',
    ],
    license = "MIT",
    description = "A BibTeX manager for LaTeX projects",
    long_description = long_description,
    long_description_content_type="text/x-rst",
    entry_points = {"console_scripts": ['bibm = bibmanager.__main__:main']},
    )
