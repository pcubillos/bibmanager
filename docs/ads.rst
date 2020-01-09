.. _ads:

ADS Management
==============

.. note:: To enable the ADS functionality, first you need to obtain an ADS token [#ADStoken]_, and set it into the ``ads_tokend`` config parameter.  To do this:

  1. Create an account and login into the new `ADS system <https://ui.adsabs.harvard.edu/?bbbRedirect=1#user/account/login>`_.

  2. Get your token (or generate a new one) from `here <https://ui.adsabs.harvard.edu/#user/settings/token>`_.

  3. Set the ``ads_token`` bibmanager parameter:

  .. code-block:: shell

    # Set ads_token to 'my_ads_token':
    bibm config ads_token my_ads_token

----------------------------------------------------------------------

ads-search
----------

Do a query on ADS.

**Usage**

.. code-block:: shell

  bibm ads-search [-h] [query]

**Description**

This command enables ADS querries.  The query syntax is identical to
a query in the new ADS's one-box search engine:
https://ui.adsabs.harvard.edu.
Here there is a detailed documentations for ADS searches:
https://adsabs.github.io/help/search/search-syntax
See below for typical query examples.

.. note:: Note that a query will display at most 'ads_display' entries on
  screen at once (see ``bibm config ads_display``).  If a query matches
  more entries, the user can execute ``bibm ads-search -n``
  to display the next set of entries.

.. caution:: When making an ADS query, note that
  ADS requires the field values (when necessary) to use `double` quotes.
  For example: `author:"^Fortney, J"`.

**Options**

| **texfile**
|       Path to an existing LaTeX file.
|
| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. code-block:: shell

  # Search entries for given author (press tab to prompt the autocompleter):
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"^Fortney, J"

  Title: Exploring A Photospheric Radius Correction to Model Secondary Eclipse
         Spectra for Transiting Exoplanets
  Authors: Fortney, Jonathan J.; et al.
  adsurl:  https://ui.adsabs.harvard.edu/abs/2019arXiv190400025F
  bibcode: 2019arXiv190400025F

  Title: Laboratory Needs for Exoplanet Climate Modeling
  Authors: Fortney, J. J.; et al.
  adsurl:  https://ui.adsabs.harvard.edu/abs/2018LPICo2065.2068F
  bibcode: 2018LPICo2065.2068F

  ...

  Showing entries 1--20 out of 74 matches.  To show the next set, execute:
  bibm ads-search -n


Basic author search examples:

.. code-block:: shell

  # Search by author in article:
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"Fortney, J"

  # Search by first author:
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"^Fortney, J"

  # Search multiple authors:
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:("Fortney, J" AND "Showman, A")

Search combining multiple fields:

.. code-block:: shell

  # Seach by author AND year:
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"Fortney, J" year:2010

  # Seach by author AND year range:
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"Fortney, J" year:2010-2019

  # Search by author AND words/phrases in title:
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"Fortney, J" title:Spitzer

  # Search by author AND words/phrases in abstract:
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"Fortney, J" abs:"HD 209458b"

Restrict searches to articles or peer-reviewed articles:

.. code-block:: shell

  # Search by author AND request only articles:
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"Fortney, J" property:article

  # Search by author AND request only peer-reviewed articles:
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"Fortney, J" property:refereed

----------------------------------------------------------------------

ads-add
-------

Add entries from ADS by bibcode into the bibmanager database.

**Usage**

.. code-block:: shell

  bibm ads-add [-h] [bibcode key]

**Description**

This command add BibTeX entries from ADS by specifying pairs of
ADS bibcodes and BibTeX keys.

Executing this command without arguments (i.e., ``bibm ads-add``) launches
an interactive prompt session allowing the user to enter multiple
bibcode, key pairs.

By default, added entries replace previously existent entries in the
bibmanager database.

**Options**

| **bibcode**
|       The ADS bibcode of an entry.
|
| **key**
|       BibTeX key to assign to the entry.
|
| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. code-block:: shell

  # Let's search and add the greatest astronomy PhD thesis of all times:
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"^payne, cecilia" doctype:phdthesis

  Title: Stellar Atmospheres; a Contribution to the Observational Study of High
         Temperature in the Reversing Layers of Stars.
  Authors: Payne, Cecilia Helena
  adsurl:  https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P
  bibcode: 1925PhDT.........1P


  # Add the entry to the bibmanager database:
  bibm ads-add 1925PhDT.........1P Payne1925phdStellarAtmospheres

----------------------------------------------------------------------

.. _ads-update:

ads-update
----------

Update bibmanager database cross-checking entries with ADS.

**Usage**

.. code-block:: shell

  bibm ads-update [-h] [update_keys]

**Description**

This command triggers an ADS search of all entries in the ``bibmanager``
database that have a ``bibcode``.  Replacing these entries with
the output from ADS.
The main utility of this command is to auto-update entries that
were added as arXiv version, with their published version.

For arXiv updates, this command updates automatically the year and
journal of the key (where possible).  This is done by searching for
the year and the string `'arxiv'` in the key, using the bibcode info.
For example, an entry with key `'NameEtal2010arxivGJ436b'` whose bibcode
changed from `'2010arXiv1007.0324B'` to `'2011ApJ...731...16B'`, will have
a new key `'NameEtal2011apjGJ436b'`.
To disable this feature, set the ``update_keys`` optional argument to `'no'`.

**Options**

| **update_keys**
|       Update the keys of the entries. (choose from: {no, arxiv}, default: arxiv).
|
| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. note::  These example outputs assume that you merged the sample bibfile
  already, i.e.: ``bibm merge ~/.bibmanager/examples/sample.bib``

.. code-block:: shell

  # Look at this entry with old info from arXiv:
  bibm search -v
  author:"^Beaulieu"

  Title: Methane in the Atmosphere of the Transiting Hot Neptune GJ436b?, 2010
  Authors: {Beaulieu}, J.-P.; et al.
  bibcode:   2010arXiv1007.0324B
  ADS url:   http://adsabs.harvard.edu/abs/2010arXiv1007.0324B
  arXiv url: http://arxiv.org/abs/arXiv:1007.0324
  key: BeaulieuEtal2010arxivGJ436b


  # Update bibmanager entries that are in ADS:
  bibm ads-update

  Merged 0 new entries.
  (Not counting updated references)
  There were 1 entries updated from ArXiv to their peer-reviewed version.
  These ones changed their key:
  BeaulieuEtal2010arxivGJ436b -> BeaulieuEtal2011apjGJ436b


  # Let's take a look at this entry again:
  bibm search -v
  author:"^Beaulieu"

  Title: Methane in the Atmosphere of the Transiting Hot Neptune GJ436B?, 2011
  Authors: {Beaulieu}, J. -P.; et al.
  bibcode:   2011ApJ...731...16B
  ADS url:   https://ui.adsabs.harvard.edu/abs/2011ApJ...731...16B
  arXiv url: http://arxiv.org/abs/1007.0324
  key: BeaulieuEtal2011apjGJ436b

.. note::  There might be cases when one does not want to ADS-update an
    entry.  To prevent this to happen, the user can set the *freeze*
    meta-parameter through the ``bibm edit`` command (see :ref:`edit`).

----------------------------------------------------------------------

**References**

.. [#ADStoken] https://github.com/adsabs/adsabs-dev-api#access
