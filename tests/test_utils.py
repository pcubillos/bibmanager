# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

import numpy as np
import pytest

from pygments.token import Token
import bibmanager.utils as u


def test_ordinal():
    assert u.ordinal(1) == "1st"
    assert u.ordinal(2) == "2nd"
    assert u.ordinal(3) == "3rd"
    assert u.ordinal(4) == "4th"
    assert u.ordinal(11) == "11th"
    assert u.ordinal(21) == "21st"
    assert u.ordinal(111) == "111th"
    assert u.ordinal(121) == "121st"
    assert u.ordinal(np.arange(1,6)) == ["1st", "2nd", "3rd", "4th", "5th"]

def test_count():
    assert u.count("") == 0
    assert u.count("{Hello} world") == 0
    assert u.count("@article{key,\n") == 1


def test_nest():
    np.testing.assert_array_equal(u.nest(""), np.zeros(0,dtype=int))
    np.testing.assert_array_equal(u.nest("abc"), np.array([0,0,0]))
    np.testing.assert_array_equal(u.nest("\\n"), np.array([0,0]))
    np.testing.assert_array_equal(u.nest("{a}"), np.array([0,1,1]))
    np.testing.assert_array_equal(
        u.nest("{{P\\'erez}, F. and {Granger}, B.~E.},"),
        np.array([0,1,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,
                  2,2,2,1,1,1,1,1,1,1,1,0]))


def test_cond_split1():
    assert u.cond_split("", ",") == [""]
    assert u.cond_split("abcd",      ",") == ["abcd"]
    assert u.cond_split("ab,cd",     ",") == ["ab", "cd"]
    assert u.cond_split(",a,b,c,d,", ",") == ["", "a", "b", "c", "d", ""]
    assert u.cond_split("a,,b,c,d",  ",") == ["a", "", "b", "c", "d"]
    assert u.cond_split("{a,b,c,d}", ",") == ["{a,b,c,d}"]
    assert u.cond_split("a,{b,c},d", ",") == ['a', '{b,c}', 'd']


def test_cond_split2():
    assert u.cond_split("a and b and c", "and")   == ['a ', ' b ', ' c']
    assert u.cond_split("a and b and c", " and ") == ['a', 'b', 'c']


def test_cond_split3():
    assert u.cond_split("a,b,c", ",", nested=[0,0,0,0,0]) == ['a', 'b', 'c']
    assert u.cond_split("a,b,c", ",", nested=[1,1,1,1,1]) == ['a', 'b', 'c']
    # Note 'nested' is inconsistent with 'text', this cases if for
    #      testing purposes only:
    assert u.cond_split("a,b,c", ",", nested=[0,1,1,1,1]) == ['a,b,c']
    assert u.cond_split("{P\\'erez}, F. and {Granger}, B.~E.", " and ") \
           == ["{P\\'erez}, F.", '{Granger}, B.~E.']


@pytest.mark.parametrize('and_texts', (
    ['and', 'and'],
    ['And', 'and'],
    ['AND', 'and'],
    ['and', 'AND']))
def test_cond_split_ignore_case(and_texts):
    assert u.cond_split(
        f"a {and_texts[0]} b",
        f" {and_texts[1]} ") == ['a', 'b']


def test_cond_next1():
    # Empty string:
    text = ""
    nested = u.nest(text)
    assert u.cond_next(text, ",", nested, nested[0:1]) == 0
    # Pattern not found in text, return last index:
    text = "ab"
    nested = u.nest(text)
    assert u.cond_next(text, ",", nested, nested[0]) == 1
    text = "abcd"
    nested = u.nest(text)
    assert u.cond_next(text, ",", nested, nested[0]) == 3

def test_cond_next2():
    # Get position:
    text = ",ab"
    nested = u.nest(text)
    assert u.cond_next(text, ",", nested, nested[0]) == 0
    text = "a,b"
    nested = u.nest(text)
    assert u.cond_next(text, ",", nested, nested[0]) == 1

def test_cond_next3():
    # Protected:
    text = "{a,b}"
    nested = u.nest(text)
    assert u.cond_next(text, ",", nested, nested[0]) == 4
    text = "{a,b},c"
    nested = u.nest(text)
    assert u.cond_next(text, ",", nested, nested[0]) == 5
    text = "{a and b} and c"
    nested = u.nest(text)
    assert u.cond_next(text, " and ", nested, nested[0]) == 9


def test_find_closing_bracket1():
    text = '@ARTICLE{key, author={last_name}, title={The Title}}'
    end_pos = u.find_closing_bracket(text)
    assert end_pos == 51


def test_find_closing_bracket2():
    text = '@ARTICLE{key, author={last_name}, title={The Title}}'
    start_pos = 14
    end_pos = u.find_closing_bracket(text, start_pos=start_pos)
    assert end_pos == 31


def test_find_closing_bracket_tuple():
    text = '@ARTICLE{key, author={last_name}, title={The Title}}'
    pos = u.find_closing_bracket(text, get_open=True)
    assert pos[0] == 8
    assert pos[1] == 51


def test_find_closing_bracket_no_left_bracket():
    text = 'key, author=last_name}'
    end_pos = u.find_closing_bracket(text)
    assert end_pos is None


def test_find_closing_bracket_no_right_bracket():
    text = '@ARTICLE{key, author=last_name'
    end_pos = u.find_closing_bracket(text)
    assert end_pos is None


def test_parse_name1():
    # 'First Last' format:
    author = u.parse_name('Jones')
    assert author.last  == 'Jones'
    assert author.first == ''
    assert author.von   == ''
    assert author.jr    == ''
    author = u.parse_name('jones')
    assert author.last  == 'jones'
    assert author.first == ''
    assert author.von   == ''
    assert author.jr    == ''
    author = u.parse_name('Eric Jones')
    assert author.last  == 'Jones'
    assert author.first == 'Eric'
    assert author.von   == ''
    assert author.jr    == ''
    author = u.parse_name('Eric Steve Jones')
    assert author.last  == 'Jones'
    assert author.first == 'Eric Steve'
    assert author.von   == ''
    assert author.jr    == ''
    author = u.parse_name('{Jones Schmidt}')
    assert author.last  == '{Jones Schmidt}'
    assert author.first == ''
    assert author.von   == ''
    assert author.jr    == ''
    author = u.parse_name('Eric Steve {Jones Schmidt}')
    assert author.last  == '{Jones Schmidt}'
    assert author.first == 'Eric Steve'
    assert author.von   == ''
    assert author.jr    == ''

def test_parse_name2():
    # 'First von Last' format:
    author = u.parse_name("Jean de la Fontaine")
    assert author.last  == 'Fontaine'
    assert author.first == 'Jean'
    assert author.von   == 'de la'
    assert author.jr    == ''
    author = u.parse_name("Jean de la fontaine")
    assert author.last  == 'fontaine'
    assert author.first == 'Jean'
    assert author.von   == 'de la'
    assert author.jr    == ''
    author = u.parse_name("Jean de La Fontaine")
    assert author.last  == 'La Fontaine'
    assert author.first == 'Jean'
    assert author.von   == 'de'
    assert author.jr    == ''
    author = u.parse_name("Jean De la Fontaine")
    assert author.last  == 'Fontaine'
    assert author.first == 'Jean De'
    assert author.von   == 'la'
    assert author.jr    == ''
    author = u.parse_name("Jean De La Fontaine")
    assert author.last  == 'Fontaine'
    assert author.first == 'Jean De La'
    assert author.von   == ''
    assert author.jr    == ''
    author = u.parse_name("jean de la Fontaine")
    assert author.last  == 'Fontaine'
    assert author.first == ''
    assert author.von   == 'jean de la'
    assert author.jr    == ''
    author = u.parse_name("jean de la fontaine")
    assert author.last  == 'fontaine'
    assert author.first == ''
    assert author.von   == 'jean de la'
    assert author.jr    == ''
    author = u.parse_name("Jean {de} la fontaine")
    assert author.last  == 'fontaine'
    assert author.first == 'Jean {de}'
    assert author.von   == 'la'
    assert author.jr    == ''
    author = u.parse_name("jean {de} {la} fontaine")
    assert author.last  == '{de} {la} fontaine'
    assert author.first == ''
    assert author.von   == 'jean'
    assert author.jr    == ''
    author = u.parse_name("Jean {de} {la} fontaine")
    assert author.last  == 'fontaine'
    assert author.first == 'Jean {de} {la}'
    assert author.von   == ''
    assert author.jr    == ''

def test_parse_name3():
    # 'Last, First' format:
    author = u.parse_name('Jones,')
    assert author.last  == 'Jones'
    assert author.first == ''
    assert author.von   == ''
    assert author.jr    == ''
    author = u.parse_name('AAS Team,')
    assert author.last  == 'AAS Team'
    assert author.first == ''
    assert author.von   == ''
    assert author.jr    == ''
    # Blank field does not count:
    author = u.parse_name('AAS Team,   ')
    assert author.last  == 'AAS Team'
    assert author.first == ''
    assert author.von   == ''
    assert author.jr    == ''
    author = u.parse_name('{AAS Team},')
    assert author.last  == '{AAS Team}'
    assert author.first == ''
    assert author.von   == ''
    assert author.jr    == ''
    author = u.parse_name('Jones, Eric')
    assert author.last  == 'Jones'
    assert author.first == 'Eric'
    assert author.von   == ''
    assert author.jr    == ''

def test_parse_name4():
    # 'von Last, First' format:
    author = u.parse_name('jean de la fontaine,')
    assert author.last  == 'fontaine'
    assert author.first == ''
    assert author.von   == 'jean de la'
    assert author.jr    == ''
    author = u.parse_name('de la fontaine, Jean')
    assert author.last  == 'fontaine'
    assert author.first == 'Jean'
    assert author.von   == 'de la'
    assert author.jr    == ''
    author = u.parse_name('De La fontaine, Jean')
    assert author.last  == 'De La fontaine'
    assert author.first == 'Jean'
    assert author.von   == ''
    assert author.jr    == ''
    author = u.parse_name('De la Fontaine, Jean')
    assert author.last  == 'Fontaine'
    assert author.first == 'Jean'
    assert author.von   == 'De la'
    assert author.jr    == ''
    author = u.parse_name('de La Fontaine, Jean')
    assert author.last  == 'La Fontaine'
    assert author.first == 'Jean'
    assert author.von   == 'de'
    assert author.jr    == ''


def test_parse_name5():
    # von Last, Jr, First
    author = u.parse_name('de la Fontaine, sr., Jean')
    assert author.last  == 'Fontaine'
    assert author.first == 'Jean'
    assert author.von   == 'de la'
    assert author.jr    == 'sr.'
    author = u.parse_name('Fontaine, sr., Jean')
    assert author.last  == 'Fontaine'
    assert author.first == 'Jean'
    assert author.von   == ''
    assert author.jr    == 'sr.'
    author = u.parse_name('Fontaine, sr.,')
    assert author.last  == 'Fontaine'
    assert author.first == ''
    assert author.von   == ''
    assert author.jr    == 'sr.'
    author = u.parse_name('Fontaine,, Jean')
    assert author.last  == 'Fontaine'
    assert author.first == 'Jean'
    assert author.von   == ''
    assert author.jr    == ''


def test_repr_author1():
    assert u.repr_author(u.parse_name("Jones")) == "Jones"
    assert u.repr_author(u.parse_name("Jones,")) == "Jones"
    assert u.repr_author(u.parse_name("Eric Jones")) == "Jones, Eric"
    assert u.repr_author(u.parse_name("Eric B. Jones")) == 'Jones, Eric B.'

def test_repr_author2():
    # Strip outer blanks, collapse inner blanks (even protected):
    assert u.repr_author(u.parse_name("Johannes D. van der Waals")) \
           == 'van der Waals, Johannes D.'
    assert u.repr_author(u.parse_name("Johannes  D.  van  der   Waals")) \
           == 'van der Waals, Johannes D.'
    assert u.repr_author(u.parse_name("  Johannes D. van der Waals  ")) \
           == 'van der Waals, Johannes D.'
    assert u.repr_author(u.parse_name("  {Johannes D.} van der {Waals}  ")) \
           == 'van der {Waals}, {Johannes D.}'
    assert u.repr_author(u.parse_name("{Johannes  D.} van der Waals")) \
           == 'van der Waals, {Johannes D.}'

def test_repr_author3():
    assert u.repr_author(u.parse_name("van der Waals, Johannes D.")) \
           == 'van der Waals, Johannes D.'
    assert u.repr_author(u.parse_name("  van  der  Waals  ,  Johannes  D.  ")) \
           == 'van der Waals, Johannes D.'
    assert u.repr_author(
               u.parse_name("  van  der  {Waals}   ,  {Johannes  D.}")) \
           == 'van der {Waals}, {Johannes D.}'


def test_purify():
    assert u.purify("St{\\'{e}}fan")                == 'stefan'
    assert u.purify("{{\\v S}ime{\\v c}kov{\\'a}}")   == 'simeckova'
    assert u.purify("{{\\v{S}}ime{\\v{c}}kov{\\'a}}") == 'simeckova'
    assert u.purify('{AAS Journals Team}')          == 'aas journals team'
    assert u.purify("Jarom{\\'i}r")                 == 'jaromir'
    assert u.purify("Kov{\\'a}{\\v r}{\\'i}k")      == 'kovarik'
    assert u.purify("Kov{\\'a\\v r\\'i}k")          == 'kovarik'
    assert u.purify('{\\.I}volgin')                 == 'ivolgin'
    assert u.purify('Gon{\\c c}alez')               == 'goncalez'
    assert u.purify('Nu{\\~n}ez')                   == 'nunez'
    assert u.purify('Knausg{\\aa}rd')               == 'knausgaard'
    assert u.purify('Sm{\\o}rrebr{\\o}d')           == 'smorrebrod'
    assert u.purify('Schr{\\"o}dinger')             == 'schrodinger'
    assert u.purify('Be{\\ss}er')                   == 'besser'

    assert u.purify('Schr{\\"o}dinger', german=True) == 'schroedinger'


def test_initials():
    assert u.initials('')                  == ''
    assert u.initials('D.')                == 'd'
    assert u.initials('D. W.')             == 'dw'
    assert u.initials('{\\"O}. H.')        == 'oh'
    assert u.initials('J. Y.-K.')          == 'jyk'
    assert u.initials('Phil')              == 'p'
    assert u.initials('Phill Henry Scott') == 'phs'
    # An error by the user (missing blank in between):
    assert u.initials('G.O.')              == 'g'


author_lists = [
    [u.parse_name('{Hunter}, J. D.')],
    [u.parse_name('{AAS Journals Team}'),
     u.parse_name('{Hendrickson}, A.')],
    [u.parse_name('Eric Jones'),
     u.parse_name('Travis Oliphant'),
     u.parse_name('Pearu Peterson')]
   ]

@pytest.mark.parametrize('author_format', ('short','long'))
def test_get_authors_single(author_format):
    assert u.get_authors(author_lists[0], author_format) == '{Hunter}, J. D.'


@pytest.mark.parametrize('author_format', ('short','long'))
def test_get_authors_two(author_format):
    assert u.get_authors(author_lists[1], author_format) == \
           '{AAS Journals Team} and {Hendrickson}, A.'


def test_get_authors_short_three():
    assert u.get_authors(author_lists[2], 'short') == 'Jones, Eric; et al.'


def test_get_authors_long_three():
    assert u.get_authors(author_lists[2], 'long') == \
           'Jones, Eric; Oliphant, Travis; and Peterson, Pearu'


def test_get_authors_default_three():
    assert u.get_authors(author_lists[2]) == \
           'Jones, Eric; Oliphant, Travis; and Peterson, Pearu'


def test_get_authors_ushort_single():
    assert u.get_authors(author_lists[0], 'ushort') == 'Hunter'


def test_get_authors_ushort_two():
    assert u.get_authors(author_lists[1], 'ushort') == 'AAS Journals Team+'


def test_get_authors_ushort_spaces():
    authors = [u.parse_name('{Collier Cameron}, J. D.')]
    assert u.get_authors(authors, 'ushort') == 'Collier Cameron'


def test_get_authors_ushort_dash():
    authors = [u.parse_name(r'{Ben-Jaffel}, Lotfi')]
    assert u.get_authors(authors, 'ushort') == 'Ben-Jaffel'


def test_get_authors_ushort_non_ascii():
    authors = [u.parse_name(r'{Huang (黄新川)}, Xinchuan')]
    assert u.get_authors(authors, 'ushort') == 'Huang (黄新川)'


@pytest.mark.parametrize('author_format', ('short','long', 'ushort'))
def test_get_authors_none(author_format):
    assert u.get_authors(None, author_format) == ''


def test_next_char():
    assert u.next_char('Hello')    == 0
    assert u.next_char('  Hello')  == 2
    assert u.next_char('  Hello ') == 2
    assert u.next_char('')         == 0
    assert u.next_char('\n Hello') == 2
    assert u.next_char('  ')       == 0


def test_last_char():
    assert u.last_char('Hello')     == 5
    assert u.last_char('  Hello')   == 7
    assert u.last_char('  Hello  ') == 7
    assert u.last_char('')          == 0
    assert u.last_char('\n Hello')  == 7
    assert u.last_char('  ')        == 0


def test_get_fields():
    entry = '''
@Article{Hunter2007ieeeMatplotlib,
  Author    = {{Hunter}, J. D.},
  Title     = {Matplotlib: A 2D graphics environment},
  Journal   = "Computing In Science \\& Engineering",
  Volume    = {9},
  Number    = {3},
  Pages     = {90--95},
  publisher = {IEEE COMPUTER SOC},
  doi       = {10.1109/MCSE.2007.55},
  year      = 2007
}'''
    fields = u.get_fields(entry)
    assert next(fields) == 'Hunter2007ieeeMatplotlib'
    assert next(fields) == ('author',
                            '{Hunter}, J. D.',
                            [2,3,3,3,3,3,3,3,2,2,2,2,2,2,2])
    assert next(fields) == ('title',
                            'Matplotlib: A 2D graphics environment',
                            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
                             2,2,2,2,2,2,2,2,2,2,2,2,2])
    assert next(fields) == ('journal',
                            'Computing In Science \\& Engineering',
                            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
                             1,1,1,1,1,1,1,1,1,1,1])
    assert next(fields) == ('volume', '9', [2])
    assert next(fields) == ('number', '3', [2])
    assert next(fields) == ('pages', '90--95', [2, 2, 2, 2, 2, 2])
    assert next(fields) == ('publisher',
                            'IEEE COMPUTER SOC',
                            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2])
    assert next(fields) == ('doi',
                            '10.1109/MCSE.2007.55',
                            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2])
    assert next(fields) == ('year', '2007', [1,1,1,1])


@pytest.mark.parametrize('mock_input', [['5']], indirect=True)
def test_req_input1(mock_input, capsys):
    # Correct user input:
    r = u.req_input('Enter number between 0 and 9: ', options=np.arange(10))
    captured = capsys.readouterr()
    assert captured.out == 'Enter number between 0 and 9: \n'
    assert r == "5"

@pytest.mark.parametrize('mock_input', [['5','10']], indirect=True)
def test_req_input2(mock_input, capsys):
    # Invalid input, then correct input:
    r = u.req_input('Enter number between 0 and 9: ', options=np.arange(10))
    captured = capsys.readouterr()
    assert captured.out == 'Enter number between 0 and 9: \n' \
                         + 'Not a valid input.  Try again: \n'
    assert r == "5"


def test_tokenizer_default():
    attribute = 'Title'
    value = 'Synthesis of the Elements in Stars'
    tokens = u.tokenizer(attribute, value)
    assert len(tokens) == 4
    # These are always the same:
    assert tokens[0][0] == Token.Name.Attribute
    assert tokens[1][0] == Token.Punctuation
    assert tokens[3][0] == Token.Text
    # Set by the arguments:
    assert tokens[0][1] == attribute
    assert tokens[2][0] == Token.Literal.String
    assert tokens[2][1] == value


def test_tokenizer_value_token():
    attribute = 'Title'
    value = 'Synthesis of the Elements in Stars'
    value_token = Token.Name.Label
    tokens = u.tokenizer(attribute, value, value_token=value_token)
    assert len(tokens) == 4
    # These are always the same:
    assert tokens[0][0] == Token.Name.Attribute
    assert tokens[1][0] == Token.Punctuation
    assert tokens[3][0] == Token.Text
    # Set by the arguments:
    assert tokens[0][1] == attribute
    assert tokens[2][0] == value_token
    assert tokens[2][1] == value


def test_tokenizer_value_none():
    tokens = u.tokenizer('Title', None)
    assert tokens == []


def test_tokenizer_value_blank():
    tokens = u.tokenizer('Title', '')
    assert tokens == []


def test_parse_search_null(mock_init_sample):
    matches = u.parse_search('')
    assert matches == []


@pytest.mark.parametrize('search_text', (
    'year:1913',
    'year: 1913',
    'year:1912-1913',
    'year:-1913'))
def test_parse_search_year_fixed(mock_init_sample, search_text):
    matches = u.parse_search(search_text)
    assert len(matches) == 1
    assert matches[0].key == 'Slipher1913lobAndromedaRarialVelocity'


def test_parse_search_year_open(mock_init_sample):
    matches = u.parse_search('year:2020-')
    print(matches[1].key)
    assert len(matches) == 2
    assert matches[0].key == 'HarrisEtal2020natNumpy'
    assert matches[1].key == 'VirtanenEtal2020natmeScipy'


def test_parse_search_year_invalid(mock_init_sample):
    matches = u.parse_search('year:1913a')
    assert matches == []


@pytest.mark.parametrize('search_text', (
    'author:"Oliphant"',
    'author:"Oliphant, T."',
    'author:"oliphant"',
    'author:"oliphant, t"',))
def test_parse_search_author(mock_init_sample, search_text):
    matches = u.parse_search(search_text)
    assert len(matches) == 2
    assert matches[0].key == 'HarrisEtal2020natNumpy'
    assert matches[1].key == 'VirtanenEtal2020natmeScipy'


def test_parse_search_first_author(mock_init_sample):
    matches = u.parse_search('author:"^Virtanen"')
    assert len(matches) == 1
    assert matches[0].key == 'VirtanenEtal2020natmeScipy'


def test_parse_search_multiple_authors(mock_init_sample):
    matches = u.parse_search('author:"oliphant" author:"jones, e"')
    assert len(matches) == 1
    assert matches[0].key == 'VirtanenEtal2020natmeScipy'


def test_parse_search_author_year(mock_init_sample):
    matches = u.parse_search('author:"^virtanen" year:2020')
    assert len(matches) == 1
    assert matches[0].key == 'VirtanenEtal2020natmeScipy'


def test_parse_search_author_year_ignore_second_year(mock_init_sample):
    matches = u.parse_search('author:"^virtanen" year:2020 year:2001')
    assert len(matches) == 1
    assert matches[0].key == 'VirtanenEtal2020natmeScipy'


def test_parse_search_multiple_title_kws(mock_init_sample):
    matches = u.parse_search(
        'title:"HD 209458b" title:"atmospheric circulation"')


def test_parse_search_bibcode(mock_init_sample):
    matches = u.parse_search('bibcode:2013A&A...558A..33A')
    matches = u.parse_search('bibcode:2013A%26A...558A..33A')


def test_parse_search_multiple_bibcodes(mock_init_sample):
    matches = u.parse_search(
        'bibcode:1917PASP...29..206C bibcode:1918ApJ....48..154S')
    assert len(matches) == 2
    assert matches[0].key == 'Curtis1917paspIslandUniverseTheory'
    assert matches[1].key == 'Shapley1918apjDistanceGlobularClusters'


def test_parse_search_key(mock_init_sample):
    matches = u.parse_search('key: VirtanenEtal2020natmeScipy')
    assert len(matches) == 1
    assert matches[0].key == 'VirtanenEtal2020natmeScipy'


def test_parse_search_multiple_keys(mock_init_sample):
    matches = u.parse_search(
        'key:Curtis1917paspIslandUniverseTheory '
        'key:Shapley1918apjDistanceGlobularClusters')
    assert len(matches) == 2
    assert matches[0].key == 'Curtis1917paspIslandUniverseTheory'
    assert matches[1].key == 'Shapley1918apjDistanceGlobularClusters'

