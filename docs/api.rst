API
===


bibmanager
__________


.. py:module:: bibmanager


bibmanager.bib_manager
______________________


.. py:module:: bibmanager.bib_manager

.. py:class:: Bib(entry)

.. code-block:: pycon

    Bibliographic-entry object.

.. code-block:: pycon

    Create a Bib() object from given entry.  Minimally, entries must
    contain the author, title, and year keys.

    Parameters
    ----------
    entry: String
       A bibliographic entry text.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> from bibmanager.utils import Author
    >>> entry = '''@Misc{JonesEtal2001scipy,
              author = {Eric Jones and Travis Oliphant and Pearu Peterson},
              title  = {{SciPy}: Open source scientific tools for {Python}},
              year   = {2001},
            }'''
    >>> bib = bm.Bib(entry)
    >>> print(bib.title)
    SciPy: Open source scientific tools for Python
    >>> for author in bib.authors:
    >>>    print(author)
    Author(last='Jones', first='Eric', von='', jr='')
    Author(last='Oliphant', first='Travis', von='', jr='')
    Author(last='Peterson', first='Pearu', von='', jr='')
    >>> print(bib.sort_author)
    Sort_author(last='jones', first='e', von='', jr='', year=2001, month=13)

.. py:function:: display_bibs(labels, bibs)
.. code-block:: pycon

    Display a list of bib entries on screen with flying colors.

    Parameters
    ----------
    labels: List of Strings
       Header labels to show above each Bib() entry.
    bibs: List of Bib() objects
       BibTeX entries to display.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> e1 = '''@Misc{JonesEtal2001scipy,
           author = {Eric Jones and Travis Oliphant and Pearu Peterson},
           title  = {{SciPy}: Open source scientific tools for {Python}},
           year   = {2001},
         }'''
    >>> e2 = '''@Misc{Jones2001,
           author = {Eric Jones and Travis Oliphant and Pearu Peterson},
           title  = {SciPy: Open source scientific tools for Python},
           year   = {2001},
         }'''
    >>> bibs = [bm.Bib(e1), bm.Bib(e2)]
    >>> bm.display_bibs(["DATABASE:\n", "NEW:\n"], bibs)
    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    DATABASE:
    @Misc{JonesEtal2001scipy,
           author = {Eric Jones and Travis Oliphant and Pearu Peterson},
           title  = {{SciPy}: Open source scientific tools for {Python}},
           year   = {2001},
         }

    NEW:
    @Misc{Jones2001,
           author = {Eric Jones and Travis Oliphant and Pearu Peterson},
           title  = {SciPy: Open source scientific tools for Python},
           year   = {2001},
         }

.. py:function:: remove_duplicates(bibs, field)
.. code-block:: pycon

    Look for duplicates (within a same list of entries) by field and
    remove them (in place).

    Parameters
    ----------
    bibs: List of Bib() objects
       Entries to filter.
    field: String
       Field to use for filtering ('doi', 'isbn', 'bibcode', or 'eprint').

.. py:function:: filter_field(bibs, new, field, take)
.. code-block:: pycon

    Filter duplicate entries by field between new and bibs.
    This routine modifies new removing the duplicates, and may modify
    bibs (depending on take argument).

    Parameters
    ----------
    bibs: List of Bib() objects
       Database entries.
    new: List of Bib() objects
       New entries to add.
    field: String
       Field to use for filtering.
    take: String
       Decision-making protocol to resolve conflicts when there are
       partially duplicated entries.
       'old': Take the database entry over new.
       'new': Take the new entry over the database.
       'ask': Ask user to decide (interactively).

.. py:function:: loadfile(bibfile=None, text=None)
.. code-block:: pycon

    Create a list of Bib() objects from a BibTeX file (.bib file).

    Parameters
    ----------
    bibfile: String
       Path to an existing .bib file.
    text: String
       Content of a .bib file (ignored if bibfile is not None).

    Returns
    -------
    bibs: List of Bib() objects
       List of Bib() objects of BibTeX entries in bibfile, sorted by
       Sort_author() fields.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> import os
    >>> bibfile = os.path.expanduser("~") + "/.bibmanager/examples/sample.bib"
    >>> bibs = bm.loadfile(bibfile)

.. py:function:: save(entries)
.. code-block:: pycon

    Save list of Bib() entries into bibmanager pickle database.

    Parameters
    ----------
    entries: List of Bib() objects
       bib files to store.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> # TBD: Load some entries
    >>> bm.save(entries)

.. py:function:: load()
.. code-block:: pycon

    Load the bibmanager database of BibTeX entries.

    Returns
    -------
    List of Bib() entries.  Return an empty list if there is no database
    file.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> bibs = bm.load()

.. py:function:: export(entries, bibfile='/Users/pato/.bibmanager/bm_bibliography.bib')
.. code-block:: pycon

    Export list of Bib() entries into a .bib file.

    Parameters
    ----------
    entries: List of Bib() objects
       Entries to export.
    bibfile: String
       Output .bib file name.

.. py:function:: merge(bibfile=None, new=None, take='old', base=None)
.. code-block:: pycon

    Merge entries from a new bibfile into the bibmanager database
    (or into an input database).

    Parameters
    ----------
    bibfile: String
        New .bib file to merge into the bibmanager database.
    new: List of Bib() objects
        List of new BibTeX entries (ignored if bibfile is not None).
    take: String
        Decision-making protocol to resolve conflicts when there are
        partially duplicated entries.
        'old': Take the database entry over new.
        'new': Take the new entry over the database.
        'ask': Ask user to decide (interactively).
    base: List of Bib() objects
        If None, merge new entries into the bibmanager database.
        If not None, merge new intries into base.

    Returns
    -------
    bibs: List of Bib() objects
        Merged list of BibTeX entries.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> import os
    >>> # TBD: Need to add sample2.bib into package.
    >>> newbib = os.path.expanduser("~") + "/.bibmanager/examples/sample2.bib"
    >>> # Merge newbib into database:
    >>> bm.merge(newbib, take='old')

.. py:function:: init(bibfile='/Users/pato/.bibmanager/bm_bibliography.bib', reset_db=True, reset_config=False)
.. code-block:: pycon

    Initialize bibmanager, reset database entries and config parameters.

    Parameters
    ----------
    bibfile: String
       A bibfile to include as the new bibmanager database.
       If None, reset the bibmanager database with a clean slate.
    reset_db: Bool
       If True, reset the bibmanager database.
    reset_config: Bool
       If True, reset the config file.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> import os
    >>> bibfile = os.path.expanduser("~") + "/.bibmanager/examples/sample.bib"
    >>> bm.init(bibfile)

.. py:function:: add_entries(take='ask')
.. code-block:: pycon

    Manually add BibTeX entries through the prompt.

    Parameters
    ----------
    take: String
       Decision-making protocol to resolve conflicts when there are
       partially duplicated entries.
       'old': Take the database entry over new.
       'new': Take the new entry over the database.
       'ask': Ask user to decide (interactively).

.. py:function:: edit()
.. code-block:: pycon

    Manually edit the bibfile database in text editor.

    Resources
    ---------
    https://stackoverflow.com/questions/17317219/
    https://docs.python.org/3.6/library/subprocess.html

.. py:function:: search(authors=None, year=None, title=None, key=None, bibcode=None)
.. code-block:: pycon

    Search in bibmanager database by authors, year, or title keywords.

    Parameters
    ----------
    authors: String or List of strings
       An author name (or list of names) with BibTeX format (see parse_name()
       docstring).  To restrict search to a first author, prepend the
       '^' character to a name.
    year: Integer or two-element integer tuple
       If integer, match against year; if tuple, minimum and maximum
       matching years (including).
    title: String or iterable (list, tuple, or ndarray of strings)
       Match entries that contain all input strings in the title (ignore case).
    key: String or list of strings
       Match any entry whose key is in the input key.
    bibcode: String or list of strings
       Match any entry whose bibcode is in the input bibcode.

    Returns
    -------
    matches: List of Bib() objects
       Entries that match all input criteria.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> # Search by last name:
    >>> matches = bm.search(authors="Cubillos")
    >>> # Search by last name and initial:
    >>> matches = bm.search(authors="Cubillos, P")
    >>> # Search by author in given year:
    >>> matches = bm.search(authors="Cubillos, P", year=2017)
    >>> # Search by first author and co-author (using AND logic):
    >>> matches = bm.search(authors=["^Cubillos", "Blecic"])
    >>> # Search by keyword in title:
    >>> matches = bm.search(title="Spitzer")
    >>> # Search by keywords in title (using AND logic):
    >>> matches = bm.search(title=["HD 189", "HD 209"])
    >>> # Search by key (note that unlike the other fields, key and
    >>> # bibcode use OR logic, so you can get many items at once):
    >>> matches = bm.search(key="Astropycollab2013aaAstropy")
    >>> # Search by bibcode (note no need to worry about UTF-8 encoding):
    >>> matches = bm.search(bibcode=["2013A%26A...558A..33A",
    >>>                              "1957RvMP...29..547B",
    >>>                              "2017AJ....153....3C"])


bibmanager.config_manager
_________________________


.. py:module:: bibmanager.config_manager

.. py:function:: help(key)
.. code-block:: pycon

    Display help information.

    Parameters
    ----------
    key: String
       A bibmanager config parameter.

.. py:function:: display(key=None)
.. code-block:: pycon

    Display the value(s) of the bibmanager config file on the prompt.

    Parameters
    ----------
    key: String
       bibmanager config parameter to display.  Leave as None to display the
       values from all parameters.

    Examples
    --------
    >>> import bibmanager.config_manager as cm
    >>> # Show all parameters and values:
    >>> cm.display()
    bibmanager configuration file:
    PARAMETER    VALUE
    -----------  -----
    style        autumn
    text_editor  default
    paper        letter
    ads_token    None
    ads_display  20

    >>> # Show an specific parameter:
    >>> cm.display('text_editor')
    text_editor: default

.. py:function:: get(key)
.. code-block:: pycon

    Get the value of a parameter in the bibmanager config file.

    Parameters
    ----------
    key: String
       The requested parameter name.

    Returns
    -------
    value: String
       Value of the requested parameter.

    Examples
    --------
    >>> import bibmanager.config_manager as cm
    >>> cm.get('paper')
    'letter'
    >>> cm.get('style')
    'autumn'

.. py:function:: set(key, value)
.. code-block:: pycon

    Set the value of a bibmanager config parameter.

    Parameters
    ----------
    key: String
       bibmanager config parameter to set.
    value: String
       Value to set for input parameter.

    Examples
    --------
    >>> import bibmanager.config_manager as cm
    >>> # Update text editor:
    >>> cm.set('text_editor', 'vim')
    text_editor updated to: vim.

    >>> # Invalid bibmanager parameter:
    >>> cm.set('styles', 'arduino')
    ValueError: 'styles' is not a valid bibmanager config parameter. The available
    parameters are:  ['style', 'text_editor', 'paper', 'ads_token', 'ads_display']

    >>> # Attempt to set an invalid style:
    >>> cm.set('style', 'fake_style')
    ValueError: 'fake_style' is not a valid style option.  Available options are:
      default, emacs, friendly, colorful, autumn, murphy, manni, monokai, perldoc,
      pastie, borland, trac, native, fruity, bw, vim, vs, tango, rrt, xcode, igor,
      paraiso-light, paraiso-dark, lovelace, algol, algol_nu, arduino,
      rainbow_dash, abap

    >>> # Attempt to set an invalid command for text_editor:
    >>> cm.set('text_editor', 'my_own_editor')
    ValueError: 'my_own_editor' is not a valid text editor.

    >>> # Beware, one can still set a valid command that doesn't edit text:
    >>> cm.set('text_editor', 'less')
    text_editor updated to: less.

.. py:function:: update_keys()
.. code-block:: pycon

    Update config in HOME with keys from ROOT, without overwriting values.


bibmanager.latex_manager
________________________


.. py:module:: bibmanager.latex_manager

.. py:function:: no_comments(text)
.. code-block:: pycon

    Remove comments from tex file, partially inspired by this:
    https://stackoverflow.com/questions/2319019

    Parameters
    ----------
    text: String
       Content from a latex file.

    Returns
    -------
    no_comments_text: String
       Input text with removed comments (as defined by latex format).

    Examples
    --------
    >>> import bibmanager.latex_manager as lm
    >>> text = r'''
    Hello, this is dog.
    % This is a comment line.
    This line ends with a comment. % A comment
    However, this is a percentage \%, not a comment.
    OK, byee.'''
    >>> print(lm.no_comments(text))
    Hello, this is dog.
    This line ends with a comment.
    However, this is a percentage \%, not a comment.
    OK, byee.

.. py:function:: citations(text)
.. code-block:: pycon

    Generator to find citations in a tex text.  Partially inspired
    by this: https://stackoverflow.com/questions/29976397

    Notes
    -----
    Act recursively in case there are references inside the square
    brackets of the cite call.  Only failing case I can think so far
    is if there are nested square brackets.

    Parameters
    ----------
    text: String
       String where to search for the latex citations.

    Yields
    ------
    citation: String
       The citation key.

    Examples
    --------
    >>> import bibmanager.latex_manager as lm
    >>> import os
    >>> # Syntax matches any of these calls:
    >>> tex = r'''
    \citep{AuthorA}.
    \citep[pre]{AuthorB}.
    \citep[pre][post]{AuthorC}.
    \citep [pre] [post] {AuthorD}.
    \citep[{\pre},][post]{AuthorE, AuthorF}.
    \citep[pre][post]{AuthorG} and \citep[pre][post]{AuthorH}.
    \citep{
     AuthorI}.
    \citep
    [][]{AuthorJ}.
    \citep[pre
     ][post] {AuthorK, AuthorL}
    \citep[see also \citealp{AuthorM}][]{AuthorN}'''
    >>> for citation in lm.citations(tex):
    >>>     print(citation, end=" ")
    AuthorA AuthorB AuthorC AuthorD AuthorE AuthorF AuthorG AuthorH AuthorI AuthorJ AuthorK AuthorL AuthorM AuthorN

    >>> # Match all of these cite calls:
    >>> tex = r'''
    \cite{AuthorA}, \nocite{AuthorB}, \defcitealias{AuthorC}.
    \citet{AuthorD}, \citet*{AuthorE}, \Citet{AuthorF}, \Citet*{AuthorG}.
    \citep{AuthorH}, \citep*{AuthorI}, \Citep{AuthorJ}, \Citep*{AuthorK}.
    \citealt{AuthorL},     \citealt*{AuthorM},
    \Citealt{AuthorN},     \Citealt*{AuthorO}.
    \citealp{AuthorP},     \citealp*{AuthorQ},
    \Citealp{AuthorR},     \Citealp*{AuthorS}.
    \citeauthor{AuthorT},  \citeauthor*{AuthorU}.
    \Citeauthor{AuthorV},  \Citeauthor*{AuthorW}.
    \citeyear{AuthorX},    \citeyear*{AuthorY}.
    \citeyearpar{AuthorZ}, \citeyearpar*{AuthorAA}.'''
    >>> for citation in lm.citations(tex):
    >>>     print(citation, end=" ")
    AuthorA AuthorB AuthorC AuthorD AuthorE AuthorF AuthorG AuthorH AuthorI AuthorJ AuthorK AuthorL AuthorM AuthorN AuthorO AuthorP AuthorQ AuthorR AuthorS AuthorT AuthorU AuthorV AuthorW AuthorX AuthorY AuthorZ AuthorAA

    >>> texfile = os.path.expanduser('~')+"/.bibmanager/examples/sample.tex"
    >>> with open(texfile) as f:
    >>>     tex = f.read()
    >>> tex = lm.no_comments(tex)
    >>> cites = [citation for citation in lm.citations(tex)]
    >>> for key in np.unique(cites):
    >>>     print(key)
    AASteamHendrickson2018aastex62
    Astropycollab2013aaAstropy
    Hunter2007ieeeMatplotlib
    JonesEtal2001scipy
    MeurerEtal2017pjcsSYMPY
    PerezGranger2007cseIPython
    vanderWaltEtal2011numpy

.. py:function:: build_bib(texfile, bibfile=None)
.. code-block:: pycon

    Generate a .bib file from a given tex file.

    Parameters
    ----------
    texfile: String
       Name of an input tex file.
    bibfile: String
       Name of an output bib file.  If None, get bibfile name from
       bibliography call inside the tex file.

    Returns
    -------
    missing: List of strings
       List of the bibkeys not found in the bibmanager database.

.. py:function:: clear_latex(texfile)
.. code-block:: pycon

    Remove by-products of previous latex compilations.

    Parameters
    ----------
    texfile: String
       Path to an existing .tex file.

    Notes
    -----
    For an input argument texfile='filename.tex', this function deletes
    the files that begin with 'filename' followed by:
      .bbl, .blg, .out, .dvi,
      .log, .aux, .lof, .lot,
      .toc, .ps,  .pdf, Notes.bib

.. py:function:: compile_latex(texfile, paper=None)
.. code-block:: pycon

    Compile a .tex file into a .pdf file using latex calls.

    Parameters
    ----------
    texfile: String
       Path to an existing .tex file.
    paper: String
       Paper size for output.  For example, ApJ articles use letter
       format, whereas A&A articles use A4 format.

    Notes
    -----
    This function executes the following calls:
    - compute a bibfile out of the citation calls in the .tex file.
    - removes all outputs from previous compilations (see clear_latex())
    - calls latex, bibtex, latex, latex to produce a .dvi file
    - calls dvips to produce a .ps file, redirecting the output to
      ps2pdf to produce the final .pdf file.

.. py:function:: compile_pdflatex(texfile)
.. code-block:: pycon

    Compile a .tex file into a .pdf file using pdflatex calls.

    Parameters
    ----------
    texfile: String
       Path to an existing .tex file.

    Notes
    -----
    This function executes the following calls:
    - compute a bibfile out of the citation calls in the .tex file.
    - removes all outputs from previous compilations (see clear_latex())
    - calls pdflatex, bibtex, pdflatex, pdflatex to produce a .pdf file


bibmanager.ads_manager
______________________


.. py:module:: bibmanager.ads_manager

.. py:function:: manager(querry=None)
.. code-block:: pycon

    A manager, it doesn't really do anything, it just delegates.

.. py:function:: search(querry, start=0, cache_rows=200, sort='pubdate+desc')
.. code-block:: pycon

    Make a querry from ADS.

    Parameters
    ----------
    querry: String
       A querry string like an entry in the new ADS interface:
       https://ui.adsabs.harvard.edu/
    start: Integer
       Starting index of entry to return.
    cache_rows: Integer
       Maximum number of entries to return.
    sort: String
       Sorting field and direction to use.

    Returns
    -------
    results: List of dicts
       Querry outputs between indices start and start+rows.
    nmatch: Integer
       Total number of entries matched by the querry.

    Resources
    ---------
    A comprehensive description of the querry format:
    - http://adsabs.github.io/help/search/
    Description of the querry parameters:
    - https://github.com/adsabs/adsabs-dev-api/blob/master/Search_API.ipynb

    Examples
    --------
    >>> import bibmanager.ads_manager as am
    >>> # Search entries by author (note the need for double quotes,
    >>> # otherwise, the search might produce bogus results):
    >>> querry = 'author:"cubillos, p"'
    >>> results, nmatch = am.search(querry)
    >>> # Search entries by first author:
    >>> querry = 'author:"^cubillos, p"'
    >>> # Combine search by first author and year:
    >>> querry = 'author:"^cubillos, p" year:2017'
    >>> # Restrict seach to article-type entries:
    >>> querry = 'author:"^cubillos, p" property:article'
    >>> # Restrict seach to peer-reviewed articles:
    >>> querry = 'author:"^cubillos, p" property:refereed'

    >>> # Attempt with invalid token:
    >>> results, nmatch = am.search(querry)
    ValueError: Invalid ADS request: Unauthorized, check you have a valid ADS token.
    >>> # Attempt with invalid querry ('properties' instead of 'property'):
    >>> results, nmatch = am.search('author:"^cubillos, p" properties:refereed')
    ValueError: Invalid ADS request:
    org.apache.solr.search.SyntaxError: org.apache.solr.common.SolrException: undefined field properties

.. py:function:: display(results, start, index, rows, nmatch, short=True)
.. code-block:: pycon

    Show on the prompt a list of entries from an ADS search.

    Parameters
    ----------
    results: List of dicts
       Subset of entries returned by a querry.
    start: Integer
       Index assigned to first entry in results.
    index: Integer
       First index to display.
    rows: Integer
       Number of entries to display.
    nmatch: Integer
       Total number of entries corresponding to querry (not necessarily
       the number of entries in results).
    short: Bool
       Format for author list. If True, truncate with 'et al' after
       the second author.

    Examples
    --------
    >>> import bibmanager.ads_manager as am
    >>> start = index = 0
    >>> querry = 'author:"^cubillos, p" property:refereed'
    >>> results, nmatch = am.search(querry, start=start)
    >>> display(results, start, index, rows, nmatch)

.. py:function:: add_bibtex(input_bibcodes, input_keys, eprints=[], dois=[], update_keys=True, base=None)
.. code-block:: pycon

    Add bibtex entries from a list of ADS bibcodes, with specified keys.
    New entries will replace old ones without asking if they are
    duplicates.

    Parameters
    ----------
    input_bibcodes: List of strings
        A list of ADS bibcodes.
    imput_keys: List of strings
        BibTeX keys to assign to each bibcode.
    eprints: List of strings
        List of ArXiv IDs corresponding to the input bibcodes.
    dois: List of strings
        List of DOIs corresponding to the input bibcodes.
    update_keys: Bool
        If True, attempt to update keys of entries that were updated
        from arxiv to published versions.
    base: List of Bib() objects
        If None, merge new entries into the bibmanager database.
        If not None, merge new entries into base.

    Returns
    -------
    bibs: List of Bib() objects
        Updated list of BibTeX entries.

    Examples
    --------
    >>> import bibmanager.ads_manager as am
    >>> # A successful add call:
    >>> bibcodes = ['1925PhDT.........1P']
    >>> keys = ['Payne1925phdStellarAtmospheres']
    >>> am.add_bibtex(bibcodes, keys)
    >>> # A failing add call:
    >>> bibcodes = ['1925PhDT....X....1P']
    >>> am.add_bibtex(bibcodes, keys)
    Error: There were no entries found for the input bibcodes.

    >>> # A successful add call with multiple entries:
    >>> bibcodes = ['1925PhDT.........1P', '2018MNRAS.481.5286F']
    >>> keys = ['Payne1925phdStellarAtmospheres', 'FolsomEtal2018mnrasHD219134']
    >>> am.add_bibtex(bibcodes, keys)
    >>> # A partially failing call will still add those that succeed:
    >>> bibcodes = ['1925PhDT.....X...1P', '2018MNRAS.481.5286F']
    >>> am.add_bibtex(bibcodes, keys)
    Warning: bibcode '1925PhDT.....X...1P' not found.

.. py:function:: update(update_keys=True, base=None)
.. code-block:: pycon

    Do an ADS querry by bibcode for all entries that have an ADS bibcode.
    Replacing old entries with the new ones.  The main use of
    this function is to update arxiv version of articles.

    Parameters
    ----------
    update_keys: Bool
        If True, attempt to update keys of entries that were updated
        from arxiv to published versions.

.. py:function:: key_update(key, bibcode, alternate_bibcode)
.. code-block:: pycon

    Update key with year and journal of arxiv version of a key.

    This function will search and update the year in a key,
    and the journal if the key contains the word 'arxiv' (case
    insensitive).

    The function extracts the info from the old and new bibcodes.
    ADS bibcode format: http://adsabs.github.io/help/actions/bibcode

    Examples
    --------
    >>> import bibmanager.ads_manager as am
    >>> key = 'BeaulieuEtal2010arxivGJ436b'
    >>> bibcode           = '2011ApJ...731...16B'
    >>> alternate_bibcode = '2010arXiv1007.0324B'
    >>> new_key = am.key_update(key, bibcode, alternate_bibcode)
    >>> print(f'{key}\n{new_key}')
    BeaulieuEtal2010arxivGJ436b
    BeaulieuEtal2011apjGJ436b

    >>> key = 'CubillosEtal2018arXivRetrievals'
    >>> bibcode           = '2019A&A...550A.100B'
    >>> alternate_bibcode = '2018arXiv123401234B'
    >>> new_key = am.key_update(key, bibcode, alternate_bibcode)
    >>> print(f'{key}\n{new_key}')
    CubillosEtal2018arXivRetrievals
    CubillosEtal2019aaRetrievals


bibmanager.utils
________________


.. py:module:: bibmanager.utils

.. py:data:: HOME
.. code-block:: pycon

  '/Users/pato/.bibmanager/'

.. py:data:: ROOT
.. code-block:: pycon

  '/Users/pato/anaconda3/envs/py37/lib/python3.7/site-packages/bibmanager/'

.. py:data:: BM_DATABASE
.. code-block:: pycon

  '/Users/pato/.bibmanager/bm_database.pickle'

.. py:data:: BM_BIBFILE
.. code-block:: pycon

  '/Users/pato/.bibmanager/bm_bibliography.bib'

.. py:data:: BM_TMP_BIB
.. code-block:: pycon

  '/Users/pato/.bibmanager/tmp_bibliography.bib'

.. py:data:: BM_CACHE
.. code-block:: pycon

  '/Users/pato/.bibmanager/cached_ads_querry.pickle'

.. py:data:: BM_HISTORY_SEARCH
.. code-block:: pycon

  '/Users/pato/.bibmanager/history_search'

.. py:data:: BM_HISTORY_ADS
.. code-block:: pycon

  '/Users/pato/.bibmanager/history_ads_search'

.. py:data:: BOLD
.. code-block:: pycon

  '\x1b[1m'

.. py:data:: END
.. code-block:: pycon

  '\x1b[0m'

.. py:data:: BANNER
.. code-block:: pycon

  '\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n'

.. py:data:: search_completer
.. code-block:: pycon

  <prompt_toolkit.completion.word_completer.WordCompleter object at 0x120b462e8>

.. py:data:: ads_completer
.. code-block:: pycon

  <prompt_toolkit.completion.word_completer.WordCompleter object at 0x120b46dd8>

.. py:class:: Author(last, first, von, jr)

.. code-block:: pycon

    Author(last, first, von, jr)

.. code-block:: pycon

    Initialize self.  See help(type(self)) for accurate signature.

.. py:class:: Sort_author(last, first, von, jr, year, month)

.. code-block:: pycon

    Sort_author(last, first, von, jr, year, month)

.. code-block:: pycon

    Initialize self.  See help(type(self)) for accurate signature.

.. py:function:: ignored(*exceptions)
.. code-block:: pycon

    Context manager to ignore exceptions. Taken from here:
    https://www.youtube.com/watch?v=anrOzOapJ2E

.. py:function:: cd(newdir)
.. code-block:: pycon

    Context manager for changing the current working directory.
    Taken from here: https://stackoverflow.com/questions/431684/

.. py:function:: ordinal(number)
.. code-block:: pycon

    Get ordinal string representation for input number(s).

    Parameters
    ----------
    number: Integer or 1D integer ndarray
       An integer or array of integers.

    Returns
    -------
    ord: String or List of strings
       Ordinal representation of input number(s).  Return a string if
       input is int; else, return a list of strings.

    Examples
    --------
    >>> from bibmanager.utils import ordinal
    >>> print(ordinal(1))
    1st
    >>> print(ordinal(2))
    2nd
    >>> print(ordinal(11))
    11th
    >>> print(ordinal(111))
    111th
    >>> print(ordinal(121))
    121st
    >>> print(ordinal(np.arange(1,6)))
    ['1st', '2nd', '3rd', '4th', '5th']

.. py:function:: count(text)
.. code-block:: pycon

    Count net number of braces in text (add 1 for each opening brace,
    subtract one for each closing brace).

    Parameters
    ----------
    text: String
       A string.

    Returns
    -------
    counts: Integer
       Net number of braces.

    Examples
    --------
    >>> from bibmanager.utils import count
    >>> count('{Hello} world')
    0

.. py:function:: nest(text)
.. code-block:: pycon

    Get braces nesting level for each character in text.

    Parameters
    ----------
    text: String
       String to inspect.

    Returns
    -------
    counts: 1D integer list
       Braces nesting level for each character.

    Examples
    --------
    >>> from bibmanager.utils import nest
    >>> s = "{{P\\'erez}, F. and {Granger}, B.~E.},"
    >>> n = nest(s)
    >>> print(f"{s}\n{''.join([str(v) for v in n])}")
    {{P\'erez}, F. and {Granger}, B.~E.},
    0122222222111111111122222222111111110

.. py:function:: cond_split(text, pattern, nested=None, nlev=-1, ret_nests=False)
.. code-block:: pycon

    Conditional find and split strings in a text delimited by all
    occurrences of pattern where the brace-nested level is nlev.

    Parameters
    ----------
    text: String
       String where to search for pattern.
    pattern: String
       A regex pattern to search.
    nested: 1D integer iterable
       Braces nesting level of characters in text.
    nlev: Integer
       Required nested level to accept pattern match.
    ret_nests: Bool
       If True, return a list with the arrays of nested level for each
       of the returned substrings.

    Returns
    -------
    substrings: List of strings
       List of strings delimited by the accepted pattern matches.
    nests: List of integer ndarrays [optional]
       nested level for substrings.

    Examples
    --------
    >>> from bibmanager.utils import cond_split
    >>> # Split an author list string delimited by ' and ' pattern:
    >>> cond_split("{P\\'erez}, F. and {Granger}, B.~E.", " and ")
    ["{P\\'erez}, F.", '{Granger}, B.~E.']
    >>> # Protected instances (within braces) won't count:
    >>> cond_split("{AAS and Astropy Teams} and {Hendrickson}, A.", " and ")
    ['{AAS and Astropy Teams}', '{Hendrickson}, A.']
    >>> # Matches at the beginning or end do not count for split:
    >>> cond_split(",Jones, Oliphant, Peterson,", ",")
    ['Jones', ' Oliphant', ' Peterson']
    >>> # But two consecutive matches do return an empty string:
    >>> cond_split("Jones,, Peterson", ",")
    ['Jones', '', ' Peterson']

.. py:function:: cond_next(text, pattern, nested, nlev=1)
.. code-block:: pycon

    Find next instance of pattern in text where nested is nlev.

    Parameters
    ----------
    text: String
       Text where to search for regex.
    pattern: String
       Regular expression to search for.
    nested: 1D integer iterable
       Braces-nesting level of characters in text.
    nlev: Integer
       Requested nested level.

    Returns
    -------
       Index integer of pattern in text.  If not found, return the
       index of the last character in text.

    Examples
    --------
    >>> from bibmanager.utils import nest, cond_next
    >>> text = '"{{HITEMP}, the high-temperature molecular database}",'
    >>> nested = nest(text)
    >>> # Ignore comma within braces:
    >>> cond_next(text, ",", nested, nlev=0)
    53

.. py:function:: parse_name(name, nested=None)
.. code-block:: pycon

    Parse first, last, von, and jr parts from a name, following these rules:
    http://mirror.easyname.at/ctan/info/bibtex/tamethebeast/ttb_en.pdf
    Page 23.

    Parameters
    ----------
    name: String
       A name following the BibTeX format.
    nested: 1D integer ndarray
       Nested level of characters in name.

    Returns
    -------
    author: Author namedtuple
       Four element tuple with the parsed name.

    Examples
    --------
    >>> from bibmanager.utils import parse_name
    >>> names = ['{Hendrickson}, A.',
    >>>          'Eric Jones',
    >>>          '{AAS Journals Team}',
    >>>          "St{\\'{e}}fan van der Walt"]
    >>> for name in names:
    >>>     print(f'{repr(name)}:\n{parse_name(name)}\n')
    '{Hendrickson}, A.':
    Author(last='{Hendrickson}', first='A.', von='', jr='')

    'Eric Jones':
    Author(last='Jones', first='Eric', von='', jr='')

    '{AAS Journals Team}':
    Author(last='{AAS Journals Team}', first='', von='', jr='')

    "St{\\'{e}}fan van der Walt":
    Author(last='Walt', first="St{\\'{e}}fan", von='van der', jr='')

.. py:function:: repr_author(Author)
.. code-block:: pycon

    Get string representation an Author namedtuple in the format:
    von Last, jr., First.

    Parameters
    ----------
    Author: An Author() namedtuple
       An author name.

    Examples
    --------
    >>> from bibmanager.utils import repr_author, parse_name
    >>> names = ['Last', 'First Last', 'First von Last', 'von Last, First',
    >>>          'von Last, sr., First']
    >>> for name in names:
    >>>     print(f"{name!r:22}: {repr_author(parse_name(name))}")
    'Last'                : Last
    'First Last'          : Last, First
    'First von Last'      : von Last, First
    'von Last, First'     : von Last, First
    'von Last, sr., First': von Last, sr., First

.. py:function:: purify(name, german=False)
.. code-block:: pycon

    Replace accented characters closely following these rules:
    https://tex.stackexchange.com/questions/57743/
    For a more complete list of special characters, see Table 2.2 of
    'The Not so Short Introduction to LaTeX2e' by Oetiker et al. (2008).

    Parameters
    ----------
    name: String
       Name to be 'purified'.
    german: Bool
       Replace umlaut with german style (append 'e' after).

    Returns
    -------
    Lower-cased name without accent characters.

    Examples
    --------
    >>> from bibmanager.utils import purify
    >>> names = ["St{\\'{e}}fan",
                 "{{\\v S}ime{\\v c}kov{\\'a}}",
                 "{AAS Journals Team}",
                 "Kov{\\'a}{\\v r}{\\'i}k",
                 "Jarom{\\'i}r Kov{\\'a\\v r\\'i}k",
                 "{\\.I}volgin",
                 "Gon{\\c c}alez Nu{\~n}ez",
                 "Knausg{\\aa}rd Sm{\\o}rrebr{\\o}d",
                 'Schr{\\"o}dinger Be{\\ss}er']

    >>> for name in names:
    >>>     print(f"{name!r:35}: {purify(name)}")
    "St{\\'{e}}fan"                     : stefan
    "{{\\v S}ime{\\v c}kov{\\'a}}"      : simeckova
    '{AAS Journals Team}'               : aas journals team
    "Kov{\\'a}{\\v r}{\\'i}k"           : kovarik
    "Jarom{\\'i}r Kov{\\'a\\v r\\'i}k"  : jaromir kovarik
    '{\\.I}volgin'                      : ivolgin
    'Gon{\\c c}alez Nu{\\~n}ez'         : goncalez nunez
    'Knausg{\\aa}rd Sm{\\o}rrebr{\\o}d' : knausgaard smorrebrod
    'Schr{\\"o}dinger Be{\\ss}er'       : schrodinger besser

.. py:function:: initials(name)
.. code-block:: pycon

    Get initials from a name.

    Parameters
    ----------
    name: String
       A name.

    Returns
    -------
    initials: String
       Name initials (lower cased).

    Examples
    --------
    >>> from bibmanager.utils import initials
    >>> names = ["", "D.", "D. W.", "G.O.", '{\\"O}. H.', "J. Y.-K.",
    >>>          "Phil", "Phill Henry Scott"]
    >>> for name in names:
    >>>     print(f"{name!r:20}: {initials(name)!r}")
    ''                  : ''
    'D.'                : 'd'
    'D. W.'             : 'dw'
    'G.O.'              : 'g'
    '{\\"O}. H.'        : 'oh'
    'J. Y.-K.'          : 'jyk'
    'Phil'              : 'p'
    'Phill Henry Scott' : 'phs'
    >>> # 'G.O.' is a typo by the user, should have had a blank in between.

.. py:function:: get_authors(authors, short=True)
.. code-block:: pycon

    Get string representation for the author list.

    Parameters
    ----------
    authors: List of Author() nametuple
    short: Bool
       If True, use 'short' format displaying at most the first two
       authors followed by 'et al.' if corresponds.
       If False, display the full list of authors.

    Examples
    --------
    >>> from bibmanager.utils import get_authors, parse_name
    >>> author_lists = [
    >>>     [parse_name('{Hunter}, J. D.')],
    >>>     [parse_name('{AAS Journals Team}'), parse_name('{Hendrickson}, A.')],
    >>>     [parse_name('Eric Jones'), parse_name('Travis Oliphant'),
    >>>      parse_name('Pearu Peterson'), parse_name('others')]
    >>>    ]
    >>> # Short format:
    >>> for i,authors in enumerate(author_lists):
    >>>     print(f"{i+1} author(s): {get_authors(authors)}")
    1 author(s): {Hunter}, J. D.
    2 author(s): {AAS Journals Team} and {Hendrickson}, A.
    3 author(s): Jones, Eric; et al.
    >>> # Long format:
    >>> for i,authors in enumerate(author_lists):
    >>>     print(f"{i+1} author(s): {get_authors(authors, short=False)}")
    1 author(s): {Hunter}, J. D.
    2 author(s): {AAS Journals Team} and {Hendrickson}, A.
    3 author(s): Jones, Eric; Oliphant, Travis; Peterson, Pearu; and others

.. py:function:: next_char(text)
.. code-block:: pycon

    Get index of next non-blank character in string text.
    Return zero if all characters are blanks.

    Parameters
    ----------
    text: String
       A string, duh!.

    Examples
    --------
    >>> from bibmanager.utils import next_char
    >>> texts = ["Hello", "  Hello", "  Hello ", "", "\n Hello", "  "]
    >>> for text in texts:
    >>>     print(f"{text!r:11}: {next_char(text)}")
    'Hello'    : 0
    '  Hello'  : 2
    '  Hello ' : 2
    ''         : 0
    '\n Hello' : 2
    '  '       : 0

.. py:function:: last_char(text)
.. code-block:: pycon

    Get index of last non-blank character in string text.

    Parameters
    ----------
    text: String
       A string, duh!.

    Examples
    --------
    >>> from bibmanager.utils import last_char
    >>> texts = ["Hello", "  Hello", "  Hello  ", "", "\n Hello", "  "]
    >>> for text in texts:
    >>>     print(f"{text!r:12}: {last_char(text)}")
    'Hello'     : 5
    '  Hello'   : 7
    '  Hello  ' : 7
    ''          : 0
    '\n Hello'  : 7
    '  '        : 0

.. py:function:: get_fields(entry)
.. code-block:: pycon

    Generator to parse entries of a bibbliographic entry.

    Parameters
    ----------
    entry: String
       A bibliographic entry text.

    Yields
    ------
    The first yield is the entry's key.  All following yields are
    three-element tuples containing a field name, field value, and
    nested level of the field value.

    Notes
    -----
    Global quotations or braces on a value are removed before yielding.

    Example
    -------
    >>> from bibmanager.utils import get_fields
    >>> entry = '''
    @Article{Hunter2007ieeeMatplotlib,
      Author    = {{Hunter}, J. D.},
      Title     = {Matplotlib: A 2D graphics environment},
      Journal   = {Computing In Science \& Engineering},
      Volume    = {9},
      Number    = {3},
      Pages     = {90--95},
      publisher = {IEEE COMPUTER SOC},
      doi       = {10.1109/MCSE.2007.55},
      year      = 2007
    }'''
    >>> fields = get_fields(entry)
    >>> # Get the entry's key:
    >>> print(next(fields))
    Hunter2007ieeeMatplotlib

    >>> # Now get the fields, values, and nested level:
    >>> for key, value, nested in fields:
    >>>   print(f"{key:9}: {value}\n{'':11}{''.join([str(v) for v in nested])}")
    author   : {Hunter}, J. D.
               233333332222222
    title    : Matplotlib: A 2D graphics environment
               2222222222222222222222222222222222222
    journal  : Computing In Science \& Engineering
               22222222222222222222222222222222222
    volume   : 9
               2
    number   : 3
               2
    pages    : 90--95
               222222
    publisher: IEEE COMPUTER SOC
               22222222222222222
    doi      : 10.1109/MCSE.2007.55
               22222222222222222222
    year     : 2007
               1111

.. py:function:: req_input(prompt, options)
.. code-block:: pycon

    Query for an aswer to prompt message until the user provides a
    valid input (i.e., answer is in options).

    Parameters
    ----------
    prompt: String
       Prompt text for input()'s argument.
    options: List
       List of options to accept.  Elements in list are casted into strings.

    Returns
    -------
    answer: String
       The user's input.

    Examples
    --------
    >>> from bibmanager.utils import req_input
    >>> req_input('Enter number between 0 and 9: ', options=np.arange(10))
    >>> # Enter the number 10:
    Enter number between 0 and 9: 10
    >>> # Now enter the number 5:
    Not a valid input.  Try again: 5
    '5'

.. py:class:: AutoSuggestCompleter()

.. code-block:: pycon

    Give suggestions based on the words in WordCompleter.

.. code-block:: pycon

    Initialize self.  See help(type(self)) for accurate signature.

