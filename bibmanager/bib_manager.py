# Copyright (c) 2018 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = ['Bib', 'search', 'loadfile', 'display_bibs',
           'init', 'merge', 'edit', 'add_entries', 'export',
           'load', 'save']

import os
import sys
import re
import requests
import json
import pickle
import subprocess
import prompt_toolkit
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import print_formatted_text
import pygments
from pygments.token import Token
from pygments.lexers.bibtex import BibTeXLexer
from pygments.styles.autumn import AutumnStyle
#import importlib
import numpy as np
from collections import namedtuple


# IO definitions (put these into a setup/config file?):
bm_home = os.path.expanduser("~") + "/.bibmanager/"
bm_bibliography = "bibliography.pickle"
lexer = prompt_toolkit.lexers.PygmentsLexer(BibTeXLexer)
style = prompt_toolkit.styles.style_from_pygments_cls(AutumnStyle)


# Some definitions:
Author      = namedtuple("Author",      "last first von jr")
Sort_author = namedtuple("Sort_author", "last first von jr year month")
months  = {"jan":1, "feb":2, "mar":3, "apr": 4, "may": 5, "jun":6,
           "jul":7, "aug":8, "sep":9, "oct":10, "nov":11, "dec":12}

banner = "\n" + ":"*70 + "\n"


def ordinal(number):
  """
  Get ordinal string representation for input number(s).

  Parameters
  ----------
  number: Integer or 1D integer ndarray
     An integer or array of integers.

  Returns
  -------
  ord: String or List of strings
     Ordinal representation of input number(s).  Return a string if
     input is int; else, return a list of strings.

  Examples
  --------
  >>> import bibm as bm
  >>> print(bm.ordinal(1))
  1st
  >>> print(bm.ordinal(2))
  2nd
  >>> print(bm.ordinal(11))
  11th
  >>> print(bm.ordinal(111))
  111th
  >>> print(bm.ordinal(121))
  121st
  >>> print(bm.ordinal(np.arange(1,6)))
  ['1st', '2nd', '3rd', '4th', '5th']
  """
  ending = ["th", "st", "nd", "rd"]
  unit = number % 10
  teen = (number//10) % 10 != 1
  idx = unit * (unit<4) * teen
  if type(number) is int:
    return "{:d}{:s}".format(number, ending[idx])
  return ["{:d}{:s}".format(n, ending[i]) for n,i in zip(number,idx)]


def count(text):
  """
  Count net number of braces in text (add 1 for each opening brace,
  subtract one for each closing brace).

  Parameters
  ----------
  text: String
     A string.

  Returns
  -------
  counts: Integer
     Net number of braces.

  Examples
  --------
  >>> import bibm as bm
  >>> bm.count('{Hello} world')
  0
  """
  return text.count("{") - text.count("}")


def nest(text):
  r"""
  Get braces nesting level for each character in text.

  Parameters
  ----------
  text: String
     String to inspect.

  Returns
  -------
  counts: 1D integer list
     Braces nesting level for each character.

  Examples
  --------
  >>> import bibm as bm
  >>> s = "{{P\\'erez}, F. and {Granger}, B.~E.},"
  >>> n = bm.nest(s)
  >>> print("{:s}\n{:s}".format(s, "".join([str(v) for v in n])))
  {{P\'erez}, F. and {Granger}, B.~E.},
  0122222222111111111122222222111111110
  """
  counts = np.zeros(len(text), int)
  for i,s in enumerate(text[:-1]):
    if s == "{":
      counts[i+1] = counts[i] + 1
    elif s == "}":
      counts[i+1] = counts[i] - 1
    else:
      counts[i+1] = counts[i]
  return counts


def cond_split(text, pattern, nested=None, nlev=-1, ret_nests=False):
  r"""
  Conditional find and split strings in a text delimited by all
  occurrences of pattern where the brace-nested level is nlev.

  Parameters
  ----------
  text: String
     String where to search for pattern.
  pattern: String
     A regex pattern to search.
  nested: 1D integer iterable
     Braces nesting level of characters in text.
  nlev: Integer
     Required nested level to accept pattern match.
  ret_nests: Bool
     If True, return a list with the arrays of nested level for each
     of the returned substrings.

  Returns
  -------
  substrings: List of strings
     List of strings delimited by the accepted pattern matches.
  nests: List of integer ndarrays [optional]
     nested level for substrings.

  Examples
  --------
  >>> import bibm as bm
  >>> # Split an author list string delimited by ' and ' pattern:
  >>> bm.cond_split("{P\\'erez}, F. and {Granger}, B.~E.", " and ")
  ["{P\\'erez}, F.", '{Granger}, B.~E.']
  >>> # Protected instances (within braces) won't count:
  >>> bm.cond_split("{AAS and Astropy Teams} and {Hendrickson}, A.", " and ")
  ['{AAS and Astropy Teams}', '{Hendrickson}, A.']
  >>> # Matches at the beginning or end do not count for split:
  >>> bm.cond_split(",Jones, Oliphant, Peterson,", ",")
  ['Jones', ' Oliphant', ' Peterson']
  >>> # But two consecutive matches do return an empty string:
  >>> bm.cond_split("Jones,, Peterson", ",")
  ['Jones', '', ' Peterson']
  """
  if nested is None:
    nested = nest(text)

  if nlev == -1 and len(nested) > 0:
    nlev = nested[0]

  # First and last indices of each pattern match:
  bounds = [(m.start(0), m.end(0))
            for m in re.finditer(pattern, text)
            if nested[m.start(0)] == nlev]

  flat_bounds = [item for sublist in bounds for item in sublist]

  # No matches:
  if len(flat_bounds) == 0:
    if ret_nests:
      return [text], [nested]
    return [text]

  # Matches, parse substrings:
  if flat_bounds[0] != 0:
    flat_bounds.insert(0, 0)
  else:
    flat_bounds.pop(0)
  if flat_bounds[-1] != len(text):
    flat_bounds.append(len(text))
  pairs = zip(*([iter(flat_bounds)]*2))
  substrings = [text[start:end] for (start,end) in pairs]
  if ret_nests:
    pairs = zip(*([iter(flat_bounds)]*2))
    nests = [nested[start:end] for (start,end) in pairs]
    return substrings, nests
  return substrings


def cond_next(text, pattern, nested, nlev=1):
  """
  Find next instance of pattern in text where nested is nlev.

  Parameters
  ----------
  text: String
     Text where to search for regex.
  pattern: String
     Regular expression to search for.
  nested: 1D integer iterable
     Braces-nesting level of characters in text.
  nlev: Integer
     Requested nested level.

  Returns
  -------
     Index integer of pattern in text.  If not found, return the
     index of the last character in text.

  Examples
  --------
  >>> import bibm as bm
  >>> text = '"{{HITEMP}, the high-temperature molecular database}",'
  >>> nested = bm.nest(text)
  >>> # Ignore comma within braces:
  >>> bm.cond_next(text, ",", nested, nlev=0)
  53
  """
  for m in re.finditer(pattern, text):
    if nested[m.start(0)] == nlev:
      return m.start(0)
  # If not found, return last index in text:
  return len(text) - 1


#@functools.lru_cache(maxsize=1024, typed=False)
def parse_name(name, nested=None):
  r"""
  Parse first, last, von, and jr parts from a name, following these rules:
  http://mirror.easyname.at/ctan/info/bibtex/tamethebeast/ttb_en.pdf
  Page 23.

  Parameters
  ----------
  name: String
     A name following the BibTeX format.
  nested: 1D integer ndarray
     Nested level of characters in name.

  Returns
  -------
  author: Author namedtuple
     Four element tuple with the parsed name.

  Examples
  --------
  >>> import bib_manager as bm
  >>> bm.parse_name('{Hendrickson}, A.')
  Author(last='{Hendrickson}', first='A.', von='', jr='')
  >>> bm.parse_name('Eric Jones')
  Author(last='Jones', first='Eric', von='', jr='')
  >>> bm.parse_name('{AAS Journals Team}')
  Author(last='{AAS Journals Team}', first='', von='', jr='')
  >>> bm.parse_name("St{\\'{e}}fan van der Walt")
  Author(last='Walt', first="St{\\'{e}}fan", von='van der', jr='')
  """
  if nested is None:
    nested = nest(name)
  name = " ".join(cond_split(name, "~", nested=nested))
  fields, nests = cond_split(name, ",", nested=nested, ret_nests=True)
  if len(fields) > 3:
    raise ValueError("Invalid BibTeX format for author '{:s}'.".format(name))

  # 'First von Last' format:
  if len(fields) == 1:
    jr = ""
    words = cond_split(name, " ", nested=nested)
    lowers = [s[0].islower() for s in words[:-1]]
    if np.any(lowers):
      ifirst = np.min(np.where(lowers))
      ilast  = np.max(np.where(lowers)) + 1
    else:
      ifirst = ilast = len(words) - 1
    first = " ".join(words[0:ifirst])
    von   = " ".join(words[ifirst:ilast])
    last  = " ".join(words[ilast:])

  else:
    istart = next_char(fields[0])
    iend   = last_char(fields[0])
    vonlast = fields[0][istart:iend]
    nested  = nests [0][istart:iend]
    if vonlast.strip() == "":
      raise ValueError("Invalid BibTeX format for author '{:s}', it "
                       "does not have a last name.".format(name))

    # 'von Last, First' format:
    if len(fields) == 2:
      jr = ""
      first = fields[1].strip()

    # 'von Last, Jr, First' format:
    elif len(fields) == 3:
      jr    = fields[1].strip()
      first = fields[2].strip()

    words = cond_split(vonlast, " ", nested=nested)
    lowers = [s[0].islower() for s in words[:-1]]

    if np.any(lowers):
      ilast = np.max(np.where(lowers)) + 1
      von = " ".join(words[:ilast])
    else:
      von = ""
      ilast = 0
    last = " ".join(words[ilast:])

  return Author(last=last, first=first, von=von, jr=jr)


#@functools.lru_cache(maxsize=1024, typed=False)
def purify(name, german=False):
  r"""
  Replace accented characters closely following these rules:
  https://tex.stackexchange.com/questions/57743/
  For a more complete list of special characters, see Table 2.2 of
  'The Not so Short Introduction to LaTeX2e' by Oetiker et al. (2008).

  Parameters
  ----------
  name: String
     Name to be 'purified'.
  german: Bool
     Replace umlaut with german style (append 'e' after).

  Returns
  -------
  Lower-cased name without accent characters.

  Examples
  --------
  >>> import bibm as bm
  >>> names = ["St{\\'{e}}fan",
               "{{\\v S}ime{\\v c}kov{\\'a}}",
               "{AAS Journals Team}",
               "Kov{\\'a}{\\v r}{\\'i}k",
               "Jarom{\\'i}r Kov{\\'a\\v r\\'i}k",
               "{\\.I}volgin",
               "Gon{\\c c}alez Nu{\~n}ez",
               "Knausg{\\aa}rd Sm{\\o}rrebr{\\o}d",
               'Schr{\\"o}dinger Be{\\ss}er']

  >>> for name in names:
  >>>     print("{:36s}".format(repr(name)), bm.purify(name))
  "St{\\'{e}}fan"                      stefan
  "{{\\v S}ime{\\v c}kov{\\'a}}"       simeckova
  '{AAS Journals Team}'                aas journals team
  "Kov{\\'a}{\\v r}{\\'i}k"            kovarik
  "Jarom{\\'i}r Kov{\\'a\\v r\\'i}k"   jaromir kovarik
  '{\\.I}volgin'                       ivolgin
  'Gon{\\c c}alez Nu{\\~n}ez'          goncalez nunez
  'Knausg{\\aa}rd Sm{\\o}rrebr{\\o}d'  knausgaard smorrebrod
  'Schr{\\"o}dinger Be{\\ss}er'        schrodinger besser
  """
  # German umlaut replace:
  if german:
    for pattern in ["a", "o", "u"]:
      name = re.sub(r'\\"{:s}'.format(pattern), pattern+"e", name)
  # Remove special:
  name = re.sub(r"\\(\"|\^|`|\.|'|~)", "", name)
  # Remove special + white space:
  name = re.sub(r"\\(c |u |H |v |d |b |t )", "", name)
  # Replace pattern:
  for pattern in ["o", "O", "l", "L", "i", "j",
                  "aa", "AA", "AE", "oe", "OE", "ss"]:
    name = re.sub(r"\\{:s}".format(pattern), pattern, name)
  # Remove braces, clean up, and return:
  return re.sub("({|})", "", name).strip().lower()


def initials(name):
  r"""
  Get initials from a name.

  Parameters
  ----------
  name: String
     A name.

  Returns
  -------
  initials: String
     Name initials (lower cased).

  Examples
  --------
  >>> import bibm as bm
  >>> names = ["",
               "D.",
               "D. W.",
               "G.O.",
               '{\\"O}. H.',
               "J. Y.-K.",
               "Phil",
               "Phill Henry Scott"]
  >>> for name in names:
  >>>   print("{:20s}: {:s}".format(repr(name), repr(bm.initials(name))))
  ''                  : ''
  'D.'                : 'd'
  'D. W.'             : 'dw'
  'G.O.'              : 'g'
  '{\\"O}. H.'        : 'oh'
  'J. Y.-K.'          : 'jyk'
  'Phil'              : 'p'
  'Phill Henry Scott' : 'phs'
  >>> # 'G.O.' is a typo by the user, should have had a blank in between.
  """
  name = purify(name)
  split_names = name.replace("-", " ").split()
  # Somehow string[0:1] does not break when string = "", unlike string[0].
  return "".join([name[0:1] for name in split_names])


def next_char(text):
  r"""
  Get index of next non-blank character in string text.
  Return zero if all characters are blanks.

  Parameters
  ----------
  text: String
     A string, duh!.

  Examples
  --------
  >>> import bibm as bm
  >>> texts = ["Hello", "  Hello", "  Hello ", "", "\n Hello", "  "]
  >>> for text in texts:
  >>>     print("{:11s}: {:d}".format(repr(text), bm.next_char(text)))
  'Hello'    : 0
  '  Hello'  : 2
  '  Hello ' : 2
  ''         : 0
  '\n Hello' : 2
  '  '       : 0
  """
  nchars = len(text)
  # Empty string:
  if nchars == 0:
    return 0
  i = 0
  while text[i].isspace():
    i += 1
    # Reach end of string, all characters blanks:
    if i == nchars:
      return 0
  return i


def last_char(text):
  r"""
  Get index of last non-blank character in string text.

  Parameters
  ----------
  text: String
     A string, duh!.

  Examples
  --------
  >>> import bibm as bm
  >>> texts = ["Hello", "  Hello", "  Hello  ", "", "\n Hello", "  "]
  >>> for text in texts:
  >>>     print("{:12s}: {:d}".format(repr(text), bm.last_char(text)))
  'Hello'     : 5
  '  Hello'   : 7
  '  Hello  ' : 7
  ''          : 0
  '\n Hello'  : 7
  '  '        : 0
  """
  i = len(text)
  if i == 0:
    return 0
  while text[i-1].isspace() and i>0:
    i -= 1
  return i


def get_fields(entry):
  r"""
  Generator to parse entries of a bibbliographic entry.

  Parameters
  ----------
  entry: String
     A bibliographic entry text.

  Yields
  ------
  The first yield is the entry's key.  All following yields are
  three-element tuples containing a field name, field value, and
  nested level of the field value.

  Notes
  -----
  Global quotations or braces on a value are removed before yielding.

  Example
  -------
  >>> import bibm as bm
  >>> entry = '''@Article{Hunter2007ieeeMatplotlib,
                   Author    = {{Hunter}, J. D.},
                   Title     = {Matplotlib: A 2D graphics environment},
                   Journal   = {Computing In Science \& Engineering},
                   Volume    = {9},
                   Number    = {3},
                   Pages     = {90--95},
                   publisher = {IEEE COMPUTER SOC},
                   doi       = {10.1109/MCSE.2007.55},
                   year      = 2007
                 }'''
  >>> fields = bm.get_fields(entry)
  >>> # Get the entry's key:
  >>> print(next(fields))
  Hunter2007ieeeMatplotlib
  >>> # Now get the fields, values, and nested level:
  >>> for key, value, nested in fields:
  >>>     print("{:9s}: {:s}\n{:11s}{:s}".format(key, value,
  >>>           "", "".join([str(v) for v in nested])))
  author   : {Hunter}, J. D.
             233333332222222
  title    : Matplotlib: A 2D graphics environment
             2222222222222222222222222222222222222
  journal  : Computing In Science \& Engineering
             22222222222222222222222222222222222
  volume   : 9
             2
  number   : 3
             2
  pages    : 90--95
             222222
  publisher: IEEE COMPUTER SOC
             22222222222222222
  doi      : 10.1109/MCSE.2007.55
             22222222222222222222
  year     : 2007
             1111
  """
  # First yield is the key:
  nested = list(nest(entry))
  start = nested.index(1)
  loc   = entry.index(",")
  yield entry[start:loc]
  loc += 1

  # Next equal sign delimits key:
  while entry[loc:].find("=") >= 0:
    eq  = entry[loc:].find("=")
    key = entry[loc:loc+eq].strip().lower()
    # next non-blank character:
    start = loc + eq + 1 + next_char(entry[loc+eq+1:])

    if entry[start] == "{":
      end = start + nested[start+1:].index(1)
      start += 1
    elif entry[start] == '"':
      start += 1
      end = start + cond_next(entry[start:], '"', nested[start:], nlev=1)
    else:
      end = start + cond_next(entry[start:], ",", nested[start:], nlev=1)
    start += next_char(entry[start:end])
    end = start + last_char(entry[start:end])
    loc = end + np.clip(entry[end:].find(","), 0, len(entry)) + 1
    yield key, entry[start:end], nested[start:end]


class Bib(object):
  """
  Bibliographic-entry object.
  """
  def __init__(self, entry):
    """
    Create a Bib() object from given entry.  Minimally, entries must
    contain the author, title, and year keys.

    Parameters
    ----------
    entry: String
       A bibliographic entry text.

    Example
    -------
    >>> import bib_manager as bm
    >>> entry = '''@Misc{JonesEtal2001scipy,
              author = {Eric Jones and Travis Oliphant and Pearu Peterson},
              title  = {{SciPy}: Open source scientific tools for {Python}},
              year   = {2001},
            }'''
    >>> bib = bm.Bib(entry)
    >>> print(bib.title)
    SciPy: Open source scientific tools for Python
    >>> for author in bib.authors:
    >>>    print(author)
    Author(last='Jones', first='Eric', von='', jr='')
    Author(last='Oliphant', first='Travis', von='', jr='')
    Author(last='Peterson', first='Pearu', von='', jr='')
    >>> print(bib.sort_author)
    Sort_author(last='jones', first='e', von='', jr='', year=2001, month=13)
    """
    self.content  = entry
    # Defaults:
    self.month    = 13
    self.adsurl   = None
    self.doi      = None
    self.eprint   = None
    self.isbn     = None

    fields = get_fields(self.content)
    self.key = next(fields)

    for key, value, nested in fields:
      if key == "title":
        # Title with no braces, tabs, nor linebreak and corrected blanks:
        self.title = " ".join(re.sub("({|})", "", value).split())

      elif key == "author":
        # Parse authors finding all non-brace-nested 'and' instances:
        authors, nests = cond_split(value.replace("\n"," "), " and ",
                            nested=nested, ret_nests=True)
        self.authors = [parse_name(author, nested)
                        for author,nested in zip(authors,nests)]

      elif key == "year":
        r = re.search('[0-9]{4}', value)
        self.year = int(r.group(0))

      elif key == "month":
        value = value.lower().strip()
        self.month = months[value[0:3]]

      elif key == "doi":
        self.doi = value

      elif key == "adsurl":
        self.adsurl = value

      elif key == "eprint":
        self.eprint = value

      elif key == "isbn":
        self.isbn = value.lower().strip()

    for attr in ['authors', 'title', 'year']:
      if not hasattr(self, attr):
        raise ValueError("Bibtex entry '{:s}' has no author, title, or year.".
                         format(self.key))
    # First-author fields used for sorting:
    # Note this differs from Author[0], since fields are 'purified',
    # and 'first' goes only by initials().
    self.sort_author = Sort_author(purify(self.authors[0].last),
                                   initials(self.authors[0].first),
                                   purify(self.authors[0].von),
                                   purify(self.authors[0].jr),
                                   self.year,
                                   self.month)

  def __repr__(self):
    return self.content

  def __contains__(self, author):
    r"""
    Check if given author is in the author list of this bib entry.
    If the 'author' string begins with the '^' character, match
    only against the first author.

    Parameters
    ----------
    author: String
       An author name in a valid BibTeX format.

    Example
    -------
    >>> import bibm as bm
    >>> bib = bm.Bib('''@ARTICLE{DoeEtal2020,
                    author = {{Doe}, J. and {Perez}, J. and {Dupont}, J.},
                     title = "What Have the Astromomers ever Done for Us?",
                   journal = {\apj},
                      year = 2020,}''')
    >>> # Check for first author:
    >>> 'Doe, J' in bib
    True
    >>> # Format doesn't matter, as long as it is a valid format:
    >>> 'John Doe' in bib
    True
    >>> # Neglecting first's initials still match:
    >>> 'Doe' in bib
    True
    >>> # But, non-matching initials wont match:
    >>> 'Doe, K.' in bib
    False
    >>> # Match against first author only if string begins with '^':
    >>> '^Doe' in bib
    True
    >>> '^Perez' in bib
    False
    """
    # Check first-author mark:
    if author[0:1] == '^':
        author = author[1:]
        authors = [self.authors[0]]
    else:
        authors = self.authors
    # Parse and purify input author name:
    author = parse_name(author)
    first = initials(author.first)
    von   = purify(author.von)
    last  = purify(author.last)
    jr    = purify(author.jr)
    # Remove non-matching authors by each non-empty field:
    if len(jr) > 0:
        authors = [author for author in authors if jr  == purify(author.jr)]
    if len(von) > 0:
        authors = [author for author in authors if von == purify(author.von)]
    if len(first) > 0:
        authors = [author for author in authors
                   if first == initials(author.first)[0:len(first)]]
    authors = [author for author in authors if last == purify(author.last)]
    return len(authors) >= 1

  # https://docs.python.org/3.6/library/stdtypes.html
  def __lt__(self, other):
    """
    Evaluate sequentially according to sort_author's fields: last,
    first, von, and jr, year, and month.  If any of these
    fields are equal, go on to next field to compare.
    """
    s, o = self.sort_author, other.sort_author
    if s.last != o.last:
      return s.last < o.last
    if len(s.first)==1 or len(o.first) == 1:
      if s.first[0:1] != o.first[0:1]:
        return s.first < o.first
    else:
      if s.first != o.first:
        return s.first < o.first
    if s.von != o.von:
      return s.von < o.von
    if s.jr != o.jr:
      return s.jr < o.jr
    if s.year != o.year:
      return s.year < o.year
    return s.month < o.month

  def __eq__(self, other):
    """
    Check whether self and other have same sort_author (first author)
    and year/month.
    Evaluate to equal by first initial if one entry has less initials
    than the other.
    """
    if len(self.sort_author.first)==1 or len(other.sort_author.first)==1:
      first = self.sort_author.first[0:1] == other.sort_author.first[0:1]
    else:
      first = self.sort_author.first == other.sort_author.first

    return (self.sort_author.last  == other.sort_author.last
        and first
        and self.sort_author.von   == other.sort_author.von
        and self.sort_author.jr    == other.sort_author.jr
        and self.sort_author.year  == other.sort_author.year
        and self.sort_author.month == other.sort_author.month)

  def __le__(self, other):
    return self.__lt__(other) or self.__eq__(other)

  def published(self):
    """
    Published status according to ADSURL field:
       Return -1 if adsurl is None.
       Return  0 if adsurl is arXiv.
       Return  1 if adsurl is peer-reviewed journal.
    """
    if self.adsurl is None:
      return -1
    return int(self.adsurl.find('arXiv') < 0)


def req_input(prompt, options):
  """
  Query for an aswer to prompt message until the user provides a
  valid input (i.e., answer is in options).

  Parameters
  ----------
  prompt: String
     Prompt text for input()'s argument.
  options: List
     List of options to accept.  Elements in list are casted into strings.

  Returns
  -------
  answer: String
     The user's input.

  Examples
  --------
  >>> import bibm as bm
  >>> bm.req_input('Enter number between 0 and 9: ', options=np.arange(10))
  >>> # Enter the number 10:
  Enter number between 0 and 9: 10
  >>> # Now enter the number 5:
  Not a valid input.  Try again: 5
  '5'
  """
  # Cast options as str:
  options = [str(option) for option in options]

  answer = input(prompt)
  while answer not in options:
    answer = input("Not a valid input.  Try again: ")
  return answer


def display_bibs(labels, bibs):
  r"""
  Display a list of bib entries on screen with flying colors.

  Parameters
  ----------
  labels: List of Strings
     Header labels to show above each Bib() entry.
  bibs: List of Bib() objects
     BibTeX entries to display.

  Examples
  --------
  >>> import bibm as bm
  >>> e1 = '''@Misc{JonesEtal2001scipy,
         author = {Eric Jones and Travis Oliphant and Pearu Peterson},
         title  = {{SciPy}: Open source scientific tools for {Python}},
         year   = {2001},
       }'''
  >>> e2 = '''@Misc{Jones2001,
         author = {Eric Jones and Travis Oliphant and Pearu Peterson},
         title  = {SciPy: Open source scientific tools for Python},
         year   = {2001},
       }'''
  >>> bibs = [bm.Bib(e1), bm.Bib(e2)]
  >>> bm.display_bibs(["DATABASE:\n", "NEW:\n"], bibs)
  ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
  DATABASE:
  @Misc{JonesEtal2001scipy,
         author = {Eric Jones and Travis Oliphant and Pearu Peterson},
         title  = {{SciPy}: Open source scientific tools for {Python}},
         year   = {2001},
       }

  NEW:
  @Misc{Jones2001,
         author = {Eric Jones and Travis Oliphant and Pearu Peterson},
         title  = {SciPy: Open source scientific tools for Python},
         year   = {2001},
       }
  """
  if labels is None:
      labels = ["" for _ in bibs]
  tokens = [(Token.Comment, banner)]
  for label,bib in zip(labels, bibs):
      tokens += [(Token.Text, label)]
      tokens += list(pygments.lex(bib.content, lexer=BibTeXLexer()))
      tokens += [(Token.Text, "\n")]
  # (Triming out final newline)
  print_formatted_text(PygmentsTokens(tokens[:-1]), style=style)


def remove_duplicates(bibs, field):
  """
  Look for duplicates (within a same list of entries) by field and remove them.

  Parameters
  ----------
  bibs: List of Bib() objects
     Entries to filter.
  field: String
     Field to use for filtering ('doi', 'isbn', 'adsurl', or 'eprint').
  """
  fieldlist = [getattr(bib,field) if getattr(bib,field) is not None else ""
               for bib in bibs]
  ubib, uinv, counts = np.unique(fieldlist, return_inverse=True,
                                 return_counts=True)
  multis = np.where(counts > 1)[0]

  # No duplicates:
  if len(multis[1:]) == 0:
    return

  removes = []
  for m in multis[1:]:
    all_indices = np.where(uinv == m)[0]
    entries = [bibs[i].content for i in all_indices]
    # Remove identical entries:
    uentries, uidx = np.unique(entries, return_index=True)
    indices = list(all_indices[uidx])
    removes += [idx for idx in all_indices if idx not in indices]
    nbibs = len(uentries)
    if nbibs == 1:
      continue
    # TBD: pick published over arxiv adsurl if that's the case

    labels = [idx + " ENTRY:\n" for idx in ordinal(np.arange(nbibs)+1)]
    display_bibs(labels, [bibs[i] for i in indices])
    s = req_input("Duplicate {:s} field, []keep first, [2]second, [3]third, "
         "etc.: ".format(field), options=[""]+list(np.arange(nbibs)+1))
    if s == "":
      indices.pop(0)
    else:
      indices.pop(int(s)-1)
    removes += indices

  for idx in reversed(sorted(removes)):
    bibs.pop(idx)


def filter_field(bibs, new, field, take):
  """
  Filter entries by field.  This routine modifies new removing the
  duplicates, and may modify bibs (depending on take argument).

  Parameters
  ----------
  bibs: List of Bib() objects
     Database entries.
  new: List of Bib() objects
     New entries to add.
  field: String
     Field to use for filtering.
  take: String
     Decision-making protocol to resolve conflicts when there are
     partially duplicated entries.
     'old': Take the database entry over new.
     'new': Take the new entry over the database.
     'ask': Ask user to decide (interactively).
  """
  fields = [getattr(e,field)  for e in bibs]
  removes = []
  for i,e in enumerate(new):
    if getattr(e,field) is None  or  getattr(e,field) not in fields:
      continue
    idx = fields.index(getattr(e,field))
    # Replace if duplicate and new has newer adsurl:
    if e.published() > bibs[idx].published():
      bibs[idx] = e
    # Look for different-key conflict:
    if e.key != bibs[idx].key:
      if take == "new":
        bibs[idx] = e
      elif take == "ask":
        display_bibs(["DATABASE:\n", "NEW:\n"], [bibs[idx], e])
        s = req_input("Duplicate {:s} field but different keys, []keep "
                      "database or take [n]ew: ".format(field),
                      options=["", "n"])
        if s == "n":
          bibs[idx] = e
    removes.append(i)
  for idx in reversed(sorted(removes)):
    new.pop(idx)


def loadfile2(bib):
  with open(bib, 'r') as f:
    text = f.read()

  nested = nest(text)

  bounds = [m.start(0)
            for m in re.finditer("@", text)
            if nested[m.start(0)] == 0]

  w = "TEMPLATES = { ('index.html', 'home')}, {('base.html', 'base')}"
  outer = re.compile("\{(.+)\}")
  m = outer.search(w)
  inner_str = m.group(1)


def loadfile(bibfile=None, text=None):
  """
  Create a list of Bib() objects from a .bib file.

  Parameters
  ----------
  bibfile: String
     Path to an existing .bib file.
  text: String
     Content of a .bib file (ignored if bibfile is not None).

  Examples
  --------
  >>> import bibm as bm
  >>> bibfile = "../examples/sample.bib"
  >>> bibs = bm.loadfile(bibfile)
  """
  entries = []  # Store Lists of bibtex entries
  entry   = []  # Store lines in the bibtex
  parcount = 0

  # Load a bib file:
  if bibfile is not None:
      f = open(bibfile, 'r')
  elif text is not None:
      f = text.splitlines()
  else:
      raise TypeError("Missing input arguments for loadfile(), at least "
                      "bibfile or text must be provided.")

  for i,line in enumerate(f):
      # New entry:
      if line.startswith("@") and parcount != 0:
          raise ValueError("Mismatched braces in line {:d}:\n'{:s}'.".
                           format(i,line.rstrip()))

      parcount += count(line)
      if parcount == 0 and entry == []:
          continue

      if parcount < 0:
          raise ValueError("Mismatched braces in line {:d}:\n'{:s}'".
                           format(i,line.rstrip()))

      entry.append(line.rstrip())

      if parcount == 0 and entry != []:
          entries.append("\n".join(entry))
          entry = []

  if bibfile is not None:
      f.close()

  if parcount != 0:
      raise ValueError("Invalid input, mistmatched braces at end of file.")

  bibs = [Bib(entry) for entry in entries]

  remove_duplicates(bibs, "doi")
  remove_duplicates(bibs, "isbn")
  remove_duplicates(bibs, "adsurl")
  remove_duplicates(bibs, "eprint")

  return sorted(bibs)


def merge(bibfile=None, new=None, take="old"):
  """
  Merge entries from a new bibfile into the bm database.

  Parameters
  ----------
  bibfile: String
     New .bib file to merge into the bibmanager database.
  new: List of Bib() objects
     List of new BibTeX entries (ignored if bibfile is not None).
  take: String
     Decision-making protocol to resolve conflicts when there are
     partially duplicated entries.
     'old': Take the database entry over new.
     'new': Take the new entry over the database.
     'ask': Ask user to decide (interactively).

  Examples
  --------
  >>> import bibm as bm
  >>> # Load bibmabager database (TBD: update with bm/examples/new.bib):
  >>> newbib = (os.path.expanduser("~")
                + "/Dropbox/latex/2018_hd209/current/hd209nuv.bib")
  >>> new  = bm.loadfile(newbib)
  >>> # Merge new into database:
  >>> bm.merge(newbib, take='old')
  """
  bibs = load()
  if bibfile is not None:
    new = loadfile(bibfile)
  if new is None:
    return

  # Filter duplicates by field:
  filter_field(bibs, new, "doi",    take)
  filter_field(bibs, new, "isbn",   take)
  filter_field(bibs, new, "adsurl", take)
  filter_field(bibs, new, "eprint", take)

  # Filter duplicate key:
  keep = np.zeros(len(new), bool)
  bm_keys = [e.key for e in bibs]
  for i,e in enumerate(new):
    if e.key not in bm_keys:
      keep[i] = True
      continue
    idx = bm_keys.index(e.key)
    if e.content == bibs[idx].content:
      continue # Duplicate, do not take
    else:
      display_bibs(["DATABASE:\n", "NEW:\n"], [bibs[idx], e])
      s = input("Duplicate key but content differ, []keep database, "
                "take [n]ew, or\nrename key of new entry: ".
                format(banner, bibs[idx].content, e.content))
      if s == "n":
        bibs[idx] = e
      elif s != "":
        new[i].key = s
        new[i].content.replace(e.key, s)
        keep[i] = True
  new = [e for e,keeper in zip(new,keep) if keeper]

  # Different key, same title:
  keep = np.zeros(len(new), bool)
  bm_titles = [e.title for e in bibs]
  for i,e in enumerate(new):
    if e.title not in bm_titles:
      keep[i] = True
      continue
    idx = bm_titles.index(e.title)
    # Printing the output of a pygments lexer.
    display_bibs(["DATABASE:\n", "NEW:\n"], [bibs[idx], e])
    s = req_input("Possible duplicate, same title but keys differ, []ignore "
                  "new, [r]eplace database with new, or [a]dd new: ",
                  options=["", "r", "a"])
    if s == "r":
      bibs[idx] = e
    elif s == "a":
      keep[i] = True
  new = [e for e,keeper in zip(new,keep) if keeper]

  # Add all new entries and sort:
  bibs = sorted(bibs + new)
  save(bibs)
  export(bibs)


def save(entries):
  """
  Save list of Bib() entries into bibmanager pickle database.

  Parameters
  ----------
  entries: List of Bib() objects
     bib files to store.

  Examples
  --------
  >>> import bibm as bm
  >>> # [Load some entries]
  >>> bm.save(entries)
  """
  # TBD: Don't pickle-save the Bib() objects directly, but store them
  #      as dict objects. (More standard / backward compatibility)
  with open(bm_home + bm_bibliography, 'wb') as handle:
    pickle.dump(entries, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load():
  """
  Load the bibmanager database of BibTeX entries.

  Returns
  -------
  List of Bib() entries.

  Examples
  --------
  >>> import bibm as bm
  >>> bibs = bm.load()
  """
  with open(bm_home + bm_bibliography, 'rb') as handle:
    return pickle.load(handle)


def export(entries, bibfile=bm_home+"bibmanager.bib"):
  """
  Export list of Bib() entries into a .bib file.

  Parameters
  ----------
  entries: List of Bib() objects
     Entries to export.
  bibfile: String
     Output .bib file name.
  """
  with open(bibfile, "w") as f:
    for e in entries:
      f.write(e.content)
      f.write("\n\n")


def init(bibfile=None):
  """
  Initialize database.

  Example
  -------
  >>> import bibm as bm
  >>> bibfile = '../examples/sample.bib'
  >>> bm.init(bibfile)
  """
  if not os.path.exists(bm_home):
    os.mkdir(bm_home)

  if bibfile is not None:
    bibs = loadfile(bibfile)
    # TBD: ask overwrite
    if bibs is not None:
      save(bibs)
      export(bibs)


def add_entries(take='ask'):
  """
  Manually add BibTeX entries through the prompt.

  Parameters
  ----------
  take: String
     Decision-making protocol to resolve conflicts when there are
     partially duplicated entries.
     'old': Take the database entry over new.
     'new': Take the new entry over the database.
     'ask': Ask user to decide (interactively).
  """
  newbibs = prompt_toolkit.prompt(
      "Enter a BibTeX entry (press META+ENTER or ESCAPE ENTER when done):\n",
      multiline=True, lexer=lexer, style=style)
  new = loadfile(text=newbibs)

  if len(new) == 0:
    print("No new entries to add.")
    return

  merge(new=new, take=take)


def edit():
  """
  Manually edit the bibfile database in text editor.

  Resources
  ---------
  https://stackoverflow.com/questions/17317219/
  https://docs.python.org/3.6/library/subprocess.html
  """
  temp_bib = bm_home + "tmp_bibmanager.bib"
  export(load(), temp_bib)
  # Open database.bib into temporary file with default text editor
  if sys.platform == "win32":
    os.startfile(temp_bib)
  else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, temp_bib])
  # Launch input() call to wait for user to save edits:
  dummy = input("Press ENTER to continue after you edit, save, and close "
                "the bib file.")
  # Check edits:
  new = loadfile(temp_bib)
  if new is None:
    print('\nInvalid bib file. Aborting edits.')
    return
  # Update database:
  save(new)
  export(new)
  # Delete tmp file:
  os.remove(temp_bib)


def search(authors=None, year=None, title=None):
  """
  Search in bibmanager database by authors, year, or title keywords.

  Parameters
  ----------
  authors: String or List of strings
     An author name (or list of names) with BibTeX format (see parse_name()
     docstring).  To restrict search to a first author, prepend the
     '^' character to a name.
  year: Integer or two-element integer tuple
     If integer, match against year; if tuple, minimum and maximum
     matching years (including).
  title: String or iterable (list, tuple, or ndarray of strings)
     Match entries that contain all input strings in the title (ignore case).

  Returns
  -------
  matches: List of Bib() objects
     Entries that match all input criteria.

  Examples
  --------
  >>> import bib_manager as bm
  >>> # Search by last name:
  >>> matches = bm.search(authors="Cubillos")
  >>> # Search by last name and initial:
  >>> matches = bm.search(authors="Cubillos, P")
  >>> # Search by author in given year:
  >>> matches = bm.search(authors="Cubillos, P", year=2017)
  >>> # Search by first author and co-author:
  >>> matches = bm.search(authors=["^Cubillos", "Blecic"])
  >>> # Search by keyword in title:
  >>> matches = bm.search(title="Spitzer")
  >>> # Search by keywords in title (must contain both strings):
  >>> matches = bm.search(title=["HD 189", "HD 209"])
  """
  matches = load()
  if year is not None:
    try: # Assume year = [from_year, to_year]
      matches = [bib for bib in matches if bib.year >= year[0]]
      matches = [bib for bib in matches if bib.year <= year[1]]
    except:
      matches = [bib for bib in matches if bib.year == year]

  if authors is not None:
    if isinstance(authors, str):
      authors = [authors]
    elif not isinstance(authors, (list, tuple, np.ndarray)):
      raise ValueError("Invalid input format for 'authors'.")
    for author in authors:
      matches = [bib for bib in matches if author in bib]

  if title is not None:
    if isinstance(title, str):
      title = [title]
    elif not isinstance(title, (list, tuple, np.ndarray)):
      raise ValueError("Invalid input format for 'title'.")
    for word in title:
      matches = [bib for bib in matches if word.lower() in bib.title.lower()]
  return matches


def querry():
  """
  Make a querry from ADS.
  """
  adquerry = "https://api.adsabs.harvard.edu/v1/search/query?"
  #adsurl = "https://api.adsabs.harvard.edu/v1/export/bibtex"

  token = "token"

  # ADS querry:
  r = requests.get('{:s}q=author%3A"%5Ecubillos%2Cp&fl=title,author',
                   headers={'Authorization': 'Bearer ' + token})

  # Get bibtx entry for a given bibcode:
  bibcode = {"bibcode":["2013arXiv1305.6548A"]}
  r = requests.post("https://api.adsabs.harvard.edu/v1/export/bibtex",
                    headers={"Authorization": "Bearer " + token,
                             "Content-type": "application/json"},
                    data=json.dumps(bibcode))
  print(r.json()["export"])

