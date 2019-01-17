import sys
import os
import filecmp
import datetime
import shutil
import pytest

import bibmanager.utils as u
import bibmanager.bib_manager as bm


def test_Bib_minimal():
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


def test_Bib_ads_entry():
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


def test_Bib_year_raise():
    # No year:
    entry = '''@Misc{JonesEtal2001scipy,
                author = {Eric Jones and Travis Oliphant and Pearu Peterson},
                title  = {{SciPy}: Open source scientific tools for {Python}},
            }'''
    with pytest.raises(ValueError, match="Bibtex entry 'JonesEtal2001scipy' is"
                                         " missing author, title, or year."):
        bib = bm.Bib(entry)


def test_Bib_title_raise():
    # No title:
    entry = '''@Misc{JonesEtal2001scipy,
                author = {Eric Jones and Travis Oliphant and Pearu Peterson},
                year   = 2001,
            }'''
    with pytest.raises(ValueError, match="Bibtex entry 'JonesEtal2001scipy' is"
                                         " missing author, title, or year."):
        bib = bm.Bib(entry)


def test_Bib_author_raise():
    # No author:
    entry = '''@Misc{JonesEtal2001scipy,
                title  = {{SciPy}: Open source scientific tools for {Python}},
                year   = 2001,
            }'''
    with pytest.raises(ValueError, match="Bibtex entry 'JonesEtal2001scipy' is"
                                         " missing author, title, or year."):
        bib = bm.Bib(entry)


def test_Bib_braces_raise():
    # Mismatched braces:
    entry = '''@Misc{JonesEtal2001scipy,
                title  = {SciPy}: Open source scientific tools for {Python}},
                author = {Eric Jones and Travis Oliphant and Pearu Peterson},
                year   = 2001,
            }'''
    with pytest.raises(ValueError, match="Mismatched braces in entry."):
        bib = bm.Bib(entry)


def test_Bib_contains():
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


def test_Bib_published_peer_reviewed():
    # Has adsurl field, no 'arXiv' in it:
    entry = '''@ARTICLE{DoeEtal2020,
          author = {{Doe}, J. and {Perez}, J. and {Dupont}, J.},
           title = "What Have the Astromomers ever Done for Us?",
          adsurl = {http://adsabs.harvard.edu/abs/2016Natur.123...45S},
            year = 2020,}'''
    bib = bm.Bib(entry)
    assert bib.published() == 1


def test_Bib_published_arxiv():
    # Has 'arXiv' adsurl:
    entry = '''@ARTICLE{DoeEtal2020,
          author = {{Doe}, J. and {Perez}, J. and {Dupont}, J.},
           title = "What Have the Astromomers ever Done for Us?",
          adsurl = {http://adsabs.harvard.edu/abs/2016arXiv0123.0045S},
            year = 2020,}'''
    bib = bm.Bib(entry)
    assert bib.published() == 0


def test_Bib_published_non_ads():
    # Does not have adsurl:
    entry = '''@ARTICLE{DoeEtal2020,
          author = {{Doe}, J. and {Perez}, J. and {Dupont}, J.},
           title = "What Have the Astromomers ever Done for Us?",
            year = 2020,}'''
    bib = bm.Bib(entry)
    assert bib.published() == -1


def test_display_bibs(capfd, mock_init):
    e1 = '''@Misc{JonesEtal2001scipy,
       author = {Eric Jones},
       title  = {SciPy},
       year   = {2001},
    }'''
    e2 = '''@Misc{Jones2001,
       author = {Travis Oliphant},
       title  = {tools for Python},
       year   = {2001},
    }'''
    bibs = [bm.Bib(e1), bm.Bib(e2)]
    bm.display_bibs(["DATABASE:\n", "NEW:\n"], bibs)
    captured = capfd.readouterr()
    #print(captured)
    assert captured.out == '\x1b[0m\x1b[?7h\x1b[0;38;5;248;3m\r\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\r\n\x1b[0mDATABASE:\r\n\x1b[0;38;5;34;1;4m@Misc\x1b[0m{\x1b[0;38;5;142mJonesEtal2001scipy\x1b[0m,\x1b[0m\r\n       \x1b[0;38;5;33mauthor\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130mEric Jones\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n       \x1b[0;38;5;33mtitle\x1b[0m  \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130mSciPy\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n       \x1b[0;38;5;33myear\x1b[0m   \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130m2001\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n    \x1b[0m}\x1b[0m\r\n\x1b[0m\r\n\x1b[0mNEW:\r\n\x1b[0;38;5;34;1;4m@Misc\x1b[0m{\x1b[0;38;5;142mJones2001\x1b[0m,\x1b[0m\r\n       \x1b[0;38;5;33mauthor\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130mTravis Oliphant\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n       \x1b[0;38;5;33mtitle\x1b[0m  \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130mtools for Python\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n       \x1b[0;38;5;33myear\x1b[0m   \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130m2001\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n    \x1b[0m}\x1b[0m\r\n\x1b[0m\r\n\x1b[0m\x1b[0m'


def test_remove_duplicates_no_duplicates(bibs):
    # No duplicates, no removal:
    my_bibs = [bibs['beaulieu_apj'], bibs['stodden']]
    bm.remove_duplicates(my_bibs, "doi")
    assert len(my_bibs) == 2


def test_remove_duplicates_identical(bibs):
    # Identical entries:
    my_bibs = [bibs["beaulieu_apj"], bibs["beaulieu_apj"]]
    bm.remove_duplicates(my_bibs, "doi")
    assert my_bibs == [bibs["beaulieu_apj"]]


def test_remove_duplicates_diff_published(bibs):
    # Duplicate, differente published status
    my_bibs = [bibs["beaulieu_apj"], bibs["beaulieu_arxiv"]]
    bm.remove_duplicates(my_bibs, "eprint")
    assert len(my_bibs) == 1
    assert my_bibs == [bibs["beaulieu_apj"]]


@pytest.mark.parametrize('mock_input', [['2']], indirect=True)
def test_remove_duplicates_querry(bibs, mock_input):
    # Querry-solve duplicate:
    my_bibs = [bibs["beaulieu_arxiv"], bibs["beaulieu_arxiv2"]]
    bm.remove_duplicates(my_bibs, "eprint")
    assert len(my_bibs) == 1
    # Note that the mocked input '2' applies on the sorted entries
    # (which, in fact, has swapped the values as seen above in my_bibs)
    assert my_bibs == [bibs["beaulieu_arxiv"]]



def test_filter_field():
    pass


def test_loadfile_bibfile(mock_init):
    bibs = bm.loadfile(u.ROOT+'examples/sample.bib')
    assert len(bibs) == 17


def test_loadfile_text(mock_init):
    with open(u.ROOT+'examples/sample.bib') as f:
       text = f.read()
    bibs = bm.loadfile(text=text)
    assert len(bibs) == 17


def test_save(bibs, mock_init):
    my_bibs = [bibs["beaulieu_apj"]]
    bm.save(my_bibs)
    assert "bm_database.pickle" in os.listdir(u.HOME)


def test_load(bibs, mock_init):
    my_bibs = [bibs["beaulieu_apj"], bibs["stodden"]]
    bm.save(my_bibs)
    loaded_bibs = bm.load()
    assert loaded_bibs == my_bibs


def test_export_home(bibs, mock_init):
    my_bibs = [bibs["stodden"], bibs["beaulieu_apj"]]
    bm.export(my_bibs, u.BM_BIBFILE)
    assert "bm_bibliography.bib" in os.listdir(u.HOME)
    with open(u.BM_BIBFILE, "r") as f:
        lines = f.readlines()
    assert lines[0] == "This file was created by bibmanager\n"
    loaded_bibs = bm.loadfile(u.BM_BIBFILE)
    assert loaded_bibs == sorted(my_bibs)


def test_export_no_overwrite(bibs, mock_init):
    with open(u.BM_BIBFILE, "w") as f:
        f.write("placeholder file.")
    my_bibs = [bibs["beaulieu_apj"], bibs["stodden"]]
    bm.export(my_bibs, u.BM_BIBFILE)
    assert "bm_bibliography.bib" in os.listdir(u.HOME)
    assert f"orig_{datetime.date.today()}_bm_bibliography.bib" \
           in os.listdir(u.HOME)


def test_init1(mock_home):
    # init from scratch:
    shutil.rmtree(u.HOME, ignore_errors=True)
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


def test_merge():
    pass
