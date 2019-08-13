# Copyright (c) 2018-2019 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = [
    'manager',
    'search',
    'display',
    'add_bibtex',
    'update',
    'key_update',
]

import os
import re
import json
import urllib
import textwrap
import pickle

import requests

from .. import bib_manager    as bm
from .. import config_manager as cm
from .. import utils as u


def manager(querry=None):
    """
    A manager, it doesn't really do anything, it just delegates.
    """
    rows  = int(cm.get('ads_display'))
    if querry is None and not os.path.exists(u.BM_CACHE):
        print("There are no more entries for this querry.")
        return

    if querry is None:
        with open(u.BM_CACHE, 'rb') as handle:
            results, querry, start, index, nmatch = pickle.load(handle)
        last = start + len(results)
        if last < nmatch and index + rows > last:
            new_results, nmatch = search(querry, start=last)
            results = results[index-start:] + new_results
            start = index
            last = start + len(results)
    else:
        start = 0
        index = start
        results, nmatch = search(querry, start=start)

    display(results, start, index, rows, nmatch)
    index += rows
    if index >= nmatch:
        with u.ignored(OSError):
            os.remove(u.BM_CACHE)
    else:
        with open(u.BM_CACHE, 'wb') as handle:
            pickle.dump([results, querry, start, index, nmatch], handle,
                        protocol=pickle.HIGHEST_PROTOCOL)


def search(querry, start=0, cache_rows=200, sort='pubdate+desc'):
    """
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
    """
    token = cm.get('ads_token')
    querry = urllib.parse.quote(querry)

    r = requests.get('https://api.adsabs.harvard.edu/v1/search/query?'
                    f'q={querry}&start={start}&rows={cache_rows}'
                     f'&sort={sort}&fl=title,author,year,bibcode,pub',
                     headers={'Authorization': f'Bearer {token}'})
    resp = r.json()
    if 'error' in resp:
        if resp['error'] == 'Unauthorized':
            raise ValueError(f"Invalid ADS request: {resp['error']}, "
                              "check you have a valid ADS token.")
        raise ValueError(f"Invalid ADS request:\n{resp['error']['msg']}.")

    nmatch  = resp['response']['numFound']
    results = resp['response']['docs']

    return results, nmatch


def display(results, start, index, rows, nmatch, short=True):
    """
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
    """
    for result in results[index-start:index-start+rows]:
        title = textwrap.fill(f"Title: {result['title'][0]}", width=78,
                              subsequent_indent='       ')
        author_list = [u.parse_name(author) for author in result['author']]
        authors = textwrap.fill(f"Authors: {u.get_authors(author_list, short)}",
                                width=78, subsequent_indent='    ')
        adsurl = ("adsurl:  https://ui.adsabs.harvard.edu/abs/" +
                 f"{result['bibcode']}")
        bibcode = f"\n{u.BOLD}bibcode{u.END}: {result['bibcode']}"
        print(f"\n{title}\n{authors}\n{adsurl}{bibcode}")
    if index + rows < nmatch:
        more = "  To show the next set, execute:\nbibm ads-search -n"
    else:
        more = ""
    print(f"\nShowing entries {index+1}--{min(index+rows, nmatch)} out of "
          f"{nmatch} matches.{more}")


def add_bibtex(input_bibcodes, input_keys, eprints=[], dois=[],
               update_keys=True, base=None):
    """
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
    """
    token = cm.get('ads_token')
    # Keep the originals untouched (copies will be modified):
    bibcodes, keys = input_bibcodes.copy(), input_keys.copy()

    # Make request:
    r = requests.post("https://api.adsabs.harvard.edu/v1/export/bibtex",
                      headers={"Authorization": f'Bearer {token}',
                               "Content-type": "application/json"},
                      data=json.dumps({"bibcode":bibcodes}))
    resp = r.json()

    # No valid outputs:
    if 'error' in resp:
        if resp['error'] == 'Unauthorized':
            print('\nError: Unauthorized access to ADS.  Check that the ADS '
                  'token is valid.')
        elif resp['error'] == 'no result from solr':
            print("\nError: There were no entries found for the input bibcodes.")
        else:
            print("\nError: ADS request returned an error message:"
                 f"\n{resp['error']}")
        return

    # Keep counts of things:
    nfound = int(resp['msg'].split()[1])
    nreqs  = len(bibcodes)

    # Split output into separate BibTeX entries (keep as strings):
    results = resp["export"].strip().split("\n\n")

    new_keys = []
    new_bibs = []
    founds = [False for _ in bibcodes]
    arxiv_updates = 0
    # Match results to bibcodes,keys:
    for result in reversed(results):
        ibib = None
        new = bm.Bib(result)
        rkey   = new.key
        doi    = new.doi
        eprint = new.eprint
        # Output bibcode is input bibcode:
        if rkey in bibcodes:
            ibib = bibcodes.index(rkey)
            new_key = keys[ibib]
        # Else, check for bibcode updates in remaining bibcodes:
        elif eprint is not None and eprint in eprints:
            ibib = eprints.index(eprint)
        elif doi is not None and doi in dois:
            ibib = dois.index(doi)

        if ibib is not None:
            new_key = keys[ibib]
            updated_key = key_update(new_key, rkey, bibcodes[ibib])
            if update_keys and updated_key.lower() != new_key.lower():
                new_key = updated_key
                new_keys.append([keys[ibib], new_key])
            if 'arXiv' in bibcodes[ibib] and 'arXiv' not in new.bibcode:
                arxiv_updates += 1

            new.update_key(new_key)
            new_bibs.append(new)
            founds[ibib] = True
            results.remove(result)

    # Warnings:
    if nfound < nreqs or len(results) > 0:
        warning = u.BANNER + "Warning:\n"
        # bibcodes not found
        missing = [bibcode for bibcode,found in zip(bibcodes, founds)
                   if not found]
        if nfound < nreqs:
            warning += '\nThere were bibcodes unmatched or not found in ADS:\n - '
            warning += '\n - '.join(missing) + "\n"
        # bibcodes not matched:
        if len(results) > 0:
            warning += '\nThese ADS results did not match input bibcodes:\n\n'
            warning += '\n\n'.join(results) + "\n"
        warning += u.BANNER
        print(warning)

    # Add to bibmanager database or base:
    updated = bm.merge(new=new_bibs, take='new', base=base)
    print('(Not counting updated references)')

    # Report arXiv updates:
    if arxiv_updates > 0:
        print(f"\nThere were {arxiv_updates} entries updated from ArXiv to "
               "their peer-reviewed version.")
    if len(new_keys) > 0:
        new_keys = [f"  {old} -> {new}" for old,new in new_keys
                    if old != new]
        if len(new_keys) > 0:
            print("These entries changed their key:\n" + "\n".join(new_keys))
    return updated


def update(update_keys=True, base=None):
    """
    Do an ADS querry by bibcode for all entries that have an ADS bibcode.
    Replacing old entries with the new ones.  The main use of
    this function is to update arxiv version of articles.

    Parameters
    ----------
    update_keys: Bool
        If True, attempt to update keys of entries that were updated
        from arxiv to published versions.
    """
    if base is None:
        bibs = bm.load()
    else:
        bibs = base

    keys     = [bib.key     for bib in bibs if bib.bibcode is not None]
    bibcodes = [bib.bibcode for bib in bibs if bib.bibcode is not None]
    eprints  = [bib.eprint  for bib in bibs if bib.bibcode is not None]
    dois     = [bib.doi     for bib in bibs if bib.bibcode is not None]
    # Querry-replace:
    bibs = add_bibtex(bibcodes, keys, eprints, dois, update_keys, base=base)
    return bibs


def key_update(key, bibcode, alternate_bibcode):
    r"""
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
    """
    old_year = alternate_bibcode[0:4]
    year = bibcode[0:4]
    # Update year:
    if old_year != year and old_year in key:
        key = key.replace(old_year, year, 1)

    # Update journal:
    journal = bibcode[4:9].replace('.','').replace('&','').lower()
    # Search for the word 'arxiv' in key:
    ijournal = key.lower().find('arxiv')
    if ijournal >= 0:
        key = "".join([key[:ijournal], journal, key[ijournal+5:]])

    return key
