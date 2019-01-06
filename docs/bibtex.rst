.. _bibtex:

BibTeX Management
=================

.. _init:

Init
----
Initialize the bibmanager database.

**Usage**

.. code-block:: shell

  bibm init [-h] [bibfile]


This command initializes the bibmanager database (from scratch).
It creates a .bibmanager/ folder in the user folder (if it does not
exists already), and it (re)sets the bibmanager configuration to
its default values.

If the user provides the ``bibfile`` argument, this command will
populate the database with the entries from that file; otherwise,
it will set an empty database.

Note that this will overwrite any pre-existing database.  In
principle the user should not execute this command more than once
in a given CPU.

**Options**

| **bibfile**
|          Path to an existing bibfile.
|
| **-h, -\\-help**
|          Show this help message and exit.

**Examples**

.. code-block:: shell

  # Initialize from scratch (reset):
  bib init

  # Initialize including entries from a bibfile:
  bib init my_file.bib

--------------------------------------------------------------------

.. _merge:

Merge
-----
Merge a bibfile into the bibmanager database.

**Usage**

.. code-block:: shell

  bibm merge [-h] bibfile [take]

**Description**

This commands merges the content from an input bibfile with the
bibmanager database.

The optional 'take' arguments defines the protocol for possible-
duplicate entries.  Either take the 'old' entry (database), take
the 'new' entry (bibfile), or 'ask' the user through the prompt
(displaying the alternatives).  bibmanager considers four fields
to check for duplicates: doi, isbn, adsurl, and eprint.

| Additionally, bibmanager considers two more cases (always asking):
| (1) new entry has duplicate key but different content, and
| (2) new entry has duplicate title but different key.

**Options**

| **bibfile**
|       Path to an existing bibfile.
|
| **take**
|       Decision protocol for duplicates (choose: {old, new, ask}, default: old)
|
| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. code-block:: shell

  # Merge bibfile ignoring duplicates (unless they update from arXiv to peer-reviewed):
  bibm merge my_file.bib

  # Merge bibfile ovewriting entries if they are duplicates:
  bibm merge my_file.bib new

  # Merge bibfile asking the user which to take for each duplicate:
  bibm merge my_file.bib ask

--------------------------------------------------------------------

.. _edit:


Edit
----

Edit the bibmanager database in a text editor.

**Usage**

.. code-block:: shell

  bibm edit [-h]

**Description**

This command let's you manually edit the bibmanager database,
in your pre-defined text editor.  Once finished editing, save and
close the text editor, and press ENTER in the terminal to
incorporate the edits (edits after continuing on the terminal won't
count).

bibmanager selects the OS default text editor.  But the user can
set a preferred editor, see 'bibm config -h' for more information.

**Options**

| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. code-block:: shell

  # Launch text editor on the bibmanager BibTeX database:
  bibm edit

--------------------------------------------------------------------

.. _add:

Add
---
Add entries into the bibmanager database.

**Usage**

.. code-block:: shell

  bibm add [-h] [take]

**Description**

This command allows the user to manually add BibTeX entries into
the bibmanager database through the terminal prompt.

The optional 'take' argument defines the protocol for
possible-duplicate entries.  Either take the 'old' entry (database), take
the 'new' entry (bibfile), or 'ask' the user through the prompt
(displaying the alternatives).  bibmanager considers four fields
to check for duplicates: doi, isbn, adsurl, and eprint.

| Additionally, bibmanager considers two more cases (always asking):
| (1) new entry has duplicate key but different content, and
| (2) new entry has duplicate title but different key.

**Options**

| **take**
|       Decision protocol for duplicates (choose: {old, new, ask}, default: new)
|
| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. code-block:: shell

  # Start multi-line prompt session to enter one or more BibTeX entries:
  bibm add

--------------------------------------------------------------------

.. _search:

Search
------
Search entries in the bibmanager database.

**Usage**

.. code-block:: shell

  bibm search [-h] [-v] [-a AUTHOR ...] [-y YEAR] [-t TITLE ...]

**Description**

This command allows the user to search for entries in the bibmanager
database by authors, years, and keywords in title.  The matching
results are displayed on screen according to the specified verbosity.
For search arguments that include a blank space, the user can set
the string within quotes.

The user can restrict the search to one or more authors, and can
request a first-author match by including the '^' character before
an author name (see examples below).

The user can restrict the publication year to an specific year,
to a range of years, or to open-end range of years (see examples
below).

Finally, the user can restrict the search to multiple strings in
the title (see examples below).  Note these are case-insensitive.

There are four levels of verbosity (see examples below):
- zero shows the title, year, first author, and key;
- one adds the ADS and arXiv urls;
- two adds the full list of authors;
- and three displays the full BibTeX entry.

**Options**

| **-a, -\\-author AUTHOR ...**
|          Search by author.
|
| **-y, -\\-year YEAR**
|           Restrict search to a year (e.g., -y 2018) or to a year range (e.g., -y 2018-2020).
|           Otherwise this is a verly long description of the option.
|
| **-t, -\\-title TITLE ...**
|           Search by keywords in title.
|
| **-v, -\\-verb**
|           Set output verbosity.
|
| **-h, -\\-help**
|           Show this help message and exit.


**Examples**

Name examples:

.. code-block:: shell

  # Search by last name:
  bibm search -a oliphant

  Title: SciPy: Open source scientific tools for Python, 2001
  Authors: Jones, Eric; et al.
  key: JonesEtal2001scipy
  
  Title: Numpy: A guide to NumPy, 2006
  Authors: Oliphant, Travis
  key: Oliphant2006numpy

.. code-block:: shell

  # Search by last name and initials (note blanks require one to use quotes):
  bibm search -a 'oliphant, t'

  Title: SciPy: Open source scientific tools for Python, 2001
  Authors: Jones, Eric; et al.
  key: JonesEtal2001scipy

  Title: Numpy: A guide to NumPy, 2006
  Authors: Oliphant, Travis
  key: Oliphant2006numpy

.. code-block:: shell

  # Search by first-author only:
  bibm search -a '^oliphant, t'

  Title: Numpy: A guide to NumPy, 2006
  Authors: Oliphant, Travis
  key: Oliphant2006numpy

.. code-block:: shell

  # Search multiple authors:
  bibm search -a 'oliphant, t' 'jones, e'

  Title: SciPy: Open source scientific tools for Python, 2001
  Authors: Jones, Eric; et al.
  key: JonesEtal2001scipy

.. note::  Note that there is no need to worry about case,
   unless it interferes with the BibTeX naming format rules.
   For example, *'oliphant, t'* will match *'Travis Oliphant'* (because
   there is no ambiguity in first-von-last names), but *'travis oliphant'*
   wont match, because the lowercase *'travis'* will be interpreted as the
   von part of the last name.

Combine search fields:

.. code-block:: shell

  # Seach by author, year, and title words/phrases:
  bibm search -a 'oliphant, t' -y 2006 -t numpy

  Title: Numpy: A guide to NumPy, 2006
  Authors: Oliphant, Travis
  key: Oliphant2006numpy

.. code-block:: shell

  # Search multiple words/phrases in title:
  bibm search -t 'HD 209458b' 'atmospheric circulation'

  Title: Atmospheric Circulation of Hot Jupiters: Coupled Radiative-Dynamical
     General Circulation Model Simulations of HD 189733b and HD 209458b, 2009
  Authors: {Showman}, Adam P.; et al.
  key: ShowmanEtal2009apjRadGCM

Year examples:

.. code-block:: shell

  # Search on specific year:
  bibm search -a 'cubillos, p' -y 2016

  Title: Characterizing Exoplanet Atmospheres: From Light-curve Observations to
     Radiative-transfer Modeling, 2016
  Authors: {Cubillos}, Patricio E.
  key: Cubillos2016phdThesis

.. code-block:: shell

  # Search anything between the specified years (inclusive):
  bibm search -a 'cubillos, p' -y 2014-2016

  Title: WASP-8b: Characterization of a Cool and Eccentric Exoplanet with Spitzer,
     2013
  Authors: {Cubillos}, Patricio; et al.
  key: CubillosEtal2013apjWASP8b

  Title: Characterizing Exoplanet Atmospheres: From Light-curve Observations to
     Radiative-transfer Modeling, 2016
  Authors: {Cubillos}, Patricio E.
  key: Cubillos2016phdThesis

.. code-block:: shell

  # Search anything up to the specified year:
  bibm search -a 'cubillos, p' -y -2016

  Title: WASP-8b: Characterization of a Cool and Eccentric Exoplanet with Spitzer,
     2013
  Authors: {Cubillos}, Patricio; et al.
  key: CubillosEtal2013apjWASP8b

  Title: Characterizing Exoplanet Atmospheres: From Light-curve Observations to
     Radiative-transfer Modeling, 2016
  Authors: {Cubillos}, Patricio E.
  key: Cubillos2016phdThesis

.. code-block:: shell

  # Search anything since the specified year:
  bibm search -a 'cubillos, p' -y 2016-

  Title: Characterizing Exoplanet Atmospheres: From Light-curve Observations to
     Radiative-transfer Modeling, 2016
  Authors: {Cubillos}, Patricio E.
  key: Cubillos2016phdThesis

  Title: On Correlated-noise Analyses Applied to Exoplanet Light Curves, 2017
  Authors: {Cubillos}, Patricio; et al.
  key: CubillosEtal2017apjRednoise

Verbosity examples:

.. code-block:: shell

  # Display title, year, first author, and key:
  bibm search -a 'Burbidge, E'

  Title: Synthesis of the Elements in Stars, 1957
  Authors: {Burbidge}, E. Margaret; et al.
  key: BurbidgeEtal1957rvmpStellarElementSynthesis

.. code-block:: shell

  # Display title, year, first author, and all keys/urls:
  bibm search -a 'Burbidge, E' -v

  Title: Synthesis of the Elements in Stars, 1957
  Authors: {Burbidge}, E. Margaret; et al.
  ADS url:   https://ui.adsabs.harvard.edu/\#abs/1957RvMP...29..547B
  key: BurbidgeEtal1957rvmpStellarElementSynthesis

.. code-block:: shell

  # Display title, year, author list, and all keys/urls:
  bibm search -a 'Burbidge, E' -vv

  Title: Synthesis of the Elements in Stars, 1957
  Authors: {Burbidge}, E. Margaret; {Burbidge}, G. R.; {Fowler}, William A.; and
     {Hoyle}, F.
  ADS url:   https://ui.adsabs.harvard.edu/\#abs/1957RvMP...29..547B
  key: BurbidgeEtal1957rvmpStellarElementSynthesis

.. code-block:: shell

  # Display full BibTeX entry:
  bibm search -a 'Burbidge, E' -vvv

  @ARTICLE{BurbidgeEtal1957rvmpStellarElementSynthesis,
         author = {{Burbidge}, E. Margaret and {Burbidge}, G.~R. and {Fowler}, William A.
          and {Hoyle}, F.},
          title = "{Synthesis of the Elements in Stars}",
        journal = {Reviews of Modern Physics},
           year = 1957,
          month = Jan,
         volume = {29},
          pages = {547-650},
            doi = {10.1103/RevModPhys.29.547},
         adsurl = {https://ui.adsabs.harvard.edu/\#abs/1957RvMP...29..547B},
        adsnote = {Provided by the SAO/NASA Astrophysics Data System}
  }

--------------------------------------------------------------------

.. _export:

Export
------
Export the bibmanager database into a bib file.

**Usage**

.. code-block:: shell

  bibm export [-h] bibfile

**Description**

Export the entire bibmanager database into a bibliography file to a
.bib or .bbl format according to the file extension of the
'bibfile' argument.

.. caution:: For the moment, only export to .bib.

**Options**

| **bibfile**
|       Path to an output bibfile.
|
| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. code-block:: shell

  bibm export my_file.bib


--------------------------------------------------------------------

.. _config:

Config
------
Manage the bibmanager configuration parameters.

**Usage**

.. code-block:: shell

  bibm config [-h] [param] [value]

**Description**

This command displays or sets the value of bibmanager config parameters.
There are five parameters that can be set by the user:

- The ``style`` parameter sets the color-syntax style of displayed BibTeX
  entries.  The default style is 'autumn'.
  See http://pygments.org/demo/6780986/ for a demo of the style options.
  The available options are:

    default, emacs, friendly, colorful, autumn, murphy, manni, monokai, perldoc,
    pastie, borland, trac, native, fruity, bw, vim, vs, tango, rrt, xcode, igor,
    paraiso-light, paraiso-dark, lovelace, algol, algol_nu, arduino,
    rainbow_dash, abap

- The ``text_editor`` sets the text editor to use when editing the
  bibmanager manually (i.e., a call to: bibm edit).  By default, bibmanager
  uses the OS-default text editor.
  Typical text editors are: emacs, vim, gedit.
  To set the OS-default editor, set text_editor to *'default'*.
  Note that aliases defined in the .bash file are not accessible.

- The ``paper`` parameter sets the default paper format for latex
  compilation outputs (not for pdflatex, which is automatic).
  Typical options are 'letter' (e.g., for ApJ articles) or 'A4' (e.g., for A&A).

- The ``ads_token`` parameter sets the ADS token required for ADS requests.
  To obtain a token, follow the steps described here: https://github.com/adsabs/adsabs-dev-api#access

- The ``ads_display`` parameter sets the number of entries to show at a time,
  for an ADS search querry.  The default number of entries to display is 20.

The number of arguments determines the action of this command (see
examples below):

- with no arguments, display all available parameters and values.
- with the 'param' argument, display detailed info on the specified
  parameter and its current value.
- with both 'param' and 'value' arguments, set the value of the parameter.

**Options**

| **param**
|       A bibmanager config parameter.
|
| **value**
|       Value for a bibmanager config parameter.
|
| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. code-block:: shell

  # Display all config parameters and values:
  bibm config

  bibmanager configuration file:
  PARAMETER    VALUE
  -----------  -----
  style        autumn
  text_editor  default
  paper        letter
  ads_token    None
  ads_display  20

.. code-block:: shell

  # Display value and help for the ads_token parameter:
  bibm config ads_token

  The 'ads_token' parameter sets the ADS token required for ADS requests.
  To obtain a token follow the two steps described here:
    https://github.com/adsabs/adsabs-dev-api#access
  
  The current ADS token is 'None'

.. code-block:: shell

  # Set the value of the BibTeX color-syntax:
  bibm config style autumn

  style updated to: autumn.
