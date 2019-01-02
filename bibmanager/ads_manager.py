# Copyright (c) 2018-2019 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = ['manager', 'search', 'display', 'add_bibtex']

import os
import json
import requests
import urllib
import textwrap
import pickle

import bib_manager    as bm
import config_manager as cm
from utils import BM_CACHE, BOLD, END, ignored, parse_name, get_authors


# FINDME: Is to possible to check a token is valid?
token = 'Bearer ' + cm.get('ads_token')
rows = int(cm.get('ads_display'))

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
                   headers={'Authorization': token})
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


def add_bibtex(bibcodes, keys):
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
  # Make request:
  r = requests.post("https://api.adsabs.harvard.edu/v1/export/bibtex",
                    headers={"Authorization": token,
                             "Content-type": "application/json"},
                    data=json.dumps({"bibcode":bibcodes}))
  resp = r.json()

  # No valid outputs:
  if 'error' in resp:
      print("\nError, there were no entries found for the input bibcode(s).")
      return
  # Output is a single string containing all BibTeX entries.
  bibtexs = r.json()["export"]

  # Replace ADS key with user-defined key:
  for bibcode,key in zip(bibcodes, keys):
      if bibtexs.find(bibcode) < 1:
          print(f"Warning: bibcode '{bibcode}' not found.")
      else:
          bibtexs = bibtexs.replace(bibcode, key, 1)

  # Add to bibmanager database:
  new = bm.loadfile(text=bibtexs)
  bm.merge(new=new, take='new')
