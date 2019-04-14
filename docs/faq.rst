.. _scenarios:

FAQs and Resources
==================

Frequently Asked Questions
--------------------------

Why should I use ``bibmanager``? I have already my working ecosystem.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``bibmanager`` simply makes your life easier, keeping all of your references
at the tip of your fingers:

- No need to wonder whether to start a new BibTeX file from scratch or reuse
  an old one (probably a massive file), nor to think which was the most current.
- Easily add new entries: manually, from your existing BibTeX files, or
  from ADS, without risking having duplicates.
- Generate BibTeX files and compile a LaTeX project with a single command.
- You can stay up to date with ADS with a single command.

----------------------------------------------------------------------

I compiled my LaTeX file before merging its bibfile, did I just overwite my own BibTeX file?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

No, if ``bibmanager`` has to overwrite a bibfile edited by the user (say,
`'myrefs.bib'`), it saves the old file (and date) as
`'orig_yyyy-mm-dd_myrefs.bib'`.

----------------------------------------------------------------------

I meged the BibTeX file for my LaTeX project, but it says there are missing references when I compile. What's going on?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Probably, there were duplicate entries with previous entries in the
``bibmanager`` database, but they had different keys.  Simply, do a search
of your missing reference, to check it's key, something like:

.. code-block:: shell

  # Surely, first author and year have not changed:
  bibm search
  author:"^Author" year:the_year

Now, you can update the key in the LaTeX file (and as a bonus, you wont
run into having duplicate entries in the future).

----------------------------------------------------------------------

A unique database? Does it mean I need to have better keys to differentiate my entries?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Certainly, as a database grows, short BibTeX keys like `'LastnameYYYY'`
are sub-optimal, since they may conflict with other entries, and are not
descriptive enough.
A good practice is to adopt a longer, more descriptive format.
I personally suggests this one:

=======  ================================  ===============================
Authors  Format                            Example
=======  ================================  ===============================
   1     LastYYYYjournalDescription        Shapley1918apjDistanceGClusters
   2     Last1Last2YYYYjournalDescription  PerezGranger2007cseIPython
   3     LastEtalYYYYjournalDescription    AstropycollabEtal2013aaAstropy
=======  ================================  ===============================

That is:

- the first-author last name (capitalized)
- either nothing, the second-author last name (capitalized), or `'Etal'`
- the publication year
- the journal initials if any (and lower-cased)
- a couple words from the title that describe the article
  (capitalized or best format at user's discretion).

These long keys will keep you from running into issues, and will make
the citations in your LaTeX documents nearly unambiguous at sight.

----------------------------------------------------------------------

Resources
---------

| Docs for querries in the new ADS:
| http://adsabs.github.io/help/search/search-syntax

| The ADS API:
| https://github.com/adsabs/adsabs-dev-api

| BibTeX author format:
| http://mirror.easyname.at/ctan/info/bibtex/tamethebeast/ttb_en.pdf
| http://texdoc.net/texmf-dist/doc/bibtex/base/btxdoc.pdf

| Pygment style BibTeX options:
| http://pygments.org/demo/6693571/

| Testing:
| https://docs.pytest.org/
| http://pythontesting.net/framework/pytest/pytest-fixtures-nuts-bolts/
| https://blog.dbrgn.ch/2016/2/18/overriding_default_arguments_in_pytest/
| https://www.patricksoftwareblog.com/monkeypatching-with-pytest/
| https://requests-mock.readthedocs.io/en/

| Useful info from stackoverflow:
| https://stackoverflow.com/questions/17317219
| https://stackoverflow.com/questions/18011902
| https://stackoverflow.com/questions/26899001
| https://stackoverflow.com/questions/2241348
| https://stackoverflow.com/questions/1158076
