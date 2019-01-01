import json
import requests
import urllib
import textwrap

import config_manager as cm

# FINDME: Is to possible to check a token is valid?
token = 'Bearer ' + cm.get('adstoken')
BOLD = '\033[1m'
END  = '\033[0m'

ADSQUERRY = "https://api.adsabs.harvard.edu/v1/search/query?"
ADSEXPORT = "https://api.adsabs.harvard.edu/v1/export/bibtex"
ADSURL    = "https://ui.adsabs.harvard.edu//#abs/"


def search(querry, start=0, rows=500, sort='pubdate+desc'):
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
  nentries: Integer
     Total number of entries matched by the querry.

  Resources
  ---------
  A comprehensive description of the querry format:
  - http://adsabs.github.io/help/search/
  Description of the querry parameters:
  - https://github.com/adsabs/adsabs-dev-api/blob/master/Search_API.ipynb

  Examples
  --------
  >>> # Search entries by author (note the need for double quotes,
  >>> # otherwise, the search might produce bogus results):
  >>> querry = 'author:"cubillos, p"'
  >>> results, nentries = am.search(querry)
  >>> # Search entries by first author:
  >>> querry = 'author:"^cubillos, p"'
  >>> # Combine search by first author and year:
  >>> querry = 'author:"^cubillos, p" year:2017'
  >>> # Restrict seach to article-type entries:
  >>> querry = 'author:"^cubillos, p" property:article'
  >>> # Restrict seach to peer-reviewed articles:
  >>> querry = 'author:"^cubillos, p" property:refereed'

  >>> # Attempt with invalid token:
  >>> results, nentries = am.search(querry)
  ValueError: Invalid ADS request: Unauthorized, check you have a valid ADS token.
  >>> # Attempt with invalid querry ('properties' instead of 'property'):
  >>> results, nentries = am.search('author:"^cubillos, p" properties:refereed')
  ValueError: Invalid ADS request:
  org.apache.solr.search.SyntaxError: org.apache.solr.common.SolrException: undefined field properties
  """
  querry = urllib.parse.quote(querry)
  r = requests.get(f'{ADSQUERRY}q={querry}&start={start}&rows={rows}'
                   f'&sort={sort}&fl=title,author,year,bibcode,pub',
                   headers={'Authorization': token})
  resp = r.json()
  if 'error' in resp:
      if resp['error'] == 'Unauthorized':
          raise ValueError(f"Invalid ADS request: {resp['error']}, "
                            "check you have a valid ADS token.")
      raise ValueError(f"Invalid ADS request:\n{resp['error']['msg']}.")

  nentries = resp['response']['numFound']
  results  = resp['response']['docs']

  return results, nentries


def display(results, start, nentries, short=True):
  """
  Show on the prompt a list of entries from an ADS search.
  """
  wrap_kw = {'width':80, 'subsequent_indent':"   "}
  for result in results:
      title = textwrap.fill(f"Title: {result['title'][0]}, {result['year']}",
          **wrap_kw)
      author_list = [bm.parse_name(author) for author in result['author']]
      authors = textwrap.fill(f"Authors: {bm.get_authors(author_list, short)}",
           **wrap_kw)
      adsurl = f"adsurl: {ADSURL}{result['bibcode']}"
      bibcode = f"\n{BOLD}bibcode{END}: {result['bibcode']}"
      print(f"\n{title}\n{authors}\n{adsurl}{bibcode}")
  if start+len(results) < nentries:
      more = "  To show the next set, execute:\nbibm ads-search"
  else:
      more = ""
  if rows < nentries:
      print(f"\nShowing entries {start}--{start+len(results)} out of "
            f"{nentries} entries.{more}")


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
