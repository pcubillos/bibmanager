# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = [
    'guess_name',
    'open',
    'set_pdf',
    'request_ads',
    'fetch',
    ]

import re
import os
import sys
import shutil
import urllib
import subprocess
import webbrowser
# Be explicit about builtin to avoid conflict with pm.open
from io import open as builtin_open

import requests

from .. import bib_manager as bm
from .. import utils as u


def guess_name(bib, arxiv=False):
    r"""
    Guess a PDF filename for a BibTex entry.  Include at least author
    and year.  If entry has a bibtex, include journal info.

    Parameters
    ----------
    bib: A Bib() instance
        BibTex entry to generate a PDF filename for.
    arxiv: Bool
        True if this PDF comes from ArXiv.  If so, prepend 'arxiv_' into
        the output name.

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

    >>> # Say, we are querying from ArXiv:
    >>> print(pm.guess_name(bib, arxiv=True))
    Huang2014_arxiv_JQSRT_147_134.pdf
    """
    # Remove non-ascii and non-letter characters:
    author = bib.get_authors(format='ushort')
    author = author.encode('ascii', errors='ignore').decode()
    author = re.sub('\W', '', author)

    year = '' if bib.year is None else bib.year
    guess_filename = f"{author}{year}.pdf"

    if author == '' and year == '':
        raise ValueError(
            'Could not guess a good filename since entry does not '
            'have author nor year fields')
    if bib.bibcode is not None:
        journal = re.sub('(\.|&)', '', bib.bibcode[4:9])
        if arxiv and journal.lower() != 'arxiv':
            journal = f'arxiv_{journal}'

        vol  = bib.bibcode[ 9:13].replace('.', '')
        if vol != '':
            vol = f'_{vol}'

        page = bib.bibcode[14:18].replace('.', '')
        if page != '':
            page = f'_{page}'
        guess_filename = f'{author}{year}_{journal}{vol}{page}.pdf'
    return guess_filename


def open(pdf=None, key=None, bibcode=None, pdf_file=None):
    """
    Open the PDF file associated to the entry matching the input key
    or bibcode argument.

    Parameters
    ----------
    pdf: String
        PDF file to open.  This refers to a filename located in
        home/pdf/.  Thus, it should not contain the file path.
    key: String
        Key of Bibtex entry to open it's PDF (ignored if pdf is not None).
    bibcode: String
        Bibcode of Bibtex entry to open it's PDF (ignored if pdf or key
        is not None).
    pdf_file: String
        Absolute path to PDF file to open.  If not None, this argument
        takes precedence over pdf, key, and bibcode.
    """
    if pdf is None and key is None and bibcode is None and pdf_file is None:
        raise ValueError("At least one of the arguments must be not None")

    # Set pdf_file:
    if pdf_file is not None:
        pass
    elif pdf is not None:
        pdf_file = u.BM_PDF() + pdf
    else:
        bib = bm.find(key=key, bibcode=bibcode)
        if bib is None:
            raise ValueError('Requested entry does not exist in database')
        if bib.pdf is None:
            raise ValueError('Entry does not have a PDF in the database')
        pdf_file = u.BM_PDF() + bib.pdf

    if not os.path.isfile(pdf_file):
        path, pdf = os.path.split(pdf_file)
        raise ValueError(f"Requested PDF file '{pdf}' does not exist in "
            f"database PDF dir '{path}'")

    # Always use default PDF viewers:
    if sys.platform == "win32":
        os.startfile(pdf_file)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.run([opener, pdf_file], stdout=subprocess.DEVNULL)


def set_pdf(bib, pdf=None, bin_pdf=None, filename=None,
        arxiv=False, replace=False):
    """
    Update the PDF file of the given BibTex entry in database
    If pdf is not None, move the file into the database pdf folder.

    Parameters
    ----------
    bibcode: String or Bib() instance
        Entry to be updated (must exist in the Bibmanager database).
        If string, the ADS bibcode of key ID of the entry.
    pdf: String
        Path to an existing PDF file.
        Only one of pdf and bin_pdf must be not None.
    bin_pdf: String
        PDF content in binary format (e.g., as in req.content).
        Only one of pdf and bin_pdf must be not None.
    arxiv: Bool
        Flag indicating the source of the PDF.  If True, insert
        'arxiv' into a guessed name.
    filename: String
        Filename to assign to the PDF file.  If None, take name from
        pdf input argument, or else from guess_name().
    replace: Bool
        Replace without asking if the entry already has a PDF assigned;
        else, ask the user.

    Returns
    -------
    filename: String
        If bib.pdf is not None at the end of this operation,
        return the absolute path to the bib.pdf file (even if this points
        to a pre-existing file).
        Else, return None.
    """
    if isinstance(bib, str):
        e = bm.find(key=bib)
        bib = bm.find(bibcode=bib) if e is None else e
    if bib is None:
        raise ValueError('BibTex entry is not in Bibmanager database')

    if (pdf is None) + (bin_pdf is None) != 1:
        raise ValueError('Exactly one of pdf or bin_pdf must be not None')

    # Let's have a guess, if needed:
    guess_filename = guess_name(bib, arxiv=arxiv)
    if filename is None:
        filename = os.path.basename(pdf) if pdf is not None else guess_filename

    if not filename.lower().endswith('.pdf'):
        raise ValueError('Invalid filename, must have a .pdf extension')
    if os.path.dirname(filename) != '':
        raise ValueError('filename must not have a path')

    if pdf is not None and bib.pdf is not None:
        pdf_is_not_bib_pdf = os.path.abspath(pdf) != f'{u.BM_PDF()}{bib.pdf}'
    else:
        pdf_is_not_bib_pdf = True

    # PDF files in BM_PDF (except for the entry being fetched):
    pdf_names = [
        file
        for file in os.listdir(u.BM_PDF())
        if os.path.splitext(file)[1].lower() == '.pdf']
    with u.ignored(ValueError):
        pdf_names.remove(bib.pdf)
    if pdf == f'{u.BM_PDF()}{filename}':
        pdf_names.remove(filename)

    if not replace and bib.pdf is not None and pdf_is_not_bib_pdf:
        rep = u.req_input(f"Bibtex entry already has a PDF file: '{bib.pdf}'  "
            "Replace?\n[]yes, [n]o.\n", options=['', 'y', 'yes', 'n', 'no'])
        if rep in ['n', 'no']:
            return f"{u.BM_PDF()}{bib.pdf}"

    while filename in pdf_names:
        overwrite = input(
            f"A filename '{filename}' already exists.  Overwrite?\n"
            f"[]yes, [n]o, or type new file name (e.g., {guess_filename}).\n")
        if overwrite in ['n', 'no']:
            return
        elif overwrite in ['', 'y', 'yes']:
            break
        elif overwrite.lower().endswith('.pdf'):
            filename = overwrite

    # Delete pre-existing file only if not merely renaming:
    if pdf is None or pdf_is_not_bib_pdf:
        with u.ignored(OSError):
            os.remove(f"{u.BM_PDF()}{bib.pdf}")

    if pdf is not None:
        shutil.move(pdf, f"{u.BM_PDF()}{filename}")
    else:
        with builtin_open(f"{u.BM_PDF()}{filename}", 'wb') as f:
            f.write(bin_pdf)
    print(f"Saved PDF to: '{u.BM_PDF()}{filename}'.")

    # Update entry and database:
    bibs = bm.load()
    index = bibs.index(bib)
    bib.pdf = filename
    bibs[index] = bib
    bm.save(bibs)
    bm.export(bibs, meta=True)

    return f"{u.BM_PDF()}{filename}"


def request_ads(bibcode, source='journal'):
    """
    Request a PDF from ADS.

    Parameters
    ----------
    bibcode: String
        ADS bibcode of entry to request PDF.
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


def fetch(bibcode, filename=None, replace=None):
    """
    Attempt to fetch a PDF file from ADS.  If successful, then
    add it into the database.  If the fetch succeeds but the bibcode is
    not in the database, download file to current folder.

    Parameters
    ----------
    bibcode: String
        ADS bibcode of entry to update.
    filename: String
        Filename to assign to the PDF file.  If None, get from
        guess_name() function.
    Replace: Bool
        If True, enforce replacing a PDF regardless of a pre-existing one.
        If None (default), only ask when fetched PDF comes from arxiv.

    Returns
    -------
    filename: String
        If successful, return the full path of the file name.
        If not, return None.
    """
    arxiv = False
    print('Fetching PDF file from Journal website:')
    req = request_ads(bibcode, source='journal')
    if req is None:
        return

    if req.status_code != 200:
        print('Fetching PDF file from ADS website:')
        req = request_ads(bibcode, source='ads')
    if req is None:
        return

    if req.status_code != 200:
        print('Fetching PDF file from ArXiv website:')
        req = request_ads(bibcode, source='arxiv')
        arxiv = True
        if replace is None:
            replace = False
    if req is None:
        return
    if replace is None:
        replace = True

    if req.status_code == 200:
        if bm.find(bibcode=bibcode) is None:
            if filename is None:
                filename = f'{bibcode}.pdf'
            with builtin_open(filename, 'wb') as f:
                f.write(req.content)
            print(f"Saved PDF to: '{filename}'.\n"
                  "(Note that BibTex entry is not in the Bibmanager database)")
        else:
            filename = set_pdf(
                bibcode, bin_pdf=req.content, filename=filename, arxiv=arxiv,
                replace=replace)
        return filename

    print('Could not fetch PDF from any source.')

