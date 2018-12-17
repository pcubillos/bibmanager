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
#import functools
import numpy as np
from collections import namedtuple

"""
I want:
+ Database
+ Create a base bibfile from a given bibfile.
+ Merge a bibfile, point out conflicts.
- Update entries manually.
- Add entries manually.
- Query from it.
- Create a bibfile from a given latex file.

Fail cases to test:
- multi-line authors without {}.

Enhancement ideas:
- cond_find() + join instead of cond_replace.
- Store database as dicts instead of Bib() objects.

Resources:
http://texdoc.net/texmf-dist/doc/bibtex/base/btxdoc.pdf
"""

# IO definitions (put these into a setup/config file?):
bm_home = os.path.expanduser("~") + "/.bibmanager/"
bm_bibliography = "bibliography.pickle"
lexer = prompt_toolkit.lexers.PygmentsLexer(BibTeXLexer)
style = prompt_toolkit.styles.style_from_pygments_cls(AutumnStyle)


# Some definitions:
Author  = namedtuple("Author", "first von last jr")
Sauthor = namedtuple("Sauthor", "last first von jr year month")
months  = {"jan":1, "feb":2, "mar":3, "apr": 4, "may": 5, "jun":6,
           "jul":7, "aug":8, "sep":9, "oct":10, "nov":11, "dec":12}

banner = "\n" + ":"*70 + "\n"


def count(text):
  """
  Count net number of braces in text (add 1 for each opening brace,
  subtract one for each closing brace).

  Parameters
  ----------
  text: String

  Returns
  -------
  counts: Integer
     Net number of braces.

  Examples
  --------
  >>> import bibm as bm
  >>> bm.count('{Hello} world')
  """
  return text.count("{") - text.count("}")


def nest(text):
  """
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
  >>> s = "{{Adams}, E. and {Dupree}, A.~K. and {Kulesa}, C. and {McCarthy}, D.},"
  >>> n = bm.nest(s)
  >>> print('{:s}\n{:s}'.format(s, "".join([str(v) for v in n])))
  >>> %timeit -n 1000 nest(s)
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


def cond_find(line, regex, protect=True, nested=None, nlev=0):
  """
  Conditional find.

  Parameters
  ----------
  line: String
     String where to search for regex.
  regex: String
     Pattern to find.
  protect: Bool
     If True, computed nested level of characters.  Accept regex match
     only if nested level is zero.
  nested: 1D integer iterable
     Braces nesting level of characters in line.
  nlev: Integer
     Required nested level to accept regex match.

  Returns
  -------
     List of strings delimited by the accepted regex matches.

  Examples
  --------
  >>> import bibm as bm
  >>> # Split an author field by searching for the ' and ' regex:
  >>> bm.cond_find("{Adams}, E.~R. and {Dupree}, A.~K. and {Kulesa}, C.",
                   " and ", protect=True)
  >>> # Protected instances (within braces) won't count:
  >>> bm.cond_find("{AAS and Astropy Teams} and {Hendrickson}, A.",
                   " and ", protect=True)
  >>> # Matches at the beginning or end do not count for split:
  >>> bm.cond_find(",Tom, Andy, Steve,", ",", protect=True)
  >>> # But two consecutive matches do return an empty string:
  >>> bm.cond_find("Tom,, Steve", ",", protect=True)
  >>> # Find both spaces and dashes with a single regex:
  >>> bm.cond_find("J. Y.-K.", " |-", protect=False)
  """
  if protect:
    if nested is None:
      nested = nest(line)
  else:
    nested = [0 for _ in line]

  # First and last indices of each regex match:
  bounds = [(m.start(0), m.end(0))
            for m in re.finditer(regex, line)
            if nested[m.start(0)] == nlev]

  flat_bounds = [item for sublist in bounds for item in sublist]

  if len(flat_bounds) == 0:
    return [line]
  if flat_bounds[0] != 0:
    flat_bounds.insert(0, 0)
  else:
    flat_bounds.pop(0)
  if flat_bounds[-1] != len(line):
    flat_bounds.append(len(line))
  pairs = zip(*([iter(flat_bounds)]*2))
  return [line[start:end] for (start,end) in pairs]


def cond_replace(text, pattern, replace, nested=None):
  """
  Conditional replace only if nested level is zero.

  Parameters
  ----------
  text: String
     Text where to search.
  pattern: String
     Pattern to replace.
  replace: String
     Replacement.

  Returns
  -------
  text: String
     Text with replaced patterns.

  Examples
  --------
  >>> import bibm as bm
  >>> %timeit -n 1000 bm.cond_replace('U.~G. and {Hammer}', "~", " ")
  """
  if nested is None:
    nested = nest(text)
  counts = [m.start(0) for m in re.finditer(pattern, text)]

  for i in counts:
    if nested[i] == 0:
      text = text[0:i] + text[i:].replace(pattern, replace, 1)
  return text


#@functools.lru_cache(maxsize=1024, typed=False)
def parse_name(name):
  """
  Parse first, last, von, and jr parts from a name, following these rules:
  http://mirror.easyname.at/ctan/info/bibtex/tamethebeast/ttb_en.pdf

  Parameters
  ----------
  name: String
     A name following bibtex style.

  Returns
  -------
  author: Author named tuple
     Four element tuple with the parsed name.

  Examples
  --------
  >>> import bibm as bm
  >>> bm.parse_name('{Hendrickson}, A.')
  Author(first='A.', von='', last='{Hendrickson}', jr='')
  >>> bm.parse_name('Eric Jones')
  Author(first='Eric', von='', last='Jones', jr='')
  >>> bm.parse_name('{AAS Journals Team}')
  Author(first='', von='', last='{AAS Journals Team}', jr='')
  """
  name = cond_replace(name, "~", " ")
  fields = cond_find(name, ",")

  if len(fields) <= 0 or len(fields) > 3:
    print("Invalid format for author '{:s}'.".format(name))

  # 'First von Last' format:
  if len(fields) == 1:
    jr = ""
    words = cond_find(name, " ")
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
    vonlast = fields[0].strip()
    if vonlast == "":
      print("Invalid author, does not have a last name.")

    # 'von Last, First' format:
    if len(fields) == 2:
      jr = ""
      first = fields[1].strip()

    # 'von Last, Jr, First' format:
    if len(fields) == 3:
      jr    = fields[1].strip()
      first = fields[2].strip()

    words = cond_find(vonlast, " ")
    lowers = [s[0].islower() for s in words[:-1]]

    if np.any(lowers):
      ilast = np.max(np.where(lowers)) + 1
      von = " ".join(words[:ilast])
    else:
      von = ""
      ilast = 0
    last = " ".join(words[ilast:])

  return Author(first, von, last, jr)


#@functools.lru_cache(maxsize=1024, typed=False)
def purify(name, german=False):
  """
  Replace accented characters closely following these rules:
  https://tex.stackexchange.com/questions/57743/how-to-write-%C3%A4-and-other-umlauts-and-accented-letters-in-bibliography
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
               '{AAS Journals Team}',
               "Kov{\\'a}{\\v r}{\\'i}k",
               "Jarom{\\'i}r Kov{\\'a\\v r\\'i}k",
               "{\\.I}volgin",
               "Gon{\\c c}alez Nu{\~n}ez",
               "Knausg{\\aa}rd Sm{\\o}rrebr{\\o}d",
               'Schr{\\"o}dinger Be{\\ss}er']

  >>> for name in names:
  >>>     print("{:35s}".format(name), bm.purify(name))
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
  """
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
    print("{:20s}:".format(name), bm.initials(name))
  """
  name = purify(name)
  split_names = cond_find(name, "( |-)", protect=False)
  # Somehow string[0:1] does not break when string = "", unlike string[0].
  return "".join([name[0:1] for name in split_names])


def cond_next(pattern, text, nested, nlev=1):
  """
  Find next instance of pattern in text where nested is nlev.

  Parameters
  ----------
  pattern: String
     Regular expression to search for.
  text: String
     Text where to search for regex.
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
  >>> # TBD
  """
  for m in re.finditer(pattern, text):
    if nested[m.start(0)] == nlev:
      return m.start(0)
  # If not found, return last index in text:
  return len(text) - 1


def next_char(s):
  """
  Get index of next non-blank character in string s.
  """
  if len(s) == 0:
    return 0
  i = 0
  while s[i].isspace():
    i += 1
  return i


def last_char(s):
  """
  Get index of last non-blank character in string s.
  """
  i = len(s)
  if i == 0:
    return 0
  while s[i-1].isspace():
    i -= 1
  return i


def get_fields(entry):
  """
  Generator to parse entries of a bibbliographic entry.

  Parameters
  ----------
  entry: String
     A bibliographic entry text.
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
      end = start + cond_next('"', entry[start:], nested[start:], nlev=1)
    else:
      end = start + cond_next(",", entry[start:], nested[start:], nlev=1)
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
    Create a Bib() object from given entry.

    Parameters
    ----------
    entry: String
       A bibliographic entry text.
    """
    self.content  = entry
    # Defaults:
    self.month    = 13
    self.adsurl   = None
    self.doi      = None
    self.eprint   = None
    self.isbn     = None

    #print(entry.split("\n")[0])
    fields = get_fields(self.content)
    self.key = next(fields)

    for key, value, nested in fields:
      if key == "title":
        # Title with no braces, tabs, nor linebreak and corrected blanks:
        self.title = " ".join(re.sub("({|})", "", value).split())

      if key == "author":
        #authors = parse_authors(value.replace("\n", " "))
        # Parse authors finding all out-of-braces 'and' instances:
        authors = cond_find(value.replace("\n"," "), " and ",
                            nested=nested, nlev=nested[0])
        self.authors = [parse_name(author) for author in authors]

      if key == "year":
        r = re.search('[0-9]{4}', value)
        self.year = int(r.group(0))

      if key == "month":
        value = value.lower().strip()
        self.month = months[value[0:3]]

      if key == "doi":
        self.doi = value

      if key == "adsurl":
        self.adsurl = value

      if key == "eprint":
        self.eprint = value

      if key == "isbn":
        self.isbn = value.lower().strip()

    if self.year is None or self.authors is None:
      print("Bibtex entry '{:s}' has no year or author.".format(self.key))
    # First-author fields used for sorting:
    #self.sort_author = Sauthor("","","","",1,2)
    self.sort_author = Sauthor(purify(self.authors[0].last),
                               initials(self.authors[0].first),
                               purify(self.authors[0].von),
                               purify(self.authors[0].jr),
                               self.year, self.month)

  def __repr__(self):
    return self.content

  def __contains__(self, author):
    """
    Check if given author is in the author list of this bib entry.
    """
    # Parse and purify input author name:
    author = parse_name(author)
    first = initials(author.first)
    von   = purify(author.von)
    last  = purify(author.last)
    jr    = purify(author.jr)
    # Remove non-matching authors by each non-empty field:
    authors = self.authors
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
    first, von, jr, year, and month.  If any is equal, use next field
    to compare.
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
    # Evaluate to equal by first initial if one entry has less info than the other:
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
    Published status according to ADSURL field.

    Return -1 if adsurl is None.
    Return  0 if adsurl is arXiv.
    Return  1 if adsurl is peer-reviewed journal.
    """
    if self.adsurl is None:
      return -1
    return int(self.adsurl.find('arXiv') < 0)


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

  Example
  -------
  >>> import bibm as bm
  >>> bibfile = "test.bib"
  >>> entries = bm.loadfile(bibfile)
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
    print("Error, missing input arguments for loadfile().")
    return

  for i,line in enumerate(f):
    # New entry:
    if line.startswith("@") and parcount != 0:
        print("Error, mismatched braces in line {:d}:\n'{:s}'.".
               format(i,line.rstrip()))
        return

    parcount += count(line)
    if parcount == 0 and entry == []:
      continue

    if parcount < 0:
      print("Error, negative braces count in line {:d}.".format(i))
      return

    entry.append(line.rstrip())

    if parcount == 0 and entry != []:
      entries.append("\n".join(entry))
      entry = []

  if bibfile is not None:
    f.close()

  #return entries
  bibs = [Bib(entry) for entry in entries]

  remove_duplicates(bibs, "doi")
  remove_duplicates(bibs, "isbn")
  remove_duplicates(bibs, "adsurl")
  remove_duplicates(bibs, "eprint")

  return sorted(bibs)


def remove_duplicates(bibs, field):
  """
  Look for duplicates (within a same list of entries) by field and remove them.

  Parameters
  ----------
  bibs: List of Bib() objects
     Entries to filter.
  field: String
     Field to use for filtering.
  """
  fieldlist = [getattr(bib,field) if getattr(bib,field) is not None else ""
               for bib in bibs]
  ubib, uinv, counts = np.unique(fieldlist, return_inverse=True, return_counts=True)
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
    if len(uentries) == 1:
      continue
    # TBD: pick published over arxiv adsurl if that's the case

    tokens = [(Token.Comment, banner)]
    tokens += list(pygments.lex("\n\n".join(uentries), lexer=BibTeXLexer()))
    print_formatted_text(PygmentsTokens(tokens), style=style)
    s = req_input("Duplicate {:s} field, keep first [], second [2], third [3], "
                  "etc.: ".format(field), options=[""]+list(range(10)))
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
        tokens = [(Token.Comment, banner),
                  (Token.Text, "DATABASE:\n")]
        tokens += list(pygments.lex(bibs[idx].content, lexer=BibTeXLexer()))
        tokens += [(Token.Text, "\nNEW:\n")]
        tokens += list(pygments.lex(e.content, lexer=BibTeXLexer()))
        print_formatted_text(PygmentsTokens(tokens), style=style)
        s = req_input("Duplicate {:s} field but different keys, []keep "
                      "database or take [n]ew: ".format(field),
                      options=["", "n"])
        if s == "n":
          bibs[idx] = e
    removes.append(i)
  for idx in reversed(sorted(removes)):
    new.pop(idx)


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
      tokens = [(Token.Comment, banner),
                (Token.Text, "DATABASE:\n")]
      tokens += list(pygments.lex(bibs[idx].content, lexer=BibTeXLexer()))
      tokens += [(Token.Text, "\nNEW:\n")]
      tokens += list(pygments.lex(e.content, lexer=BibTeXLexer()))
      print_formatted_text(PygmentsTokens(tokens), style=style)
      s = input("Duplicate key but content differ, []keep database, "
                "take [n]ew, or edit new key into new entry:\n".
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
    tokens = [(Token.Comment, banner),
              (Token.Text, "DATABASE:\n")]
    tokens += list(pygments.lex(bibs[idx].content, lexer=BibTeXLexer()))
    tokens += [(Token.Text, "\nNEW:\n")]
    tokens += list(pygments.lex(e.content, lexer=BibTeXLexer()))
    print_formatted_text(PygmentsTokens(tokens), style=style)
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
  Load the bibmanager database of bib entries.

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
  >>> bibfile = 'pyrat.bib'
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
  if new is not None:
    merge(new=new, take=take)


def edit():
  """
  Manual edit the bibfile database in text editor.

  Resources
  ---------
  https://stackoverflow.com/questions/17317219/is-there-an-platform-independent-equivalent-of-os-startfile
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
  # Check edits, update database:
  pass
  # Delete tmp file:
  pass


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



if False:
  # Printing the output of a pygments lexer.
  tokens = [(Token.Comment, banner),
            (Token.Text, "DATABASE:\n")]
  tokens += list(pygments.lex(bibs[0].content, lexer=BibTeXLexer()))
  tokens += [(Token.Text, "\nNEW:\n")]
  tokens += list(pygments.lex(bibs[1].content, lexer=BibTeXLexer()))
  print_formatted_text(PygmentsTokens(tokens), style=style)
  s = req_input("Possible duplicate, same title but keys differ, []ignore, "
                "[r]eplace, or [a]dd: ",  options=["", "r", "a"])

