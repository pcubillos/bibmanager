# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = [
    'Bib',
    'display_bibs',
    'remove_duplicates',
    'filter_field',
    'read_file',
    'save',
    'load',
    'find',
    'get_version',
    'export',
    'merge',
    'init',
    'add_entries',
    'edit',
    'search',
    'prompt_search',
]

import datetime
import os
import pickle
import re
import shutil
import subprocess
import sys
import urllib
import warnings

import numpy as np
import prompt_toolkit
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit.output.defaults import create_output
from prompt_toolkit import print_formatted_text
import pygments
from pygments.token import Token
from pygments.lexers.bibtex import BibTeXLexer

from .. import config_manager as cm
from .. import utils as u
from ..__init__ import __version__


# Some constant definitions:
lexer = prompt_toolkit.lexers.PygmentsLexer(BibTeXLexer)

months  = {"jan":1, "feb":2, "mar":3, "apr": 4, "may": 5, "jun":6,
           "jul":7, "aug":8, "sep":9, "oct":10, "nov":11, "dec":12}


class Bib(object):
  """
  Bibliographic-entry object.
  """
  def __init__(self, entry, pdf=None, freeze=None):
      """
      Create a Bib() object from given entry.

      Parameters
      ----------
      entry: String
          A bibliographic entry text.
      pdf: String
          Name of PDF file associated with this entry.
      freeze: Bool
          Flag that, if True, prevents the entry to be ADS-updated.

      Examples
      --------
      >>> import bibmanager.bib_manager as bm
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
      if u.count(entry) != 0:
          raise ValueError("Mismatched braces in entry.")
      self.content  = entry
      # Defaults:
      self.authors = None
      self.title = None
      self.year = None
      self.month = 13
      self.adsurl = None
      self.bibcode = None
      self.doi = None
      self.eprint = None
      self.isbn = None
      # Meta info (not contained in bibtex):
      self.pdf = pdf
      self.freeze = freeze

      fields = u.get_fields(self.content)
      self.key = next(fields)

      for key, value, nested in fields:
          if key == "title":
              # Title with no braces, tabs, nor linebreak and corrected blanks:
              self.title = " ".join(re.sub("({|})", "", value).split())
          elif key == "booktitle" and self.title is None:
              # Only when the entry does not contain a 'title' field:
              self.title = " ".join(re.sub("({|})", "", value).split())

          elif key == "author":
              # Parse authors finding all non-brace-nested 'and' instances:
              authors, nests = u.cond_split(
                  value.replace("\n"," "), " and ",
                  nested=nested,
                  ret_nests=True)
              self.authors = [
                  u.parse_name(author, nested, self.key)
                  for author,nested in zip(authors,nests)]

          elif key == "year":
              value = re.sub('({|}|")', '', value)
              if value.isnumeric():
                  self.year = int(value)
              else:
                  warnings.formatwarning = u.warnings_format
                  warnings.warn(
                      f"Bad year format value '{value}' for entry '{self.key}'")

          elif key == "month":
              value = value.lower().strip()
              if value.isdigit():
                  month = int(value)
              else:
                  month = value[0:3]
              if month in months.values():
                  self.month = month
              elif month in months.keys():
                  self.month = months[month]
              elif month == '':
                  pass
              else:
                  warnings.formatwarning = u.warnings_format
                  warnings.warn(
                      f"Invalid month value '{value}' for entry '{self.key}'")

          elif key == "doi":
              self.doi = value

          elif key == "adsurl":
              self.adsurl = value
              # Get bibcode from adsurl, un-code UTF-8, and remove backslashes:
              bibcode = os.path.split(value)[1].replace('\\', '')
              self.bibcode = urllib.parse.unquote(bibcode)

          elif key == "eprint":
              self.eprint = value.replace('arXiv:','').replace('astro-ph/','')

          elif key == "isbn":
              self.isbn = value.lower().strip()

      # First-author fields used for sorting:
      # Note this differs from Author[0], since fields are 'purified',
      # and 'first' goes only by initials().
      if self.authors is not None:
          last = u.purify(self.authors[0].last)
          first = u.initials(self.authors[0].first)
          von = u.purify(self.authors[0].von)
          jr = u.purify(self.authors[0].jr)
      else:
          last, first, von, jr = None, None, None, None

      self.sort_author = u.Sort_author(
          last, first, von, jr, self.year, self.month)

  def update_content(self, other):
      """Update the bibtex content of self with that of other."""
      # Update these (non-bibtex info) only if not None:
      non_bibtex = ['pdf', 'freeze']
      for key,val in other.__dict__.items():
          if key in self.__dict__ and not (key in non_bibtex and val is None):
              setattr(self, key, val)

  def update_key(self, new_key):
      """Update key with new_key, making sure to also update content."""
      self.content = self.content.replace(self.key, new_key, 1)
      self.key = new_key

  def meta(self):
      """String containing the non-None meta information."""
      meta = ''
      if self.freeze:
          meta += 'freeze\n'
      if self.pdf is not None:
          meta += f'pdf: {self.pdf}\n'
      return meta

  def __repr__(self):
      return self.meta() + self.content

  def __contains__(self, author):
      r"""
      Check if given author is in the author list of this bib entry.
      If the 'author' string begins with the '^' character, match
      only against the first author.

      Parameters
      ----------
      author: String
          An author name in a valid BibTeX format.

      Examples
      --------
      >>> import bibmanager.bib_manager as bm
      >>> bib = bm.Bib('''@ARTICLE{DoeEtal2020,
                      author = {{Doe}, J. and {Perez}, J. and {Dupont}, J.},
                       title = "What Have the Astronomers ever Done for Us?",
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
      if self.authors is None:
          return False
      # Check first-author mark:
      if author[0:1] == '^':
          author = author[1:]
          authors = [self.authors[0]]
      else:
          authors = self.authors
      # Parse and purify input author name:
      author = u.parse_name(author)
      first  = u.initials(author.first)
      von    = u.purify(author.von)
      last   = u.purify(author.last)
      jr     = u.purify(author.jr)
      # Remove non-matching authors by each non-empty field:
      if len(jr) > 0:
          authors = [author for author in authors if jr  == u.purify(author.jr)]
      if len(von) > 0:
          authors = [
              author for author in authors
              if von == u.purify(author.von)]
      if len(first) > 0:
          authors = [
              author for author in authors
              if first == u.initials(author.first)[0:len(first)]]
      authors = [author for author in authors if last == u.purify(author.last)]
      return len(authors) >= 1

  # https://docs.python.org/3.6/library/stdtypes.html
  def __lt__(self, other):
      """
      Evaluate sequentially according to sort_author's fields: last,
      first, von, and jr, year, and month.  If any of these
      fields are equal, go on to next field to compare.
      """
      s, o = self.sort_author, other.sort_author
      if s.last is None and o.last is not None:
          return False
      elif s.last is not None and o.last is None:
          return True
      elif s.last is not None and o.last is not None:
          if s.last != o.last:
              return s.last < o.last

          if len(s.first) == 1 or len(o.first) == 1:
              if s.first[0:1] != o.first[0:1]:
                  return s.first < o.first
          else:
              if s.first != o.first:
                  return s.first < o.first
          if s.von != o.von:
              return s.von < o.von
          if s.jr != o.jr:
              return s.jr < o.jr

      s_year = 9999 if s.year is None else s.year
      o_year = 9999 if o.year is None else o.year
      if s_year != o_year:
          return s_year < o_year
      return s.month < o.month

  def __eq__(self, other):
      """
      Check whether self and other have same sort_author (first author)
      and year/month.
      Evaluate to equal by first initial if one entry has less initials
      than the other.
      """
      s, o = self.sort_author, other.sort_author
      if s.last is None and o.last is None:
          return s.year == o.year and s.month == o.month
      if s.last is None or o.last is None:
          return False

      if len(s.first) == 1 or len(o.first) == 1:
          first = s.first[0:1] == o.first[0:1]
      else:
          first = s.first == o.first

      return (
          s.last == o.last and
          first and
          s.von == o.von and
          s.jr == o.jr and
          s.year == o.year and
          s.month == o.month)

  def __le__(self, other):
      return self.__lt__(other) or self.__eq__(other)

  def published(self):
      """
      Published status according to the ADS bibcode field:
          Return -1 if bibcode is None.
          Return  0 if bibcode is arXiv.
          Return  1 if bibcode is peer-reviewed journal.
      """
      if self.bibcode is None:
          return -1
      return int(self.bibcode.find('arXiv') < 0)


  def get_authors(self, format="short"):
      """
      wrapper for string representation for the author list.
      See bib_manager.get_authors() for docstring.
      """
      return u.get_authors(self.authors, format)


def display_bibs(labels, bibs, meta=False):
    r"""
    Display a list of bib entries on screen with flying colors.

    Parameters
    ----------
    labels: List of Strings
        Header labels to show above each Bib() entry.
    bibs: List of Bib() objects
        BibTeX entries to display.
    meta: Bool
        If True, also display the meta-information.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
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
    style = prompt_toolkit.styles.style_from_pygments_cls(
        pygments.styles.get_style_by_name(cm.get('style')))
    if labels is None:
        labels = ["" for _ in bibs]
    tokens = [(Token.Comment, u.BANNER)]
    for label,bib in zip(labels, bibs):
        tokens += [(Token.Text, label)]
        if meta:
            tokens += [(Token.Comment, bib.meta())]
        tokens += list(pygments.lex(bib.content, lexer=BibTeXLexer()))
        tokens += [(Token.Text, "\n")]
    print_formatted_text(
        PygmentsTokens(tokens), end="", style=style,
        output=create_output(sys.stdout))


def remove_duplicates(bibs, field):
    """
    Look for duplicates (within a same list of entries) by field and
    remove them (in place).

    Parameters
    ----------
    bibs: List of Bib() objects
        Entries to filter.
    field: String
        Field to use for filtering ('doi', 'isbn', 'bibcode', or 'eprint').
    """
    fieldlist = [
        getattr(bib,field) if getattr(bib,field) is not None else ""
        for bib in bibs]
    # No entries:
    if len(fieldlist) == 0:
        return

    ubib, uinv, counts = np.unique(
        fieldlist, return_inverse=True, return_counts=True)
    multis = np.where((counts > 1) & (ubib != ""))[0]

    # No duplicates:
    if len(multis) == 0:
        return

    removes = []
    for m in multis:
        all_indices = np.where(uinv == m)[0]
        entries = [bibs[i].content for i in all_indices]

        # Remove identical entries:
        uentries, uidx = np.unique(entries, return_index=True)
        indices = list(all_indices[uidx])
        removes += [idx for idx in all_indices if idx not in indices]
        nbibs = len(uentries)
        if nbibs == 1:
            continue

        # Pick peer-reviewed over ArXiv over non-ADS:
        pubs = [bibs[i].published() for i in indices]
        pubmax = np.amax(pubs)
        removes += [idx for idx,pub in zip(indices,pubs) if pub <  pubmax]
        indices  = [idx for idx,pub in zip(indices,pubs) if pub == pubmax]
        nbibs = len(indices)
        if nbibs == 1:
            continue

        # If field is isbn, check doi to differentiate chapters from same book:
        if field == 'isbn':
            dois = [
                bibs[idx].doi if bibs[idx].doi is not None else ""
                for idx in indices]
            u_doi, doi_inv, doi_counts = np.unique(
                dois, return_inverse=True, return_counts=True)
            single_dois = u_doi[doi_counts==1]
            indices = [
                idx for idx,doi in zip(indices,dois)
                if doi not in single_dois]
            nbibs = len(indices)
            if nbibs <= 1:
                continue

        # Query the user:
        labels = [idx + " ENTRY:\n" for idx in u.ordinal(np.arange(nbibs)+1)]
        display_bibs(labels, [bibs[i] for i in indices])
        s = u.req_input(
            f"Duplicate {field} field, []keep first, [2]second, "
            "[3]third, etc.: ",
            options=[""]+list(np.arange(nbibs)+1))
        if s == "":
            indices.pop(0)
        else:
            indices.pop(int(s)-1)
        removes += indices

    for idx in reversed(sorted(removes)):
        bibs.pop(idx)


def filter_field(bibs, new, field, take):
    """
    Filter duplicate entries by field between new and bibs.
    This routine modifies new removing the duplicates, and may modify
    bibs (depending on take argument).

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
        duplicated entries:
        'old': Take the database entry over new.
        'new': Take the new entry over the database.
        'ask': Ask user to decide (interactively).
    """
    fields = [getattr(bib,field) for bib in bibs]
    removes = []
    for i,bib in enumerate(new):
        if getattr(bib,field) is None or getattr(bib,field) not in fields:
            continue
        idx = fields.index(getattr(bib,field))
        # Replace if duplicated and new has newer bibcode:
        if bib.published() > bibs[idx].published() or take == 'new':
            bibs[idx].update_content(bib)
        # Look for different-key conflict:
        if bib.key != bibs[idx].key and take == "ask":
            display_bibs(["DATABASE:\n", "NEW:\n"], [bibs[idx], bib])
            s = u.req_input(
                f"Duplicate {field} field but different keys, []keep "
                "database or take [n]ew: ",
                options=["", "n"])
            if s == "n":
                bibs[idx].update_content(bib)
        removes.append(i)
    for idx in reversed(sorted(removes)):
        new.pop(idx)


def read_file(bibfile=None, text=None):
    r"""
    Create a list of Bib() objects from a BibTeX file (.bib file).

    Parameters
    ----------
    bibfile: String
        Path to an existing .bib file.
    text: String
        Content of a .bib file (ignored if bibfile is not None).

    Returns
    -------
    bibs: List of Bib() objects
        List of Bib() objects of BibTeX entries in bibfile, sorted by
        Sort_author() fields.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> text = (
    >>>    "@misc{AASteamHendrickson2018aastex62,\n"
    >>>    "author = {{AAS Journals Team} and {Hendrickson}, Amy},\n"
    >>>    "title  = {{AASJournals/AASTeX60: Version 6.2 official release}},\n"
    >>>    "year   = 2018\n"
    >>>    "}")
    >>> bibs = bm.read_file(text=text)
    """
    entries = []  # Store Lists of bibtex entries
    meta_info = []  # Meta information for each entry

    # Load a bib file:
    if bibfile is None and text is None:
        raise TypeError(
            "Missing input arguments for read_file(), at least "
            "bibfile or text must be provided.")
    if bibfile is not None:
        with open(bibfile, 'r') as f:
            text = f.read()

    position = 0
    while True:
        start_pos = text.find('@', position)
        if start_pos < 0:
            break
        # TBD: bracket_or_parenthesis
        pos = u.find_closing_bracket(text, start_pos, get_open=True)
        # Open end:
        if pos is None:
            start_line = len(text[:start_pos].splitlines())
            line = text.splitlines()[start_line].rstrip()
            raise ValueError(
                f"Mismatched braces at/after line {start_line}:\n{line}")
        left_bracket, end_pos = pos
        # Skip @comment entries
        if text[start_pos+1:start_pos+left_bracket].lower() == 'comment':
            position = end_pos
            continue
        # Content outside/before entry is comments or meta info:
        meta = {
            'pdf': None,
            'freeze': None,
        }
        for line in text[position:start_pos].splitlines():
            if line.lower().startswith('pdf'):
                meta['pdf'] = line.split()[-1]
            if line.lower().strip() == 'freeze':
                meta['freeze'] = True

        entries.append(text[start_pos:end_pos+1])
        meta_info.append(meta)
        position = end_pos

    bibs = [
        Bib(entry, **meta)
        for entry,meta in zip(entries,meta_info)
    ]

    remove_duplicates(bibs, "doi")
    remove_duplicates(bibs, "isbn")
    remove_duplicates(bibs, "bibcode")
    remove_duplicates(bibs, "eprint")

    # Check pathed-pdf meta values:
    for i,bib in enumerate(bibs):
        if bib.pdf is not None and os.path.dirname(bib.pdf) != '':
            filename = os.path.expanduser(bib.pdf)
            if not os.path.isfile(filename):
                bibs[i].pdf = None
            else:
                shutil.move(
                    os.path.expanduser(filename),
                    f"{u.BM_PDF()}{os.path.basename(filename)}")
                bibs[i].pdf = os.path.basename(filename)
    return sorted(bibs)


def save(entries):
    """
    Save list of Bib() entries into bibmanager pickle database.

    Parameters
    ----------
    entries: List of Bib() objects
        bib files to store.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> # TBD: Load some entries
    >>> bm.save(entries)
    """
    with open(u.BM_DATABASE(), 'wb') as handle:
        pickle.dump(entries, handle, protocol=4)
        pickle.dump(__version__, handle, protocol=4)


def load(bm_database=None):
    """
    Load a Bibmanager database of BibTeX entries.

    Parameters
    ----------
    bm_database: String
        A Bibmanager pickle database file.  If None, default's the
        database in system.

    Returns
    -------
    bibs: List Bib() instances
        Return an empty list if there is no database file.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> bibs = bm.load()
    """
    if bm_database is None:
        bm_database = u.BM_DATABASE()

    try:
        with open(bm_database, 'rb') as handle:
            bibs = pickle.load(handle)
    except:
        return []
    return bibs


def find(key=None, bibcode=None, bibs=None):
    """
    Find an specific entry in the database.

    Parameters
    ----------
    key: String
        Key of entry to find.
    bibcode: String
        Bibcode of entry to find (ignored if key is not None).
    bibs: List of Bib() instances
        Database where to search.  If None, load the Bibmanager database.

    Returns
    -------
    bib: a Bib() instance
        BibTex matching either key or bibcode.
    """
    if bibs is None:
        bibs = load()

    if key is not None:
        for bib in bibs:
            if bib.key == key:
                return bib
        else:
            return None

    if bibcode is not None:
        for bib in bibs:
            if bib.bibcode == bibcode:
                return bib
        else:
            return None

    raise ValueError("Either key or bibcode arguments must be specified.")


def get_version(bm_database=None):
    """
    Get version of pickled database file.
    If database does not exists, return current bibmanager version.
    If database does not contain version, return '0.0.0'.

    Parameters
    ----------
    bm_database: String
        A Bibmanager pickle database file.  If None, default's the
        database in system.

    Returns
    -------
    version: String
        bibmanager version of pickled objects.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> bibs = bm.get_version()
    """
    if bm_database is None:
        bm_database = u.BM_DATABASE()

    if not os.path.exists(bm_database):
        return __version__

    with open(bm_database, 'rb') as handle:
        dummy = pickle.load(handle)
        try:
            version = pickle.load(handle)
        except EOFError:
            version = '0.0.0'
    return version


def export(entries, bibfile=None, meta=False):
    """
    Export list of Bib() entries into a .bib file.

    Parameters
    ----------
    entries: List of Bib() objects
        Entries to export.
    bibfile: String
        Output .bib file name.  If None, export into home directory.
    meta: Bool
        If True, include meta information before the entries on the
        output bib file.
    """
    if bibfile is None:
        bibfile = u.BM_BIBFILE()
    # Header for identification purposes:
    header = [
        'This file was created by bibmanager\n',
        'https://pcubillos.github.io/bibmanager/\n\n']
    # Care not to overwrite user's bib files:
    if os.path.exists(bibfile):
        with open(bibfile, 'r') as f:
            head = f.readline()
        if head.strip() != header[0].strip():
            path, bfile = os.path.split(os.path.realpath(bibfile))
            shutil.copy(
                bibfile, "".join(
                [path, '/orig_', str(datetime.date.today()), '_', bfile]))

    with open(bibfile, 'w') as f:
        f.writelines(header)
        for bib in entries:
            if meta:
                f.write(bib.meta())
            f.write(bib.content)
            f.write("\n\n")


def merge(bibfile=None, new=None, take="old", base=None):
    """
    Merge entries from a new bibfile into the bibmanager database
    (or into an input database).

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
    base: List of Bib() objects
        If None, merge new entries into the bibmanager database.
        If not None, merge new entries into base.

    Returns
    -------
    bibs: List of Bib() objects
        Merged list of BibTeX entries.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> import os
    >>> # TBD: Need to add sample2.bib into package.
    >>> newbib = os.path.expanduser("~") + "/.bibmanager/examples/sample2.bib"
    >>> # Merge newbib into database:
    >>> bm.merge(newbib, take='old')
    """
    if base is None:
        bibs = load()
    else:
        bibs = base

    if bibfile is not None:
        new = read_file(bibfile)
    if new is None:
        return

    # Filter duplicates by field:
    filter_field(bibs, new, "doi", take)
    filter_field(bibs, new, "isbn", take)
    filter_field(bibs, new, "bibcode", take)
    filter_field(bibs, new, "eprint", take)

    # Filter duplicate key:
    keep = np.zeros(len(new), bool)
    bm_keys = [bib.key for bib in bibs]
    for i,bib in enumerate(new):
        if bib.key not in bm_keys:
            keep[i] = True
            continue
        idx = bm_keys.index(bib.key)
        if bib.content == bibs[idx].content:
            continue # Duplicate, do not take
        else:
            display_bibs(["DATABASE:\n", "NEW:\n"], [bibs[idx], bib])
            s = input(
                "Duplicate key but content differ, []ignore new, "
                "take [n]ew, or\nrename key of new entry: ")
            if s == "n":
                bibs[idx].update_content(bib)
            elif s != "":
                new[i].key = s
                new[i].content.replace(bib.key, s)
                keep[i] = True
    new = [bib for bib,keeper in zip(new,keep) if keeper]

    # Different key, same title:
    keep = np.zeros(len(new), bool)
    bm_titles = [bib.title for bib in bibs]
    for i,bib in enumerate(new):
        if bib.title not in bm_titles or bib.title is None:
            keep[i] = True
            continue
        idx = bm_titles.index(bib.title)
        display_bibs(["DATABASE:\n", "NEW:\n"], [bibs[idx], bib])
        s = u.req_input(
            "Possible duplicate, same title but keys differ, "
            "[]ignore new, [r]eplace database with new, or [a]dd new: ",
            options=["", "r", "a"])
        if s == "r":
            bibs[idx].update_content(bib)
        elif s == "a":
            keep[i] = True
    new = [bib for bib,keeper in zip(new,keep) if keeper]

    # Add all new entries and sort:
    bibs = sorted(bibs + new)
    print(f"\nMerged {len(new)} new entries.")

    if base is None:
        save(bibs)
        export(bibs, meta=True)

    return bibs


def init(bibfile=None, reset_db=True, reset_config=False):
    """
    Initialize bibmanager, reset database entries and config parameters.

    Parameters
    ----------
    bibfile: String
        A bibfile to include as the new bibmanager database.
        If None, reset the bibmanager database with a clean slate.
    reset_db: Bool
        If True, reset the bibmanager database.
    reset_config: Bool
        If True, reset the config file.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> import os
    >>> bibfile = os.path.expanduser("~") + "/.bibmanager/examples/sample.bib"
    >>> bm.init(bibfile)
    """
    # First install ever:
    if not os.path.exists(u.HOME):
        os.mkdir(u.HOME)
    if not os.path.exists(u.HOME+'pdf/'):
        os.mkdir(u.HOME+'pdf/')

    # Copy examples folder:
    shutil.rmtree(u.HOME+'examples/', ignore_errors=True)
    shutil.copytree(u.ROOT+'examples/', u.HOME+'examples/')

    # Make sure config exists before working with the database:
    if reset_config:
        with u.ignored(OSError):
            os.remove(u.HOME+'config')
    cm.update_keys()

    if reset_db:
        if bibfile is None:
            for bm_file in [u.BM_DATABASE(), u.BM_BIBFILE()]:
                with u.ignored(OSError):
                    os.remove(bm_file)
        else:
            bibs = read_file(bibfile)
            save(bibs)
            export(bibs, meta=True)


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
    style = prompt_toolkit.styles.style_from_pygments_cls(
        pygments.styles.get_style_by_name(cm.get('style')))
    newbibs = prompt_toolkit.prompt(
        "Enter a BibTeX entry (press META+ENTER or ESCAPE ENTER when done):\n",
        multiline=True, lexer=lexer, style=style)
    new = read_file(text=newbibs)

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
    export(load(), u.BM_TMP_BIB(), meta=True)
    # Open database.bib into temporary file with default text editor
    if sys.platform == "win32":
        os.startfile(u.BM_TMP_BIB())
    else:
        opener = cm.get('text_editor')
        if opener == 'default':
            opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, u.BM_TMP_BIB()])
    # Launch input() call to wait for user to save edits:
    dummy = input(
        "Press ENTER to continue after you edit, save, and close "
        "the bib file.")
    # Check edits:
    try:
        new = read_file(u.BM_TMP_BIB())
    finally:
        # Always delete the tmp file:
        os.remove(u.BM_TMP_BIB())
    # Update database if everything went fine:
    with u.ignored(OSError):
        os.remove(u.BM_DATABASE())
    merge(new=new)


def search(authors=None, year=None, title=None, key=None, bibcode=None):
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
    key: String or list of strings
        Match any entry whose key is in the input key.
    bibcode: String or list of strings
        Match any entry whose bibcode is in the input bibcode.

    Returns
    -------
    matches: List of Bib() objects
        Entries that match all input criteria.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> # Search by last name:
    >>> matches = bm.search(authors="Cubillos")
    >>> # Search by last name and initial:
    >>> matches = bm.search(authors="Cubillos, P")
    >>> # Search by author in given year:
    >>> matches = bm.search(authors="Cubillos, P", year=2017)
    >>> # Search by first author and co-author (using AND logic):
    >>> matches = bm.search(authors=["^Cubillos", "Blecic"])
    >>> # Search by keyword in title:
    >>> matches = bm.search(title="Spitzer")
    >>> # Search by keywords in title (using AND logic):
    >>> matches = bm.search(title=["HD 189", "HD 209"])
    >>> # Search by key (note that unlike the other fields, key and
    >>> # bibcode use OR logic, so you can get many items at once):
    >>> matches = bm.search(key="Astropycollab2013aaAstropy")
    >>> # Search by bibcode (note no need to worry about UTF-8 encoding):
    >>> matches = bm.search(bibcode=["2013A%26A...558A..33A",
    >>>                              "1957RvMP...29..547B",
    >>>                              "2017AJ....153....3C"])
    """
    matches = load()

    if year is not None:
        if isinstance(year, int):
            matches = [bib for bib in matches if bib.year == year]
        else: # Assume year = [from_year, to_year]
            matches = [
                bib for bib in matches
                if bib.year is not None
                if bib.year >= year[0]
            ]
            matches = [
                bib for bib in matches
                if bib.year is not None
                if bib.year <= year[1]
            ]

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
            matches = [
                bib for bib in matches
                if bib.title is not None
                if word.lower() in bib.title.lower()
            ]

    if key is not None:
        if isinstance(key, str):
            key = [key]
        elif not isinstance(key, (list, tuple, np.ndarray)):
            raise ValueError("Invalid input format for 'key'.")
        matches = [bib for bib in matches if bib.key in key]

    if bibcode is not None:
        if isinstance(bibcode, str):
            bibcode = [bibcode]
        elif not isinstance(bibcode, (list, tuple, np.ndarray)):
            raise ValueError("Invalid input format for 'bibcode'.")
        # Take care of encoding:
        bibcode = [urllib.parse.unquote(b) for b in bibcode]
        matches = [bib for bib in matches if bib.bibcode in bibcode]

    return matches


def prompt_search(keywords, field, prompt_text):
    r"""
    Do an interactive prompt search in the Bibmanager database by
    the given keywords, with auto-complete and auto-suggest only
    offering non-None values of the given field.
    Only one keyword must be set in the prompt.
    A bottom toolbar dynamically shows additional info.

    Parameters
    ----------
    keywords: List of strings
        BibTex keywords to search by.
    field: String
        Filtering BibTex field for auto-complete and auto-suggest.
    prompt_text: String
        Text to display when launching the prompt.

    Returns
    -------
    kw_input: List of strings
        List of the parsed input (same order as keywords).
        Items are None for the keywords not defined.
    extra: List of strings
        Any further word written in the prompt.

    Examples
    --------
    >>> import bibmanager.bib_manager as bm
    >>> # Search by key or bibcode, of entries with non-None bibcode:
    >>> keywords = ['key', 'bibcode']
    >>> field = 'bibcode'
    >>> prompt_text = ("Sample search  (Press 'tab' for autocomplete):\n")
    >>> prompt_input = bm.prompt_search(keywords, field, prompt_text)
    Sample search  (Press 'tab' for autocomplete):
    key: Astropy2013aaAstroPy
    >>> # Look at the results (list corresponds to [key, bibcode]):
    >>> print(prompt_input[0])
    ['Astropy2013aaAstroPy', None]
    >>> print(f'extra = {prompt_input[1]}')
    extra = [None]

    >>> # Repeat search, now by bibcode:
    >>> prompt_input = u.prompt_search(keywords, field, prompt_text)
    Sample search  (Press 'tab' for autocomplete):
    bibcode: 2013A&A...558A..33A
    >>> print(prompt_input[0])
    [None, '2013A&A...558A..33A']
    """
    bibs = [bib for bib in load() if getattr(bib,field) is not None]
    fetch_keywords = [f'{keyword}:' for keyword in keywords]
    completer = u.KeyPathCompleter(fetch_keywords, bibs)
    suggester = u.AutoSuggestKeyCompleter()
    validator = u.AlwaysPassValidator(bibs,
        toolbar_text=f"(Press 'tab' for autocomplete)")

    session = prompt_toolkit.PromptSession(
        history=FileHistory(u.BM_HISTORY_PDF()))

    inputs = session.prompt(
        prompt_text,
        auto_suggest=suggester,
        completer=completer,
        complete_while_typing=False,
        validator=validator,
        validate_while_typing=True,
        bottom_toolbar=validator.bottom_toolbar,
        )

    kw_input = [
        re.search(fr'(?:^|[\s]+){kw}[\s]*(.+)', inputs)
        for kw in fetch_keywords
    ]
    # Only one of these keywords should be defined:
    output = [val is not None for val in kw_input]
    if sum(output) != 1:
        raise ValueError("Invalid syntax.")

    index = output.index(True)
    content = kw_input[index].group(1).split()
    if content == []:
        raise ValueError("Invalid syntax.")
    kw_input[index] = content[0]
    extra = content[1:] if len(content) > 1 else [None]
    return kw_input, extra

