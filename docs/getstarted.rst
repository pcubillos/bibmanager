.. _getstarted:

Getting Started
===============

``bibmanager`` offers command-line tools to automate the management of BibTeX entries for LaTeX projects.

``bibmanager`` places all of the user's bibtex entries in a centralized database, which is beneficial because it allows to ``bibmanager`` to automate duplicates detection, arxiv-to-peer review updates, and generate bibfiles with the entries specifically required for a LaTeX file.

There are three main categories for the ``bibmanager`` tools:

* :ref:`bibtex` tools help to create, edit, and querry from a
  ``bibmanager`` database, containing all BibTeX entries that a user may need.

* :ref:`latex` tools  help to generate (automatically) a bib file
  for specific LaTeX files, and compile LaTeX files without worring for
  maintaining/updating its bib file.

* :ref:`ads` tools help to makes querries into ADS, add entries
  from ADS, and cross-check the ``bibmanager`` database against ADS, to
  update arXiv-to-peer reviewed entries.

Once installed (see below), take a look at the ``bibmanager`` main menu, executing from the command-line:

.. code-block:: shell

  # Display bibmanager main help menu:
  bibm -h

From there, take a look at the sub-command helps or the rest of these docs for further details, or see the :ref:`qexample` for an introductory worked example.

System Requirements
-------------------

``bibmanager`` is compatible with Python3.6+ and is known to work (at
least) in both Linux and OS X, with the following software:

* python (version 3.6+)
* numpy (version 1.15.1+)
* sphinx (version 1.7.9+)
* sphinx_rtd_theme (version 0.4.2+)
* requests (version 2.19.1+)
* prompt_toolkit (version 2.0.5+)
* pygments (version 2.2.0+)

| ``bibmanager`` may work with previous versions of these software.  However, we do not guarantee it nor provide support for that.
| **TBD: Check versions for py3.6**

.. _install:

Install
-------

To obtain the ``bibmanager`` code, clone this repository to your local machine with the following terminal commands:

.. code-block:: shell

  pip install bibmananger

**TBD:** ``pip install`` is not available yet, but you can follow the steps below:

.. code-block:: shell

  # Clone the repository to your working directory:
  git clone https://github.com/pcubillos/bibmanager/
  cd bibmanager
  python setup.py install


To enable the ADS capability, follow the instructions in the ADS dev API:
https://github.com/adsabs/adsabs-dev-api#access


.. _qexample:

Quick Example
-------------

**Quick Example is TBD.**  The idea is to use the files in the example folder to merge a bibfile, and compile the latex file.

.. code-block:: shell

  # Add your bib file into the bibmanager database:
  bibm merge myfile.bib

  # Compile your Latex project:
  bibm latex myproject.tex

