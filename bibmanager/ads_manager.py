# Copyright (c) 2018-2019 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = ['search', 'display']

import os
import json
import requests
import urllib
import textwrap
import pickle

import config_manager as cm
from utils import BM_CACHE, BOLD, END, ignored, parse_name, get_authors


# FINDME: Is to possible to check a token is valid?
token = 'Bearer ' + cm.get('ads_token')

ADSQUERRY = "https://api.adsabs.harvard.edu/v1/search/query?"
ADSEXPORT = "https://api.adsabs.harvard.edu/v1/export/bibtex"
ADSURL    = "https://ui.adsabs.harvard.edu//#abs/"


def manager(querry=None):
  """
  A manager, it doesn't really do anything, it just delegates.
  """
  if querry is None:
      results, querry, start, index, nmatch = read_cache()
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
      with ignored:
          os.remove(BM_CACHE)
  else:
      cache(results, querry, start, index, nmatch)


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


def cache(results, istart, index, nmatch):
  """
  Cache the current set of results returned by am.search(), the index
  of the last entry shown to the user, and the total number of entries
  matched by the search call.

  Parameters
  ----------
  querry: String
     I guess I don't need this
  results: List of dicts
     The output list of entries returned by a am.search() call.
  nmatch: Integer
     Total number of entries matched by the querry/search.
  """
  # New cache:
  if istart == 0:
      with open(BM_CACHE, 'wb') as handle:
          pickle.dump([results, istart, index, nmatch], handle,
                      protocol=pickle.HIGHEST_PROTOCOL)
  # Append to existing cache:
  else:
      # load previous cache
      with open(BM_CACHE, 'rb') as handle:
          old_results, dummy, old_index, dummy = pickle.load(handle)
      # keep from index to end
      # prepend to results
      results = old_results[index:] + results
      # save
      with open(BM_CACHE, 'wb') as handle:
          pickle.dump([results, index, index, nmatch], handle,
                      protocol=pickle.HIGHEST_PROTOCOL)


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
  wrap_kw = {'width':80, 'subsequent_indent':"    "}
  last = start + len(results)
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
  print(f"\nShowing entries {index+1}--{min(index+1+rows, nmatch)} out of "
        f"{nmatch} entries matched.{more}")


def get_bibtex():
  """
  Get bibtex entry for a given bibcode:
  """
  bibcode = {"bibcode":["2013arXiv1305.6548A"]}
  r = requests.post("https://api.adsabs.harvard.edu/v1/export/bibtex",
                    headers={"Authorization": token,
                             "Content-type": "application/json"},
                    data=json.dumps(bibcode))
  print(r.json()["export"])
