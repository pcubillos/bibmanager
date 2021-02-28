.. _getstarted:

Getting Started
===============

``bibmanager`` offers command-line tools to automate the management of BibTeX entries for LaTeX projects.

``bibmanager`` places all of the user's bibtex entries in a centralized database, which is beneficial because it allows ``bibmanager`` to automate duplicates detection, arxiv-to-peer review updates, and generate bibfiles with only the entries required for a specific LaTeX file.

There are four main categories for the ``bibmanager`` tools:

* :ref:`bibtex` tools help to create, edit, browse, and query from a
  ``bibmanager`` database, containing all BibTeX entries that a user may need.

* :ref:`latex` tools  help to generate (automatically) a bib file
  for specific LaTeX files, and compile LaTeX files without worring for
  maintaining/updating its bib file.

* :ref:`ads` tools help to makes queries into ADS, add entries
  from ADS, and cross-check the ``bibmanager`` database against ADS, to
  update arXiv-to-peer reviewed entries.

* :ref:`pdf` tools help to maintain a database of the PDF files associated
  to the BibTex entries: Fetch from ADS, set manually, and open in a
  PDF viewer.

Once installed (see below), take a look at the ``bibmanager`` main menu by executing the following command:

.. code-block:: shell

  # Display bibmanager main help menu:
  bibm -h

From there, take a look at the sub-command helps or the rest of these docs for further details, or see the :ref:`qexample` for an introductory worked example.

System Requirements
-------------------

``bibmanager`` is compatible with Python3.6+ and has been `tested <https://travis-ci.com/pcubillos/bibmanager>`_ to work in both Linux and OS X, with the following software:

* numpy (version 1.15.1+)
* requests (version 2.19.1+)
* packaging (version 17.1+)
* prompt_toolkit (version 3.0.5+)
* pygments (version 2.2.0+)

.. * sphinx (version 1.7.9+)
   * sphinx_rtd_theme (version 0.4.2+)


.. _install:

Install
-------

To install ``bibmanager`` run the following command from the terminal:

.. code-block:: shell

    pip install bibmanager

Or if you prefer conda:

.. code-block:: shell

    conda install -c conda-forge bibmanager

Alternatively (e.g., for developers), clone the repository to your local machine with the following terminal commands:

.. code-block:: shell

  git clone https://github.com/pcubillos/bibmanager
  cd bibmanager
  python setup.py develop


.. note:: To enable the ADS functionality, first you need to obtain an `ADS token <https://github.com/adsabs/adsabs-dev-api#access>`_, and set it into the ``ads_tokend`` config parameter.  To do this:

  1. Create an account and login into the new `ADS system <https://ui.adsabs.harvard.edu/?bbbRedirect=1#user/account/login>`_.

  2. Get your token (or generate a new one) from `here <https://ui.adsabs.harvard.edu/#user/settings/token>`_.

  3. Set the ``ads_token`` bibmanager parameter:

  .. code-block:: shell

    # Set ads_token to 'my_ads_token':
    bibm config ads_token my_ads_token


.. _qexample:

Quick Example
-------------

Adding your BibTeX file into ``bibmanager`` is as simple as one command:

.. code-block:: shell

  # Add this sample bibfile into the bibmanager database:
  bibm merge ~/.bibmanager/examples/sample.bib

Compiling a LaTeX file that uses those BibTeX entries is equally simple:

.. code-block:: shell

  # Compile your LaTeX project:
  bibm latex ~/.bibmanager/examples/sample.tex

This command produced a BibTeX file according to the citations in sample.tex; then executed latex, bibtex, latex, latex; and finally  produced a pdf file out of it.  You can see the results in `~/.bibmanager/examples/sample.pdf`.

As long as the citation keys are in the ``bibmanager`` database, you won't need to worry about maintaining a bibfile anymore.  The next sections will show all of the capabilities that ``bibmanager`` offers.
