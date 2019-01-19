import os
import shutil
import pytest

import prompt_toolkit

import bibmanager
import bibmanager.bib_manager as bm
import bibmanager.utils as u
 

@pytest.fixture
def mock_input(monkeypatch, request):
    def mock_input(s):
        print(s)
        return request.param.pop()
    monkeypatch.setattr('builtins.input', mock_input)


@pytest.fixture
def mock_prompt(monkeypatch, request):
    def mock_prompt(s, multiline, lexer, style):
        print(s)
        return request.param.pop()
    monkeypatch.setattr('prompt_toolkit.prompt', mock_prompt)


@pytest.fixture
def mock_home(monkeypatch):
    # Re-define bibmanager HOME:
    mock_home = os.path.expanduser("~") + "/.mock_bibmanager/"
    monkeypatch.setattr(bibmanager.utils, 'HOME', mock_home)
    monkeypatch.setattr(bibmanager.utils,
                        'BM_DATABASE', mock_home + "bm_database.pickle")
    monkeypatch.setattr(bibmanager.utils,
                        'BM_BIBFILE',  mock_home + "bm_bibliography.bib")
    monkeypatch.setattr(bibmanager.utils,
                        'BM_TMP_BIB',  mock_home + "tmp_bibliography.bib")
    monkeypatch.setattr(bibmanager.utils,
                        'BM_CACHE',    mock_home + "cached_ads_querry.pickle")


@pytest.fixture
def mock_init(mock_home):
    shutil.rmtree(u.HOME, ignore_errors=True)
    bm.init(bibfile=None)


@pytest.fixture(scope="session")
def entries():
    jones_minimal = '''@Misc{JonesEtal2001scipy,
  author = {Eric Jones and Travis Oliphant and Pearu Peterson},
  title  = {{SciPy}: Open source scientific tools for {Python}},
  year   = {2001},
}'''

    jones_no_year = '''@Misc{JonesEtal2001scipy,
  author = {Eric Jones and Travis Oliphant and Pearu Peterson},
  title  = {{SciPy}: Open source scientific tools for {Python}},
}'''

    jones_no_title = '''@Misc{JonesEtal2001scipy,
  author = {Eric Jones and Travis Oliphant and Pearu Peterson},
  year   = {2001},
}'''

    jones_no_author = '''@Misc{JonesEtal2001scipy,
  title  = {{SciPy}: Open source scientific tools for {Python}},
  year   = {2001},
}'''

    jones_braces = '''@Misc{JonesEtal2001scipy,
  title  = {SciPy}: Open source scientific tools for {Python}},
  author = {Eric Jones and Travis Oliphant and Pearu Peterson},
  year   = 2001,
}'''

    beaulieu_apj = """@ARTICLE{BeaulieuEtal2011apjGJ436bMethane,
   author = {{Beaulieu}, J.-P. and {Tinetti}, G. and {Kipping}, D.~M. and
        {Ribas}, I. and {Barber}, R.~J. and {Cho}, J.~Y.-K. and {Polichtchouk}, I. and
        {Tennyson}, J. and {Yurchenko}, S.~N. and {Griffith}, C.~A. and
        {Batista}, V. and {Waldmann}, I. and {Miller}, S. and {Carey}, S. and
        {Mousis}, O. and {Fossey}, S.~J. and {Aylward}, A.},
    title = "{Methane in the Atmosphere of the Transiting Hot Neptune GJ436B?}",
  journal = {\apj},
archivePrefix = "arXiv",
   eprint = {1007.0324},
 primaryClass = "astro-ph.EP",
 keywords = {planetary systems, techniques: spectroscopic},
     year = 2011,
    month = apr,
   volume = 731,
      eid = {16},
    pages = {16},
      doi = {10.1088/0004-637X/731/1/16},
   adsurl = {http://adsabs.harvard.edu/abs/2011ApJ...731...16B},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""

    beaulieu_arxiv = """@ARTICLE{BeaulieuEtal2010arxivGJ436b,
   author = {{Beaulieu}, J.-P. and {Tinetti}, G. and {Kipping}, D.~M. and
        {Ribas}, I. and {Barber}, R.~J. and {Cho}, J.~Y.-K. and {Polichtchouk}, I. and
        {Tennyson}, J. and {Yurchenko}, S.~N. and {Griffith}, C.~A. and
        {Batista}, V. and {Waldmann}, I. and {Miller}, S. and {Carey}, S. and
        {Mousis}, O. and {Fossey}, S.~J. and {Aylward}, A.},
    title = "Methane in the Atmosphere of the Transiting Hot {Neptune GJ436b}?",
  journal = {\apj},
   eprint = {1007.0324},
 primaryClass = "astro-ph.EP",
 keywords = {planetary systems, techniques: spectroscopic},
     year = 2010,
    month = apr,
   volume = 731,
    pages = {16},
      doi = {10.1088/0004-637X/731/1/16},
   adsurl = {http://adsabs.harvard.edu/abs/2010arXiv1007.0324B},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""

    beaulieu_arxiv_dup = """@ARTICLE{BeaulieuEtal2010,
   author = {{Beaulieu}, J.-P. and {Tinetti}, G. and {Kipping}, D.~M. and
        {Ribas}, I. and {Barber}, R.~J. and {Cho}, J.~Y.-K. and {Polichtchouk}, I. and
        {Tennyson}, J. and {Yurchenko}, S.~N. and {Griffith}, C.~A. and
        {Batista}, V. and {Waldmann}, I. and {Miller}, S. and {Carey}, S. and
        {Mousis}, O. and {Fossey}, S.~J. and {Aylward}, A.},
    title = "Methane in the Atmosphere of the Transiting Hot {Neptune GJ436b}?",
   eprint = {1007.0324},
     year = 2010,
   adsurl = {http://adsabs.harvard.edu/abs/2010arXiv1007.0324B},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""

    hunter = """@Article{Hunter2007ieeeMatplotlib,
  Author    = {{Hunter}, J. D.},
  Title     = {Matplotlib: A 2D graphics environment},
  Journal   = {Computing In Science \& Engineering},
  Volume    = {9},
  Number    = {3},
  Pages     = {90--95},
  abstract  = {Matplotlib is a 2D graphics package used for Python
  for application development, interactive scripting, and
  publication-quality image generation across user
  interfaces and operating systems.},
  publisher = {IEEE COMPUTER SOC},
  doi       = {10.1109/MCSE.2007.55},
  year      = 2007
}"""

    oliphant_dup = """@Misc{Oliphant2006numpy,
   author = {Travis Oliphant},
    title = {{Numpy}: A guide to {NumPy}, Part B},
     year = {2006},
}"""

    no_oliphant = """@Misc{NoOliphant2020,
   author = {Oliphant, No},
    title = {{Numpy}: A guide to {NumPy}},
     year = {2020},
}"""

    sing = '''@ARTICLE{SingEtal2016natHotJupiterTransmission,
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

    stodden = """@article{StoddenEtal2009ciseRRlegal,
  author = {Stodden, Victoria},
   title = "The legal framework for reproducible scientific research:
                  {Licensing} and copyright",
  journal= {Computing in Science \\& Engineering},
  volume = 11,
  number = 1,
  pages  = {35--40},
  year   = 2009,
  publisher={AIP Publishing}
}"""

    data = {
        'jones_minimal':      jones_minimal,
        'jones_no_year':      jones_no_year,
        'jones_no_title':     jones_no_title,
        'jones_no_author':    jones_no_author,
        'jones_braces':       jones_braces,
        'beaulieu_apj':       beaulieu_apj,
        'beaulieu_arxiv':     beaulieu_arxiv,
        'beaulieu_arxiv_dup': beaulieu_arxiv_dup,
        'hunter':             hunter,
        'oliphant_dup':       oliphant_dup,
        'no_oliphant':        no_oliphant,
        'sing':               sing,
        'stodden':            stodden,
           }
    return data

@pytest.fixture(scope="session")
def bibs(entries):
    beaulieu_apj       = bm.Bib(entries['beaulieu_apj'])
    beaulieu_arxiv     = bm.Bib(entries['beaulieu_arxiv'])
    beaulieu_arxiv_dup = bm.Bib(entries['beaulieu_arxiv_dup'])
    hunter             = bm.Bib(entries['hunter'])
    oliphant_dup       = bm.Bib(entries['oliphant_dup'])
    no_oliphant        = bm.Bib(entries['no_oliphant'])
    sing               = bm.Bib(entries['sing'])
    stodden            = bm.Bib(entries['stodden'])

    data = {
        'beaulieu_apj':       beaulieu_apj,
        'beaulieu_arxiv':     beaulieu_arxiv,
        'beaulieu_arxiv_dup': beaulieu_arxiv_dup,
        'hunter':             hunter,
        'oliphant_dup':       oliphant_dup,
        'no_oliphant':        no_oliphant,
        'sing':               sing,
        'stodden':            stodden,
        }
    return data

