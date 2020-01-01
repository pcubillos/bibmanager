# Copyright (c) 2018-2020 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = [
    'guess_name',
    'open',
    'request_ads',
    ]

import re
import os
import sys
import urllib
import subprocess
import webbrowser

import requests

from .. import config_manager as cm
from .. import bib_manager as bm
from .. import utils as u


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


def open(key):
    """
    Open the PDF file associated to the entry for given key.

    Parameters
    ----------
    key: String
        Key of bibtex entry to open it's PDF.
    """
    for bib in bm.load():
        if bib.key == key:
            break
    else:
        raise ValueError('Input key is not in the database.')

    if bib.pdf is None:
        raise ValueError('Entry does not have a PDF in the database.')
    pdf_file = cm.get('pdf_dir') + bib.pdf

    # Always use default PDF viewers:
    if sys.platform == "win32":
        os.startfile(pdf_file)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, pdf_file])


def request_ads(bibcode, source='journal'):
    """
    Request a PDF from ADS.

    Parameters
    ----------
    query: String
        ADS request form.
    source: String
        Flag to indicate from which source make the request.
        Choose between: 'journal', 'ads', or 'arxiv'.

    Returns
    -------
    req: requests.Response instance
        The server's response to the HTTP request.
        Return None if it failed to establish a connection.

    Note
    ----
    If the request succeeded, but the response content is not a PDF,
    this function modifies the value of req.status_code (in a desperate
    attempt to give a meaningful answer).

    Examples
    --------
    >>> import bibmanager.pdf_manager as pm
    >>> bibcode = '2017AJ....153....3C'
    >>> req = pm.request_ads(bibcode)

    >>> # On successful request, you can save the PDF file as, e.g.:
    >>> with open('fetched_file.pdf', 'wb') as f:
    >>>     f.write(r.content)

    >>> # Nature articles are not directly accessible from Journal:
    >>> bibcode = '2018NatAs...2..220D'
    >>> req = pm.request_ads(bibcode)
    Request failed with status code 404: NOT FOUND
    >>> # Get ArXiv instead:
    >>> req = pm.request_ads(bibcode, source='arxiv')
    """
    sources = {
        'journal': 'PUB_PDF',
        'arxiv': 'EPRINT_PDF',
        'ads': 'ADS_PDF',
    }
    if source not in sources:
        raise ValueError(f"Source argument must be one of {list(sources)}")

    query = ('https://ui.adsabs.harvard.edu/link_gateway/'
            f'{urllib.parse.quote(bibcode)}/{sources[source]}')

    # This fixed MNRAS requests and CAPTCHA issues:
    # (take from https://stackoverflow.com/questions/43165341)
    headers = requests.utils.default_headers()
    headers['User-Agent'] = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')
    # Make the request:
    try:
        req = requests.get(query, headers=headers)
    except requests.exceptions.ConnectionError:
        print('Failed to establish a web connection.')
        return None

    if not req.ok:
        print(f'Request failed with status code {req.status_code}: '
              f'{req.reason}')

    elif req.headers['Content-Type'].startswith('text/html') \
            and 'CAPTCHA' in req.content.decode():
        browse = u.req_input('There are issues with CAPTCHA verification, '
            'try to open PDF in browser?\n[]yes [n]o.\n',
            options=['', 'y', 'yes', 'n', 'no'])
        if browse in ['', 'y', 'yes']:
            webbrowser.open(query, new=2)
            print("\nIf you managed to download the PDF, add the PDF into "
                "the database\nwith the following command (and right path):\n"
               f"bibm pdf-set '{bibcode}' PATH/TO/FILE.pdf filename")
            req.status_code = -101
        else:
            req.status_code = -102

    # Request is OK, but output is not a PDF:
    elif not req.headers['Content-Type'].startswith('application/pdf'):
        print('Request succeeded, but fetched content is not a PDF (might '
              'have been\nredirected to website due to paywall).')
        req.status_code = -100

    return req


