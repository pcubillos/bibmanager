.. _scenarios:

Frequently Asked Questions
==========================

Case Study #1
-------------

I merged a bib, but it kept old bibkeys.

Now my compilation output says:
bibkey not found.
solution:
You can do a search by name and author to get the bibkey maintained
in the bibmanager database:
bibm search -a ^Author -y year
Now, simply update the bibkey in the .tex file.

Case Study #2
-------------

I ran bibm compile on my latex file before merging its bibfile,
did I just lost my references?

No, if bibmanager has to overwrite a bibfile edited by the user, it
saves the old file into prebm\_file.bib

Auto-update arXiv entries
-------------------------

There were 3 entries updated from ArXiv to their peer-reviewed version.
These ones changed their key:
KreidbergEtal2017apjlWASP107bWFC3 -> KreidbergEtal2018apjlWASP107bWFC3

Issues
------

Short BibTeX keys
One of the issues that a user might find by having a unique BibTeX database
is that now short not-so-descriptive keys like 'Lastname2019' might not be
enough to distinguish references if an author publishes more than one article
a year.  This forces the user to use somewhat more descriptive keys.  I
personally suggests these formats for single, two, and multiple authors:
format                            Example
LastYYYYjournalDescription        Shapley1918apjDistanceGlobularClusters
Last1Last2YYYYjournalDescription  AASteamHendrickson2018zenodoAASTeX62
LastEtalYYYYjournalDescription    AstropycollabEtal2013aaAstropy

Clearly, these long keys raise the issue that the citations in your LaTeX
document are now very unambiguous as to which article one is refeering.


ADS querries
------------

note there is a limit of 5000 querries per user per day
https://github.com/adsabs/adsabs-dev-api

Resources
~~~~~~~~~

http://texdoc.net/texmf-dist/doc/bibtex/base/btxdoc.pdf
BibTeX author format:
http://mirror.easyname.at/ctan/info/bibtex/tamethebeast/ttb_en.pdf
Pygment style BibTeX options:
http://pygments.org/demo/6693571/

ADS search:
http://adsabs.github.io/help/search/search-syntax
