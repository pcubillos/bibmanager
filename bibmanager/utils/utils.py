# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = [
    # Constants:
    'HOME',
    'ROOT',
    'BOLD',
    'END',
    'BANNER',
    'search_keywords',
    'ads_keywords',
    # Pseudo-constants:
    'BM_DATABASE',
    'BM_BIBFILE',
    'BM_TMP_BIB',
    'BM_CACHE',
    'BM_HISTORY_SEARCH',
    'BM_HISTORY_ADS',
    'BM_HISTORY_PDF',
    'BM_PDF',
    # Named tuples:
    'Author',
    'Sort_author',
    # Context managers:
    'ignored',
    'cd',
    # Functions:
    'ordinal',
    'count',
    'nest',
    'cond_split',
    'cond_next',
    'find_closing_bracket',
    'parse_name',
    'repr_author',
    'purify',
    'initials',
    'get_authors',
    'next_char',
    'last_char',
    'get_fields',
    'req_input',
    'warnings_format',
    # Classes:
    'AutoSuggestCompleter',
    'AutoSuggestKeyCompleter',
    'KeyWordCompleter',
    'KeyPathCompleter',
    'AlwaysPassValidator',
    ]

import os
import re
import warnings
from collections import namedtuple
from contextlib import contextmanager

import numpy as np
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.completion import WordCompleter, PathCompleter, Completion
from prompt_toolkit.validation import Validator

from .. import config_manager as cm


# Directories/files:
HOME = os.path.expanduser('~') + '/.bibmanager/'
ROOT = os.path.realpath(os.path.dirname(__file__) + '/..') + '/'

# Unicode to start/end bold-face syntax:
BOLD = '\033[1m'
END  = '\033[0m'

# A delimiter:
BANNER = "\n" + ":"*70 + "\n"


# Pseudo-constants:
def BM_DATABASE():
    """The database of BibTex entries"""
    return cm.get('home') + 'bm_database.pickle'

def BM_BIBFILE():
    """Bibfile representation of the database"""
    return cm.get('home') + 'bm_bibliography.bib'

def BM_TMP_BIB():
    """Temporary bibfile database for editing"""
    return cm.get('home') + 'tmp_bibliography.bib'

def BM_CACHE():
    """ADS queries cache"""
    return cm.get('home') + 'cached_ads_query.pickle'

def BM_HISTORY_SEARCH():
    """Search history"""
    return cm.get('home') + 'history_search'

def BM_HISTORY_ADS():
    """ADS search history"""
    return cm.get('home') + 'history_ads_search'

def BM_HISTORY_PDF():
    """PDF search history"""
    return cm.get('home') + 'history_pdf_search'

def BM_PDF():
    """Folder for PDF files of the BibTex entries"""
    return cm.get('home') + 'pdf/'


# Named tuples:
Author = namedtuple("Author", "last first von jr")
Sort_author = namedtuple("Sort_author", "last first von jr year month")


# Completer keywords:
search_keywords = [
    'author:"^"',
    'author:""',
    'year:',
    'title:""',
    'key:',
    'bibcode:',
    ]

# For more info, see  https://adsabs.github.io/help/search/search-syntax
ads_keywords = [
    # First seven show on 'tab' hit:
    'author:"^"',
    'author:""',
    'year:',
    'title:""',
    'abstract:""',
    'property:refereed',
    'property:article',
    # Sort the rest alphabetically:
    'abs:""',
    'ack:""',
    'aff:""',
    'arXiv:',
    'arxiv_class:""',
    'bibcode:',
    'bibgroup:""',
    'bibstem:',
    'body:""',
    'citations()',
    'copyright:',
    'data:""',
    'database:astronomy',
    'database:physics',
    'doctype:abstract',
    'doctype:article',
    'doctype:book',
    'doctype:bookreview',
    'doctype:catalog',
    'doctype:circular',
    'doctype:eprint',
    'doctype:erratum',
    'doctype:inproceedings',
    'doctype:inbook',
    'doctype:mastersthesis',
    'doctype:misc',
    'doctype:newsletter',
    'doctype:obituary',
    'doctype:phdthesis',
    'doctype:pressrelease',
    'doctype:proceedings',
    'doctype:proposal',
    'doctype:software',
    'doctype:talk',
    'doctype:techreport',
    'doi:',
    'full:""',
    'grant:',
    'identifier:""',
    'issue:',
    'keyword:""',
    'lang:""',
    'object:""',
    'orcid:',
    'page:',
    'property:ads_openaccess',
    'property:eprint',
    'property:eprint_openaccess',
    'property:inproceedings',
    'property:non_article',
    'property:notrefereed',
    'property:ocrabstract',
    'property:openaccess',
    'property:pub_openaccess',
    'property:software',
    'references()',
    'reviews()',
    'similar()',
    'topn()',
    'trending()',
    'useful()',
    'vizier:""',
    'volume:',
    ]

# Context managers:
@contextmanager
def ignored(*exceptions):
    """
    Context manager to ignore exceptions. Taken from here:
    https://www.youtube.com/watch?v=anrOzOapJ2E
    """
    try:
        yield
    except exceptions:
        pass


@contextmanager
def cd(newdir):
    """
    Context manager for changing the current working directory.
    Taken from here: https://stackoverflow.com/questions/431684/
    """
    olddir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(olddir)


# Functions:
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
    >>> from bibmanager.utils import ordinal
    >>> print(ordinal(1))
    1st
    >>> print(ordinal(2))
    2nd
    >>> print(ordinal(11))
    11th
    >>> print(ordinal(111))
    111th
    >>> print(ordinal(121))
    121st
    >>> print(ordinal(np.arange(1,6)))
    ['1st', '2nd', '3rd', '4th', '5th']
    """
    ending = ["th", "st", "nd", "rd"]
    unit = number % 10
    teen = (number//10) % 10 != 1
    idx = unit * (unit<4) * teen
    if type(number) is int:
        return f"{number}{ending[idx]}"
    return [f"{n}{ending[i]}" for n,i in zip(number,idx)]


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
    >>> from bibmanager.utils import count
    >>> count('{Hello} world')
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
    >>> from bibmanager.utils import nest
    >>> s = "{{P\\'erez}, F. and {Granger}, B.~E.},"
    >>> n = nest(s)
    >>> print(f"{s}\n{''.join([str(v) for v in n])}")
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
    >>> from bibmanager.utils import cond_split
    >>> # Split an author list string delimited by ' and ' pattern:
    >>> cond_split("{P\\'erez}, F. and {Granger}, B.~E.", " and ")
    ["{P\\'erez}, F.", '{Granger}, B.~E.']
    >>> # Protected instances (within braces) won't count:
    >>> cond_split("{AAS and Astropy Teams} and {Hendrickson}, A.", " and ")
    ['{AAS and Astropy Teams}', '{Hendrickson}, A.']
    >>> # Matches at the beginning or end do not count for split:
    >>> cond_split(",Jones, Oliphant, Peterson,", ",")
    ['Jones', ' Oliphant', ' Peterson']
    >>> # But two consecutive matches do return an empty string:
    >>> cond_split("Jones,, Peterson", ",")
    ['Jones', '', ' Peterson']
    """
    if nested is None:
        nested = nest(text)

    if nlev == -1 and len(nested) > 0:
        nlev = nested[0]

    # First and last indices of each pattern match:
    bounds = [
        (m.start(0), m.end(0))
        for m in re.finditer(pattern, text, re.IGNORECASE)
        if nested[m.start(0)] == nlev]

    flat_bounds = [item for sublist in bounds for item in sublist]

    # No matches:
    if len(flat_bounds) == 0:
        if ret_nests:
            return [text], [nested]
        return [text]

    # Beginning and end of substrings at the ends of the input:
    flat_bounds.insert(0, 0)
    flat_bounds.append(len(text))

    # Matches, parse substrings:
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
    >>> from bibmanager.utils import nest, cond_next
    >>> text = '"{{HITEMP}, the high-temperature molecular database}",'
    >>> nested = nest(text)
    >>> # Ignore comma within braces:
    >>> cond_next(text, ",", nested, nlev=0)
    53
    """
    if len(text) == 0:
        return 0

    for m in re.finditer(pattern, text):
        if nested[m.start(0)] == nlev:
            return m.start(0)
    # If not found, return last index in text:
    return len(text) - 1


def find_closing_bracket(text, start_pos=0, get_open=False):
    """
    Find the closing bracket that matches the nearest opening bracket in
    text starting from start_pos.

    Parameters
    ----------
    text: String
        Text to search through.
    start_pos: Integer
        Starting position where to start looking for the brackets.
    get_opening: Bool
        If True, return a tuple with the position of both
        opening and closing brackets.

    Returns
    -------
    end_pos: Integer
        The absolute position to the cursor position at closing bracket.
        Returns None if there are no matching brackets.

    Examples
    --------
    >>> import bibmanager.utils as u
    >>> text = '@ARTICLE{key, author={last_name}, title={The Title}}'
    >>> end_pos = u.find_closing_bracket(text)
    >>> print(text[:end_pos+1])
    @ARTICLE{key, author={last_name}, title={The Title}}

    >>> start_pos = 14
    >>> end_pos = find_closing_bracket(text, start_pos=start_pos)
    >>> print(text[start_pos:end_pos+1])
    author={last_name}
    """
    left_bracket = text[start_pos:].find('{')
    if left_bracket < 0:
        return None
    start_pos += left_bracket + 1
    end_pos = len(text)

    stack = 1
    for index,char in enumerate(text[start_pos:end_pos]):
        if char == '{':
            stack += 1
        elif char == '}':
            stack -= 1

        if stack == 0:
            if get_open:
                return left_bracket, start_pos + index
            return start_pos + index
    return None


#@functools.lru_cache(maxsize=1024, typed=False)
def parse_name(name, nested=None, key=None):
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
    key: Sting
        The entry that contains this author name (to display in case of
        a warning).

    Returns
    -------
    author: Author namedtuple
        Four element tuple with the parsed name.

    Examples
    --------
    >>> from bibmanager.utils import parse_name
    >>> names = ['{Hendrickson}, A.',
    >>>          'Eric Jones',
    >>>          '{AAS Journals Team}',
    >>>          "St{\\'{e}}fan van der Walt"]
    >>> for name in names:
    >>>     print(f'{repr(name)}:\n{parse_name(name)}\n')
    '{Hendrickson}, A.':
    Author(last='{Hendrickson}', first='A.', von='', jr='')

    'Eric Jones':
    Author(last='Jones', first='Eric', von='', jr='')

    '{AAS Journals Team}':
    Author(last='{AAS Journals Team}', first='', von='', jr='')

    "St{\\'{e}}fan van der Walt":
    Author(last='Walt', first="St{\\'{e}}fan", von='van der', jr='')
    """
    if nested is None:
        nested = nest(name)
    name = " ".join(cond_split(name, "~", nested=nested))
    fields, nests = cond_split(name, ",", nested=nested, ret_nests=True)
    if len(fields) > 3:
        warnings.formatwarning = warnings_format
        warning_text = f"Too many commas in name '{name}'"
        if key is not None:
            warning_text += f" for entry '{key}'"
        warnings.warn(warning_text)
        # LaTeX seems to interpret extra content as middle names:
        fields = [fields[0], ' '.join(fields[1:])]
        nests = [nests[0], nest(fields[1])]

    # 'First von Last' format:
    if len(fields) == 1:
        jr = ""
        words = [
            word
            for word in cond_split(fields[0], " ", nested=nests[0])
            if word != ""]
        lowers = [s[0].islower() for s in words[:-1]]
        if np.any(lowers):
            ifirst = np.min(np.where(lowers))
            ilast  = np.max(np.where(lowers)) + 1
        else:
            ifirst = ilast = len(words) - 1
        # Join words, then collapse blanks:
        first = " ".join(words[0:ifirst])
        first = " ".join(first.split())
        von   = " ".join(words[ifirst:ilast])
        von   = " ".join(von.split())
        last  = " ".join(words[ilast:])
        last  = " ".join(last.split())

    else:
        vonlast = fields[0]
        if vonlast.strip() == "":
            raise ValueError(
                f"Invalid BibTeX format for author '{name}', it "
                "does not have a last name.")

        # 'von Last, First' format:
        if len(fields) == 2:
            jr = ""
            first = " ".join(fields[1].split())

        # 'von Last, Jr, First' format:
        elif len(fields) == 3:
            jr    = " ".join(fields[1].split())
            first = " ".join(fields[2].split())

        words = [
            word
            for word in cond_split(vonlast, " ", nested=nests[0])
            if word != ""]
        lowers = [s[0].islower() for s in words[:-1]]

        if np.any(lowers):
            ilast = np.max(np.where(lowers)) + 1
            von = " ".join(words[:ilast])
        else:
            von = ""
            ilast = 0
        last = " ".join(words[ilast:])
        last = " ".join(last.split())
    return Author(last=last, first=first, von=von, jr=jr)


def repr_author(Author):
    """
    Get string representation of an Author namedtuple in the format:
    von Last, jr., First.

    Parameters
    ----------
    Author: An Author() namedtuple
        An author name.

    Examples
    --------
    >>> from bibmanager.utils import repr_author, parse_name
    >>> names = ['Last', 'First Last', 'First von Last', 'von Last, First',
    >>>          'von Last, sr., First']
    >>> for name in names:
    >>>     print(f"{name!r:22}: {repr_author(parse_name(name))}")
    'Last'                : Last
    'First Last'          : Last, First
    'First von Last'      : von Last, First
    'von Last, First'     : von Last, First
    'von Last, sr., First': von Last, sr., First
    """
    name = Author.last
    if Author.von != "":
        name = " ".join([Author.von, name])
    if Author.jr != "":
        name += f", {Author.jr}"
    if Author.first != "":
        name += f", {Author.first}"
    return name


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
    >>> from bibmanager.utils import purify
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
    >>>     print(f"{name!r:35}: {purify(name)}")
    "St{\\'{e}}fan"                     : stefan
    "{{\\v S}ime{\\v c}kov{\\'a}}"      : simeckova
    '{AAS Journals Team}'               : aas journals team
    "Kov{\\'a}{\\v r}{\\'i}k"           : kovarik
    "Jarom{\\'i}r Kov{\\'a\\v r\\'i}k"  : jaromir kovarik
    '{\\.I}volgin'                      : ivolgin
    'Gon{\\c c}alez Nu{\\~n}ez'         : goncalez nunez
    'Knausg{\\aa}rd Sm{\\o}rrebr{\\o}d' : knausgaard smorrebrod
    'Schr{\\"o}dinger Be{\\ss}er'       : schrodinger besser
    """
    # German umlaut replace:
    if german:
        for pattern in ["a", "o", "u"]:
            name = re.sub(fr'\\"{pattern}', pattern+"e", name)
    # Remove special:
    name = re.sub(r"\\(\"|\^|`|\.|'|~)", "", name)
    # Remove special + white space:
    name = re.sub(r"\\(c |u |H |v |d |b |t )", "",  name)
    # Remove special + braces:
    name = re.sub(r"\\(c{|u{|H{|v{|d{|b{|t{)", "{", name)
    # Replace pattern:
    for pattern in [
        "o", "O", "l", "L", "i", "j", "aa", "AA", "AE", "oe", "OE", "ss"]:
        name = re.sub(fr"\\{pattern}", pattern, name)
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
    >>> from bibmanager.utils import initials
    >>> names = ["", "D.", "D. W.", "G.O.", '{\\"O}. H.', "J. Y.-K.",
    >>>          "Phil", "Phill Henry Scott"]
    >>> for name in names:
    >>>     print(f"{name!r:20}: {initials(name)!r}")
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


def get_authors(authors, format='long'):
    """
    Get string representation for the author list.

    Parameters
    ----------
    authors: List of Author() nametuple
    format: String
        If format='ushort', display only the first author's last name,
            followed by a '+' if there are more authors.
        If format='short', display at most the first two authors followed
            by 'et al.' if corresponds.
        Else, display the full list of authors.

    Returns
    -------
    author_list: String
        String representation of the author list in the requested format.

    Examples
    --------
    >>> from bibmanager.utils import get_authors, parse_name
    >>> author_lists = [
    >>>     [parse_name('{Hunter}, J. D.')],
    >>>     [parse_name('{AAS Journals Team}'), parse_name('{Hendrickson}, A.')],
    >>>     [parse_name('Eric Jones'), parse_name('Travis Oliphant'),
    >>>      parse_name('Pearu Peterson')]
    >>>    ]
    >>> # Ultra-short format:
    >>> for i,authors in enumerate(author_lists):
    >>>     print(f"{i+1} author(s): {get_authors(authors, format='ushort')}")
    1 author(s): Hunter
    2 author(s): AAS Journals Team+
    3 author(s): Jones+

    >>> # Short format:
    >>> for i,authors in enumerate(author_lists):
    >>>     print(f"{i+1} author(s): {get_authors(authors, format='short')}")
    1 author(s): {Hunter}, J. D.
    2 author(s): {AAS Journals Team} and {Hendrickson}, A.
    3 author(s): Jones, Eric; et al.

    >>> # Long format:
    >>> for i,authors in enumerate(author_lists):
    >>>     print(f"{i+1} author(s): {get_authors(authors)}")
    1 author(s): {Hunter}, J. D.
    2 author(s): {AAS Journals Team} and {Hendrickson}, A.
    3 author(s): Jones, Eric; Oliphant, Travis; and Peterson, Pearu
    """
    if authors is None:
        return ''

    if format == "ushort":
        # Remove characters except letters, spaces, dashes, and parentheses:
        last = re.sub("[^\w\s\-\(\)]", "", authors[0].last)
        if len(authors) > 1:
            last = f"{last}+"
        return last

    if len(authors) <= 2:
        return " and ".join([repr_author(author) for author in authors])

    if format != 'short':
        author_list = [repr_author(author) for author in authors]
        authors = "; ".join(author_list[:-1])
        return authors + "; and " + author_list[-1]
    else:
        return repr_author(authors[0]) + "; et al."


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
    >>> from bibmanager.utils import next_char
    >>> texts = ["Hello", "  Hello", "  Hello ", "", "\n Hello", "  "]
    >>> for text in texts:
    >>>     print(f"{text!r:11}: {next_char(text)}")
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
        Any string.

    Returns
    -------
    index: Integer
        Index of last non-blank character.

    Examples
    --------
    >>> from bibmanager.utils import last_char
    >>> texts = ["Hello", "  Hello", "  Hello  ", "", "\n Hello", "  "]
    >>> for text in texts:
    >>>     print(f"{text!r:12}: {last_char(text)}")
    'Hello'     : 5
    '  Hello'   : 7
    '  Hello  ' : 7
    ''          : 0
    '\n Hello'  : 7
    '  '        : 0
    """
    index = len(text)
    if index == 0:
        return 0
    while text[index-1].isspace() and index > 0:
        index -= 1
    return index


def get_fields(entry):
    r"""
    Generator to parse entries of a bibliographic entry.

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
    >>> from bibmanager.utils import get_fields
    >>> entry = '''
    @Article{Hunter2007ieeeMatplotlib,
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
    >>> fields = get_fields(entry)
    >>> # Get the entry's key:
    >>> print(next(fields))
    Hunter2007ieeeMatplotlib

    >>> # Now get the fields, values, and nested level:
    >>> for key, value, nested in fields:
    >>>   print(f"{key:9}: {value}\n{'':11}{''.join([str(v) for v in nested])}")
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
    loc = entry.index(",")
    yield entry[start:loc]
    loc += 1

    # Next equal sign delimits key:
    while entry[loc:].find("=") >= 0:
        eq = entry[loc:].find("=")
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


def req_input(prompt, options):
    """
    Query for an answer to prompt message until the user provides a
    valid input (i.e., answer is in options).

    Parameters
    ----------
    prompt: String
        Prompt text for input()'s argument.
    options: List
        List of options to accept.  Elements in list are cast into strings.

    Returns
    -------
    answer: String
        The user's input.

    Examples
    --------
    >>> from bibmanager.utils import req_input
    >>> req_input('Enter number between 0 and 9: ', options=np.arange(10))
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


def warnings_format(message, category, filename, lineno, file=None, line=None):
    """Custom format for warnings."""
    return f'Warning: {message}\n'


class AutoSuggestCompleter(AutoSuggest):
    """Give suggestions based on the words in WordCompleter."""
    def get_suggestion(self, buffer, document):
        completer = buffer.completer.get_completer()
        # Consider only the last line for the suggestion.
        text = document.text.rsplit('\n', 1)[-1]
        # Consider only last word:

        for tw in text.split():
            for kw in completer.words:
               if tw.startswith(kw):
                   text = text.replace(kw, f'{kw} ')

        # Make the last word a '' if text ends with a space:
        text_words = text.split()
        if len(text) == 0 or text[-1].isspace():
            text_words.append('')
        nwords = len(text_words)
        text = text_words[-1]
        completer.bottom = text

        # Only create a suggestion when this is not an empty line.
        if text.strip():
            # Find first matching line in history.
            for string in completer.words:
                for line in reversed(string.splitlines()):
                    if line.startswith(text):
                        return Suggestion(line[len(text):])


class KeyWordCompleter(WordCompleter):
    def __init__(self, words, bibs):
        super().__init__(words)
        self.bibs = bibs

    def get_completions(self, document, complete_event):
        """Get right key/option completions."""
        text = document.text.rsplit('\n', 1)[-1]
        # Insert a space after colon if there is a 'key':
        for tw in text.split():
            for kw in self.words:
               if tw.startswith(kw):
                   text = text.replace(kw, f'{kw} ')

        # Make the last word a '' if text ends with a space:
        text_words = text.split()
        if len(text) == 0 or text[-1].isspace():
            text_words.append('')
        nwords = len(text_words)
        text = text_words[-1]

        if nwords > 1 and text_words[-2] in self.words \
                and text_words[-2].endswith(':'):
            key = text_words[-2]
        else:
            key = ''

        # List of words to match against:
        if key in self.words:
            try:
                options = np.unique([
                    str(getattr(bib,key[:-1]))
                    for bib in self.bibs
                    if getattr(bib,key[:-1]) is not None])
            except:
                return
        else:
            options = self.words

        for word in options:
            # True when the word before the cursor matches.
            if word.startswith(text):
                display_meta = self.meta_dict.get(word, "")
                yield Completion(word, -len(text), display_meta=display_meta)


class KeyPathCompleter(WordCompleter, PathCompleter):
    def __init__(self, words, bibs):
        WordCompleter.__init__(self, words)
        PathCompleter.__init__(self, min_input_len=0, expanduser=True)
        self.bibs = bibs

    def get_completions(self, document, complete_event):
        """Get right key/option/file completions."""
        text = document.text.rsplit('\n', 1)[-1]
        # Insert a space after colon if there is a 'key':
        for tw in text.split():
            for kw in self.words:
               if tw.startswith(kw):
                   text = text.replace(kw, f'{kw} ')

        # Make the last word a '' if text ends with a space:
        text_words = text.split()
        if len(text) == 0 or text[-1].isspace():
            text_words.append('')
        nwords = len(text_words)
        text = text_words[-1]

        if nwords>1 and text_words[-2] in self.words:
            key = text_words[-2]
        elif nwords>2 and text_words[-3] in self.words:
            key = None
            if text_words[-1] == '':
                text = './'
        else:
            key = ''

        if key is None:
            yield from self.path_completions(text)
            return

        # List of words to match against:
        if key in self.words:
            try:
                options = np.unique([
                    str(getattr(bib,key[:-1]))
                    for bib in self.bibs
                    if getattr(bib,key[:-1]) is not None])
            except:
                return
        else:
            options = self.words

        for word in options:
            # True when the word before the cursor matches.
            if word.startswith(text):
                display_meta = self.meta_dict.get(word, "")
                yield Completion(word, -len(text), display_meta=display_meta)

    def path_completions(self, text):
        """Slightly modified from PathCompleter.get_completions()"""
        if len(text) < self.min_input_len:
            return
        try:
            text = os.path.expanduser(text)
            if os.path.dirname(text):
                directories = [
                    os.path.dirname(os.path.join(p, text))
                    for p in self.get_paths()]
            else:
                directories = self.get_paths()

            # Start of current file.
            prefix = os.path.basename(text)
            # Get all filenames except hidden files.
            filenames = [
                (directory, filename)
                for directory in directories
                for filename in os.listdir(directory)
                if os.path.isdir(directory)
                if filename.startswith(prefix) and not filename.startswith('.')
                ]

            # Sort
            filenames = sorted(filenames, key=lambda k: k[1])
            # Yield them.
            for directory, filename in filenames:
                completion = filename[len(prefix):]
                full_name = os.path.join(directory, filename)
                if os.path.isdir(full_name):
                    filename += "/"
                elif self.only_directories:
                    continue
                if not self.file_filter(full_name):
                    continue
                yield Completion(completion, 0, display=filename)
        except OSError:
            pass


class AutoSuggestKeyCompleter(AutoSuggest):
    """Give suggestions based on the words in WordCompleter."""
    def get_suggestion(self, buffer, document):
        completer = buffer.completer.get_completer()
        # Consider only the last line for the suggestion.
        text = document.text.rsplit('\n', 1)[-1]
        # Only create a suggestion when this is not an empty line.
        if text == '' or text[-1].isspace() or text[-1] == ':':
            return

        # Consider only two last words:
        words = text.split()
        if ':' in words[-1]:
            key, word = words[-1].split(':')[-2:]
            key = key + ':'
        elif len(words) > 1:
            key, word = words[-2:]
        else:
            key, word = '', words[-1]

        if key in completer.words:
            options = np.unique([
                str(getattr(bib,key[:-1]))
                for bib in completer.bibs
                if getattr(bib,key[:-1]) is not None])
        else:
            options = completer.words

        # Find first matching line in history.
        for string in options:
            for line in reversed(string.splitlines()):
                if line.startswith(word):
                    return Suggestion(line[len(word):])


class AlwaysPassValidator(Validator):
    """Validator that always passes (using actually for bottom toolbar)."""
    def __init__(self, bibs, toolbar_text=''):
        super().__init__()
        self.bibs = bibs
        self.keys = [bib.key for bib in bibs]
        self.pdfs = [bib.pdf for bib in bibs]
        self.bibcodes = [bib.bibcode for bib in bibs]
        self.default_toolbar_text = toolbar_text
        self.toolbar_text = self.default_toolbar_text

    def validate(self, document):
        text_words = document.text.split()
        # Null text:
        if text_words == []:
            self.toolbar_text = self.default_toolbar_text
            return True

        text = text_words[-1]
        if ':' in text:
            text = text.split(':')[-1]

        if text in self.keys:
            bib = self.bibs[self.keys.index(text)]
        elif text in self.pdfs:
            bib = self.bibs[self.pdfs.index(text)]
        elif text in self.bibcodes:
            bib = self.bibs[self.bibcodes.index(text)]
        else:
            bib = None

        if bib is None:
            self.toolbar_text = self.default_toolbar_text
        else:
            year = '' if bib.year is None else bib.year
            title = 'NO_TITLE' if bib.title is None else bib.title
            self.toolbar_text = f"{bib.get_authors('ushort')}{year}: {title}"
        return True

    def bottom_toolbar(self):
        return self.toolbar_text

