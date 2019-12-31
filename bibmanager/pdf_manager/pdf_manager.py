# Copyright (c) 2018-2020 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = [
    'guess_name',
    ]

import re


def guess_name(bib, query=''):
    r"""
    Guess a PDF filename for a BibTex entry.  Include at least author
    and year.  If entry has a bibtex, include journal info.

    Parameters
    ----------
    bib: A Bib() instance
        BibTex entry to generate a PDF filename for.
    query: String
        Requesting query form (if quering form ArXiv, then prepend
        'arxiv_' into the name).

    Returns
    -------
    guess_filename: String
        Suggested name for a PDF file of the entry.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> import bibmanager.pdf_manager as pm
    >>> bibs = bm.load()
    >>> # Entry without bibcode:
    >>> bib = bm.Bib('''@misc{AASteam2016aastex61,
    >>>     author       = {{AAS Journals Team} and {Hendrickson}, A.},
    >>>     title        = {AASJournals/AASTeX60: Version 6.1},
    >>>     year         = 2016,
    >>> }''')
    >>> print(pm.guess_name(bib))
    AASJournalsTeam2016.pdf

    >>> # Entry with bibcode:
    >>> bib = bm.Bib('''@ARTICLE{HuangEtal2014jqsrtCO2,
    >>>   author = {{Huang (黄新川)}, Xinchuan and {Gamache}, Robert R.},
    >>>    title = "{Reliable infrared line lists for 13 CO$_{2}$}",
    >>>     year = "2014",
    >>>   adsurl = {https://ui.adsabs.harvard.edu/abs/2014JQSRT.147..134H},
    >>> }''')
    >>> print(pm.guess_name(bib))
    >>> Huang2014_JQSRT_147_134.pdf

    >>> # Say, we are quering from ArXiv:
    >>> print(pm.guess_name(bib, query='http://blah/EPRINT'))
    Huang2014_arxiv_JQSRT_147_134.pdf
    """
    # Remove non-ascii and non-letter characters:
    author = bib.get_authors(format='ushort')
    author = author.encode('ascii', errors='ignore').decode()
    author = re.sub('\W', '', author)

    year = bib.year
    guess_filename = f"{author}{year}.pdf"

    if bib.bibcode is not None:
        journal = re.sub('(\.|&)', '', bib.bibcode[4:9])
        if 'EPRINT' in query and journal.lower() != 'arxiv':
            journal = f'arxiv_{journal}'

        vol  = bib.bibcode[ 9:13].replace('.', '')
        if vol != '':
            vol = f'_{vol}'

        page = bib.bibcode[14:18].replace('.', '')
        if page != '':
            page = f'_{page}'
        guess_filename = f'{author}{year}_{journal}{vol}{page}.pdf'
    return guess_filename

