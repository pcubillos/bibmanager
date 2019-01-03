# Copyright (c) 2018-2019 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = ['manager', 'search', 'display', 'add_bibtex', 'update']

import os
import re
import json
import requests
import urllib
import textwrap
import pickle

import bib_manager    as bm
import config_manager as cm
from utils import BM_CACHE, BOLD, END, BANNER, ignored, parse_name, get_authors


# FINDME: Is to possible to check a token is valid?
token = cm.get('ads_token')
rows  = int(cm.get('ads_display'))

ADSQUERRY = "https://api.adsabs.harvard.edu/v1/search/query?"
ADSEXPORT = "https://api.adsabs.harvard.edu/v1/export/bibtex"
ADSURL    = "https://ui.adsabs.harvard.edu/\#abs/"


def manager(querry=None):
  """
  A manager, it doesn't really do anything, it just delegates.
  """
  if querry is None and not os.path.exists(BM_CACHE):
      print("There are no more entries for this querry.")
      return

  if querry is None:
      with open(BM_CACHE, 'rb') as handle:
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
      with ignored(OSError):
          os.remove(BM_CACHE)
  else:
      with open(BM_CACHE, 'wb') as handle:
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
  rows: Integer
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
  >>> import ads_manager as am
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
  querry = urllib.parse.quote(querry)
  r = requests.get(f'{ADSQUERRY}q={querry}&start={start}&rows={cache_rows}'
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
  >>> import ads_manager as am
  >>> start = index = 0
  >>> querry = 'author:"^cubillos, p" property:refereed'
  >>> results, nmatch = am.search(querry, start=start)
  >>> display(results, start, index, rows, nmatch)
  """
  wrap_kw = {'width':76, 'subsequent_indent':"    "}
  for result in results[index-start:index-start+rows]:
      title = textwrap.fill(f"Title: {result['title'][0]}", **wrap_kw)
      author_list = [parse_name(author) for author in result['author']]
      authors = textwrap.fill(f"Authors: {get_authors(author_list, short)}",
           **wrap_kw)
      adsurl = f"adsurl: {ADSURL}{result['bibcode']}"
      bibcode = f"\n{BOLD}bibcode{END}: {result['bibcode']}"
      print(f"\n{title}\n{authors}\n{adsurl}{bibcode}")
  if index + rows < nmatch:
      more = "  To show the next set, execute:\nbibm ads-search"
  else:
      more = ""
  print(f"\nShowing entries {index+1}--{min(index+rows, nmatch)} out of "
        f"{nmatch} matches.{more}")


def add_bibtex(input_bibcodes, input_keys):
  """
  Add bibtex entries from a list of ADS bibcodes, with specified keys.
  New entries will replace old ones without asking if they are
  duplicates.

  Parameters
  ----------
  bibcodes: List of strings
     A list of ADS bibcodes.
  keys: List of strings
     BibTeX keys to assign to each bibcode.

  Examples
  --------
  >>> import ads_manager as am
  >>> # A successful add call:
  >>> bibcodes = ['1925PhDT.........1P']
  >>> keys = ['Payne1925phdStellarAtmospheres']
  >>> am.add_bibtex(bibcodes, keys)
  >>> # A failing add call:
  >>> bibcodes = ['1925PhDT....X....1P']
  >>> am.add_bibtex(bibcodes, keys)
  Error, there were no entries found for the input bibcode(s).

  >>> # A successful add call with multiple entries:
  >>> bibcodes = ['1925PhDT.........1P', '2018MNRAS.481.5286F']
  >>> keys = ['Payne1925phdStellarAtmospheres', 'FolsomEtal2018mnrasHD219134']
  >>> am.add_bibtex(bibcodes, keys)
  >>> # A partially failing call will still add those that succeed:
  >>> bibcodes = ['1925PhDT.....X...1P', '2018MNRAS.481.5286F']
  >>> am.add_bibtex(bibcodes, keys)
  Warning: bibcode '1925PhDT.....X...1P' not found.
  """
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
      print("\nError, there were no entries found for the input bibcode(s).")
      return

  # Keep counts of things:
  nfound = int(resp['msg'].split()[1])
  nreqs  = len(bibcodes)

  # Split output into separate BibTeX entries (keep as strings):
  results = resp["export"].strip().split("\n\n")

  new_bibs = ""
  # Match results to bibcodes,keys:
  for result in reversed(results):
      rkey = result[result.index('{')+1:result.index(',')]
      # Output bibcode is input bibcode:
      if rkey in bibcodes:
          ibib = bibcodes.index(rkey)
          new_bibs += "\n\n" + result.replace(rkey, keys[ibib], 1)
          bibcodes.pop(ibib)
          keys.pop(ibib)
          results.remove(result)
          continue
      # Else, check for arxiv updates in remaining bibcodes:
      if 'eprint' in result:
          eprint = re.findall('eprint.*[^{]{(.*)},', result)[0]
          if len(eprint) == 10:
              eprint = eprint.replace(".", "")
          for bibcode in bibcodes:
              if 'arXiv' in bibcode and eprint in bibcode:
                  ibib = bibcodes.index(bibcode)
                  #new_key = key_update(keys[ibib], rkey, bibcode)
                  new_bibs += "\n\n"+result.replace(rkey, keys[ibib], 1)
                  bibcodes.pop(ibib)
                  keys.pop(ibib)
                  results.remove(result)
                  break

  # Warnings:
  if nfound < nreqs or len(results) > 0:
      warning = BANNER + "Warning:\n"
      # bibcodes not found
      if nfound < nreqs:
          warning += '\nThere were bibcodes not found:\n - '
          warning += '\n - '.join(bibcodes) + "\n"
      # bibcodes not matched:
      if len(results) > 0:
          warning += '\nThere were results not mached to input bibcodes:\n\n'
          warning += '\n\n'.join(results) + "\n"
      warning += BANNER
      print(warning)

  # Add to bibmanager database:
  new = bm.loadfile(text=new_bibs)
  bm.merge(new=new, take='new')
  print('(Not counting updated references)')


def update():
  """
  Do an ADS querry by bibcode for all entries that have an adsurl
  field.  Replacing old entries with the new ones.  The main use of
  this function is to update arxiv version of articles.
  """
  bibs = bm.load()
  keys    = [bib.key    for bib in bibs if bib.adsurl is not None]
  adsurls = [bib.adsurl for bib in bibs if bib.adsurl is not None]
  # Get bibcode from adsurl, un-code UTF-8, and remove backslashes:
  bibcodes = [urllib.parse.unquote(os.path.split(adsurl)[1]).replace('\\','')
              for adsurl in adsurls]
  # Querry-replace:
  add_bibtex(bibcodes, keys)

