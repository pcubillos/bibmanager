import sys
import os
import filecmp
import pytest

import bibmanager.utils as u
import bibmanager.bib_manager as bm


def test_Bib1():
    # Minimal entry:
    entry = '''@Misc{JonesEtal2001scipy,
                author = {Eric Jones and Travis Oliphant and Pearu Peterson},
                title  = {{SciPy}: Open source scientific tools for {Python}},
                year   = {2001},
              }'''
    bib = bm.Bib(entry)
    assert bib.content == entry
    assert bib.key  == "JonesEtal2001scipy"
    assert bib.authors == [
        u.Author(last='Jones', first='Eric', von='', jr=''),
        u.Author(last='Oliphant', first='Travis', von='', jr=''),
        u.Author(last='Peterson', first='Pearu', von='', jr='')]
    assert bib.sort_author == u.Sort_author(last='jones', first='e',
                                  von='', jr='', year=2001, month=13)
    assert bib.year == 2001
    assert bib.title == "SciPy: Open source scientific tools for Python"
    assert bib.doi == None
    assert bib.bibcode == None
    assert bib.adsurl == None
    assert bib.eprint == None
    assert bib.isbn == None
    assert bib.month == 13

def test_Bib2():
    # Entry with more fields:
    entry = '''@ARTICLE{SingEtal2016natHotJupiterTransmission,
   author = {{Sing}, D.~K. and {Fortney}, J.~J. and {Nikolov}, N. and {Wakeford}, H.~R. and
        {Kataria}, T. and {Evans}, T.~M. and {Aigrain}, S. and {Ballester}, G.~E. and
        {Burrows}, A.~S. and {Deming}, D. and {D{\'e}sert}, J.-M. and
        {Gibson}, N.~P. and {Henry}, G.~W. and {Huitson}, C.~M. and
        {Knutson}, H.~A. and {Lecavelier Des Etangs}, A. and {Pont}, F. and
        {Showman}, A.~P. and {Vidal-Madjar}, A. and {Williamson}, M.~H. and
        {Wilson}, P.~A.},
    title = "{A continuum from clear to cloudy hot-Jupiter exoplanets without primordial water depletion}",
  journal = {\nat},
archivePrefix = "arXiv",
   eprint = {1512.04341},
 primaryClass = "astro-ph.EP",
     year = 2016,
    month = jan,
   volume = 529,
    pages = {59-62},
      doi = {10.1038/nature16068},
   adsurl = {http://adsabs.harvard.edu/abs/2016Natur.529...59S},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}'''
    bib = bm.Bib(entry)
    assert bib.content == entry
    assert bib.key  == "SingEtal2016natHotJupiterTransmission"
    assert bib.authors == [
        u.Author(last='{Sing}', first='D. K.', von='', jr=''),
        u.Author(last='{Fortney}', first='J. J.', von='', jr=''),
        u.Author(last='{Nikolov}', first='N.', von='', jr=''),
        u.Author(last='{Wakeford}', first='H. R.', von='', jr=''),
        u.Author(last='{Kataria}', first='T.', von='', jr=''),
        u.Author(last='{Evans}', first='T. M.', von='', jr=''),
        u.Author(last='{Aigrain}', first='S.', von='', jr=''),
        u.Author(last='{Ballester}', first='G. E.', von='', jr=''),
        u.Author(last='{Burrows}', first='A. S.', von='', jr=''),
        u.Author(last='{Deming}', first='D.', von='', jr=''),
        u.Author(last="{D{'e}sert}", first='J.-M.', von='', jr=''),
        u.Author(last='{Gibson}', first='N. P.', von='', jr=''),
        u.Author(last='{Henry}', first='G. W.', von='', jr=''),
        u.Author(last='{Huitson}', first='C. M.', von='', jr=''),
        u.Author(last='{Knutson}', first='H. A.', von='', jr=''),
        u.Author(last='{Lecavelier Des Etangs}', first='A.', von='', jr=''),
        u.Author(last='{Pont}', first='F.', von='', jr=''),
        u.Author(last='{Showman}', first='A. P.', von='', jr=''),
        u.Author(last='{Vidal-Madjar}', first='A.', von='', jr=''),
        u.Author(last='{Williamson}', first='M. H.', von='', jr=''),
        u.Author(last='{Wilson}', first='P. A.', von='', jr='')]
    assert bib.sort_author == u.Sort_author(last='sing', first='dk', von='',
                                  jr='', year=2016, month=1)
    assert bib.year == 2016
    assert bib.title == "A continuum from clear to cloudy hot-Jupiter exoplanets without primordial water depletion"
    assert bib.doi == "10.1038/nature16068"
    assert bib.bibcode == "2016Natur.529...59S"
    assert bib.adsurl == "http://adsabs.harvard.edu/abs/2016Natur.529...59S"
    assert bib.eprint == "1512.04341"
    assert bib.isbn == None
    assert bib.month == 1

def test_Bib3():
    # No year:
    entry = '''@Misc{JonesEtal2001scipy,
                author = {Eric Jones and Travis Oliphant and Pearu Peterson},
                title  = {{SciPy}: Open source scientific tools for {Python}},
            }'''
    with pytest.raises(ValueError, match="Bibtex entry 'JonesEtal2001scipy' is"
                                         " missing author, title, or year."):
        bib = bm.Bib(entry)

def test_Bib4():
    # No title:
    entry = '''@Misc{JonesEtal2001scipy,
                author = {Eric Jones and Travis Oliphant and Pearu Peterson},
                year   = 2001,
            }'''
    with pytest.raises(ValueError, match="Bibtex entry 'JonesEtal2001scipy' is"
                                         " missing author, title, or year."):
        bib = bm.Bib(entry)

def test_Bib5():
    # No author:
    entry = '''@Misc{JonesEtal2001scipy,
                title  = {{SciPy}: Open source scientific tools for {Python}},
                year   = 2001,
            }'''
    with pytest.raises(ValueError, match="Bibtex entry 'JonesEtal2001scipy' is"
                                         " missing author, title, or year."):
        bib = bm.Bib(entry)

def test_Bib6():
    # Mismatched braces:
    entry = '''@Misc{JonesEtal2001scipy,
                title  = {SciPy}: Open source scientific tools for {Python}},
                author = {Eric Jones and Travis Oliphant and Pearu Peterson},
                year   = 2001,
            }'''
    with pytest.raises(ValueError, match="Mismatched braces in entry."):
        bib = bm.Bib(entry)


def test_contains():
    bib = bm.Bib('''@ARTICLE{DoeEtal2020,
                    author = {{Doe}, J. and {Perez}, J. and {Dupont}, J.},
                     title = "What Have the Astromomers ever Done for Us?",
                      year = 2020,}''')
    assert 'Doe, J'   in bib
    assert 'John Doe' in bib
    assert 'Doe'      in bib
    assert 'Doe, K.'  not in bib
    assert 'Doe, J K' not in bib
    assert '^Doe'     in bib
    assert '^J Doe'   in bib
    assert '^Perez'   not in bib

def test_published_peer_reviewed():
    # Has adsurl field, no 'arXiv' in it:
    entry = '''@ARTICLE{DoeEtal2020,
          author = {{Doe}, J. and {Perez}, J. and {Dupont}, J.},
           title = "What Have the Astromomers ever Done for Us?",
          adsurl = {http://adsabs.harvard.edu/abs/2016Natur.123...45S},
            year = 2020,}'''
    bib = bm.Bib(entry)
    assert bib.published() == 1

def test_published_arxiv():
    # Has 'arXiv' adsurl:
    entry = '''@ARTICLE{DoeEtal2020,
          author = {{Doe}, J. and {Perez}, J. and {Dupont}, J.},
           title = "What Have the Astromomers ever Done for Us?",
          adsurl = {http://adsabs.harvard.edu/abs/2016arXiv0123.0045S},
            year = 2020,}'''
    bib = bm.Bib(entry)
    assert bib.published() == 0

def test_published_non_ads():
    # Does not have adsurl:
    entry = '''@ARTICLE{DoeEtal2020,
          author = {{Doe}, J. and {Perez}, J. and {Dupont}, J.},
           title = "What Have the Astromomers ever Done for Us?",
            year = 2020,}'''
    bib = bm.Bib(entry)
    assert bib.published() == -1


def test_loadfile(mock_home):
    bibs = bm.loadfile(u.ROOT+'examples/sample.bib')
    assert len(bibs) == 17


def test_remove_duplicates():
    pass


def test_filter_field():
    pass


def test_merge():
    pass


def test_save():
    pass


def test_load():
    pass


def test_export():
    pass


def test_init1(mock_home):
    # init from scratch:
    bm.init(bibfile=None)
    assert set(os.listdir(u.HOME)) == set(["config", "examples"])
    assert filecmp.cmp(u.HOME+"config", u.ROOT+"config")
    assert set(os.listdir(u.HOME+"examples")) \
        == set(['aastex62.cls', 'apj_hyperref.bst', 'sample.bib', 'sample.tex',
                'top-apj.tex'])

def test_add_entries():
    pass


def test_edit():
    pass


def test_search():
    pass
