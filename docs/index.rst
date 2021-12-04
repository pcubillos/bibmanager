.. bibmanager documentation master file, created by
   sphinx-quickstart on Thu Jan  3 08:27:43 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

bibmanager
==========

**The Next Standard in BibTeX Management**

|Build Status|  |docs|  |PyPI|  |conda|  |License|  |DOI|

-------------------------------------------------------------------


:Author:       Patricio Cubillos and contributors (see :ref:`team`)
:Contact:      `pcubillos[at]fulbrightmail.org`_
:Organizations: `Space Research Institute (IWF)`_
:Web Site:     https://github.com/pcubillos/bibmanager
:Date:         |today|

Features
========

``bibmanager`` is a command-line based application to facilitate the management of BibTeX entries, allowing the user to:

* Unify all BibTeX entries into a single database
* Automate .bib file generation when compiling a LaTeX project
* Automate duplicate detection and updates from arXiv to peer-reviewed
* Clean up (remove duplicates, ADS update) any external bibfile (since version 1.1.2)
* Keep a database of the entries' PDFs and fetch PDFs from ADS (since version 1.2)
* Browse interactively through the database (since version 1.3)
* Keep track of the more relevant entries using custom-set tags (since version 1.4)

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

Check out this video tutorial to get started with ``bibmanager``:

.. raw:: html

    <iframe width="720" height="405" src="https://www.youtube.com/embed/qewdBx0M8VE" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

And this one covering some other features:

.. raw:: html

    <iframe width="720" height="405" src="https://www.youtube.com/embed/WVmhdwVNXOE" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


.. _team:

Contributors
============

``bibmanager`` was created and is maintained by
`Patricio Cubillos`_ (`pcubillos[at]fulbrightmail.org`_).

These people have directly contributed to make the software better:

- `K.-Michael Aye <https://github.com/michaelaye>`_
- `Ellert van der Velden <https://github.com/1313e>`_
- `Aaron David Schneider <https://github.com/AaronDavidSchneider>`_

Documentation
=============

.. toctree::
   :maxdepth: 2

   getstarted
   bibtex
   latex
   ads
   pdf
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

  @MISC{Cubillos2019zndoBibmanager,
         author = {{Cubillos}, Patricio E.},
          title = "{bibmanager: A BibTeX manager for LaTeX projects}",
           year = 2019,
          month = Apr,
            eid = {10.5281/zenodo.2547042},
            doi = {10.5281/zenodo.2547042},
      publisher = {Zenodo},
         url    = {https://doi.org/10.5281/zenodo.2547042},
         adsurl = {https://ui.adsabs.harvard.edu/abs/2019zndo...2547042C},
        adsnote = {Provided by the SAO/NASA Astrophysics Data System},
  }


Featured Articles
=================

| `ADS Blog <http://adsabs.github.io/blog/>`_: **User-Developed Tools for ADS**
| *(30 Jul 2019)*
| http://adsabs.github.io/blog/3rd-party-tools


| `AstroBetter <https://www.astrobetter.com>`_: **Bibmanager: A BibTex Manager Designed for Astronomers**
| *(17 Feb 2020)*
| https://www.astrobetter.com/blog/2020/02/17/bibmanager-a-bibtex-manager-designed-for-astronomers/

---------------------------------------------------------------------------

Please send any feedback or inquiries to:

  Patricio Cubillos (`pcubillos[at]fulbrightmail.org`_)

.. _Patricio Cubillos: https://github.com/pcubillos/
.. _pcubillos[at]fulbrightmail.org: pcubillos@fulbrightmail.org
.. _Space Research Institute (IWF): http://iwf.oeaw.ac.at/

.. |Build Status| image:: https://travis-ci.com/pcubillos/bibmanager.svg?branch=master
   :target: https://travis-ci.com/pcubillos/bibmanager

.. |docs| image:: https://readthedocs.org/projects/bibmanager/badge/?version=latest
    :target: https://bibmanager.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |PyPI| image:: https://img.shields.io/pypi/v/bibmanager.svg
    :target: https://pypi.org/project/bibmanager/
    :alt: Latest Version

.. |conda| image:: https://img.shields.io/conda/vn/conda-forge/bibmanager.svg
    :target: https://anaconda.org/conda-forge/bibmanager

.. |License| image:: https://img.shields.io/github/license/pcubillos/bibmanager.svg?color=blue
    :target: https://pcubillos.github.io/bibmanager/license.html

.. |DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.2547042.svg
    :target: https://doi.org/10.5281/zenodo.2547042


