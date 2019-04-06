.. bibmanager documentation master file, created by
   sphinx-quickstart on Thu Jan  3 08:27:43 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

bibmanager
==========

**The Next Standard in BibTeX Management**

|Build Status|  |PyPI|   |License|  |DOI|

-------------------------------------------------------------------


:Author:       Patricio Cubillos and contributors (see :ref:`team`)
:Contact:      `patricio.cubillos[at]oeaw.ac.at`_
:Organizations: `Space Research Institute (IWF)`_
:Web Site:     https://github.com/pcubillos/bibmanager
:Date:         |today|

Features
========

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

.. _team:

Contributors
============

- `Patricio Cubillos`_ (IWF) `patricio.cubillos[at]oeaw.ac.at`_


Documentation
=============

.. toctree::
   :maxdepth: 2

   getstarted
   bibtex
   latex
   ads
   faq
   api
   contributing
   license

.. * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`

Be Kind
=======

If ``bibmanager`` was useful for your research, please be kind and
acknowledge the effort of the developers of this project.  Here's a BibTeX
entry for that:

.. code-block:: bibtex

  @misc{Cubillos2019bibmanager,
    author = {Cubillos, Patricio E.},
    title  = {bibmanager: A {BibTeX} manager for {LaTeX} projects},
    month  = jan,
    year   = 2019,
    doi    = {10.5281/zenodo.2547043},
    url    = {https://doi.org/10.5281/zenodo.2547043}
  }

Please send any feedback or inquiries to:

  Patricio Cubillos (`patricio.cubillos[at]oeaw.ac.at`_)

.. _Patricio Cubillos: https://github.com/pcubillos/
.. _patricio.cubillos[at]oeaw.ac.at: patricio.cubillos@oeaw.ac.at
.. _Space Research Institute (IWF): http://iwf.oeaw.ac.at/

.. |Build Status| image:: https://travis-ci.com/pcubillos/bibmanager.svg?branch=master
   :target: https://travis-ci.com/pcubillos/bibmanager

.. |PyPI| image:: https://img.shields.io/pypi/v/bibmanager.svg
    :target:      https://pypi.org/project/bibmanager/
    :alt: Latest Version

.. |License| image:: https://img.shields.io/github/license/pcubillos/bibmanager.svg?color=blue
    :target: https://pcubillos.github.io/bibmanager/license.html

.. |DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.2547043.svg
    :target: https://doi.org/10.5281/zenodo.2547043

