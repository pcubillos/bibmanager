# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import shutil
import urllib
import pytest

import requests

import bibmanager
import bibmanager.bib_manager as bm
import bibmanager.utils as u


# Number of entries in bibmanager/examples/sample.bib:
nentries = 19


@pytest.fixture
def mock_input(monkeypatch, request):
    def mock_input(s):
        print(s)
        return request.param.pop()
    monkeypatch.setattr('builtins.input', mock_input)


@pytest.fixture
def mock_prompt(monkeypatch, request):
    def mock_prompt(s, multiline=None, lexer=None, style=None, completer=None,
                    complete_while_typing=None):
        print(s)
        return request.param.pop()
    monkeypatch.setattr('prompt_toolkit.prompt', mock_prompt)


@pytest.fixture
def mock_prompt_session(monkeypatch, request):
    class mocked_session():
        def __init__(self, *arg, **kwargs):
            pass
        def prompt(self, s, *arg, **kwargs):
            print(s)
            return request.param.pop()
    monkeypatch.setattr('prompt_toolkit.PromptSession', mocked_session)


@pytest.fixture
def mock_webbrowser(monkeypatch):
    def mock_webby(query, new):
        return
    monkeypatch.setattr('webbrowser.open', mock_webby)


@pytest.fixture
def mock_call(monkeypatch):
    def mock_call(some_list):
        return
    monkeypatch.setattr('subprocess.call', mock_call)


# FINDME: Does not test windows:
@pytest.fixture
def mock_open(monkeypatch):
    def mock_open(*arg, **kwargs):
        return
    monkeypatch.setattr('subprocess.run', mock_open)


@pytest.fixture
def mock_home(monkeypatch):
    # Re-define bibmanager HOME:
    mock_home = os.path.expanduser('~') + '/.mock_bibmanager/'
    # Monkey patch utils:
    monkeypatch.setattr(bibmanager.utils, 'HOME', mock_home)


@pytest.fixture
def mock_init(mock_home):
    shutil.rmtree(u.HOME, ignore_errors=True)
    bm.init(bibfile=None)


@pytest.fixture
def mock_init_sample(mock_home):
    shutil.rmtree(u.HOME, ignore_errors=True)
    bm.init(bibfile=u.ROOT+"examples/sample.bib")


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

    jones_no_title = '''@Misc{JonesNoTitleEtal2001scipy,
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

    hunter = r"""@Article{Hunter2007ieeeMatplotlib,
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

    isbn_doi1 = """
@INBOOK{2018haex.bookE.116P,
       author = {{Parmentier}, Vivien and {Crossfield}, Ian J.~M.},
        title = "{Exoplanet Phase Curves: Observations and Theory}",
         year = 2018,
          doi = {10.1007/978-3-319-55333-7\_116},
         isbn = "978-3-319-55333-7",
}"""

    isbn_doi2 = """
@INBOOK{2018haex.bookE.147C,
       author = {{Cowan}, Nicolas B. and {Fujii}, Yuka},
        title = "{Mapping Exoplanets}",
         year = 2018,
          doi = {10.1007/978-3-319-55333-7\_147},
         isbn = "978-3-319-55333-7",
}"""

    isbn_no_doi1 = """
@INBOOK{2018haex.bookE.116P,
       author = {{Parmentier}, Vivien and {Crossfield}, Ian J.~M.},
        title = "{Exoplanet Phase Curves: Observations and Theory}",
         year = 2018,
         isbn = "978-3-319-55333-7",
}"""

    isbn_no_doi2 = """
@INBOOK{2018haex.bookE.147C,
       author = {{Cowan}, Nicolas B. and {Fujii}, Yuka},
        title = "{Mapping Exoplanets}",
         year = 2018,
         isbn = "978-3-319-55333-7",
}"""

    data = {
        'jones_minimal': jones_minimal,
        'jones_no_year': jones_no_year,
        'jones_no_title': jones_no_title,
        'jones_no_author': jones_no_author,
        'jones_braces': jones_braces,
        'beaulieu_apj': beaulieu_apj,
        'beaulieu_arxiv': beaulieu_arxiv,
        'beaulieu_arxiv_dup': beaulieu_arxiv_dup,
        'hunter': hunter,
        'oliphant_dup': oliphant_dup,
        'no_oliphant': no_oliphant,
        'sing': sing,
        'stodden': stodden,
        'isbn_doi1': isbn_doi1,
        'isbn_doi2': isbn_doi2,
        'isbn_no_doi1': isbn_no_doi1,
        'isbn_no_doi2': isbn_no_doi2,
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


@pytest.fixture(scope="session")
def ads_entries():
    mayor = {'year': '1995',
              'bibcode': '1995Natur.378..355M',
              'author': ['Mayor, Michel', 'Queloz, Didier'],
              'pub': 'Nature',
              'title': ['A Jupiter-mass companion to a solar-type star']}

    fortney2018 = {'year': '2018',
                   'bibcode': '2018Natur.555..168F',
                   'author': ['Fortney, Jonathan'],
                   'pub': 'Nature',
                   'title': ['A deeper look at Jupiter']}

    fortney2016 = {'year': '2016',
                   'bibcode': '2016ApJ...824L..25F',
                   'author': ['Fortney, Jonathan J.', 'Marley, Mark S.',
                              'Laughlin, Gregory', 'Nettelmann, Nadine',
                              'Morley, Caroline V.', 'Lupu, Roxana E.',
                              'Visscher, Channon', 'Jeremic, Pavle',
                              'Khadder, Wade G.', 'Hargrave, Mason'],
                   'pub': 'The Astrophysical Journal',
                   'title': ['The Hunt for Planet Nine: Atmosphere, Spectra, Evolution, and Detectability']}

    fortney2013 = {'year': '2013',
                   'bibcode': '2013ApJ...775...80F',
                   'author': ['Fortney, Jonathan J.', 'Mordasini, Christoph',
                              'Nettelmann, Nadine', 'Kempton, Eliza M. -R.',
                              'Greene, Thomas P.', 'Zahnle, Kevin'],
                   'pub': 'The Astrophysical Journal',
                   'title': ['A Framework for Characterizing the Atmospheres of Low-mass Low-density Transiting Planets']}

    fortney2012 = {'year': '2012',
                   'bibcode': '2012ApJ...747L..27F',
                   'author': ['Fortney, Jonathan J.'],
                   'pub': 'The Astrophysical Journal',
                   'title': ['On the Carbon-to-oxygen Ratio Measurement in nearby Sun-like Stars: Implications for Planet Formation and the Determination of Stellar Abundances']}

    data = {
        'mayor': mayor,
        'fortney2018': fortney2018,
        'fortney2016': fortney2016,
        'fortney2013': fortney2013,
        'fortney2012': fortney2012,
        }
    return data


@pytest.fixture
def reqs(requests_mock):
    # get json's
    mayor = {'responseHeader': {'status': 0,
             'QTime': 3,
             'params': {'q': 'author:"^mayor" year:1995 property:refereed',
              'x-amzn-trace-id': 'Root=1-5c4a1d95-0cd91c606022f5b933a9a213',
              'fl': 'title,author,year,bibcode,pub',
              'start': '0',
              'sort': 'pubdate desc',
              'rows': '200',
              'wt': 'json'}},
        'response': {'numFound': 1,
              'start': 0,
              'docs': [{'year': '1995',
                'bibcode': '1995Natur.378..355M',
                'author': ['Mayor, Michel', 'Queloz, Didier'],
                'pub': 'Nature',
                'title': ['A Jupiter-mass companion to a solar-type star']}]}}

    fortney02 = {
      'responseHeader': {'status': 0,
        'QTime': 3,
        'params': {'q': 'author:"^fortney, j" year:2000-2018 property:refereed',
         'x-amzn-trace-id': 'Root=1-5c4a2215-54982261ad4601b6fb4bba51',
         'fl': 'title,author,year,bibcode,pub',
         'start': '0',
         'sort': 'pubdate desc',
         'rows': '200',
         'wt': 'json'}},
 'response': {'numFound': 26,
  'start': 0,
  'docs': [{'year': '2018',
    'bibcode': '2018Natur.555..168F',
    'author': ['Fortney, Jonathan'],
    'pub': 'Nature',
    'title': ['A deeper look at Jupiter']},
   {'year': '2016',
    'bibcode': '2016ApJ...824L..25F',
    'author': ['Fortney, Jonathan J.',
     'Marley, Mark S.',
     'Laughlin, Gregory',
     'Nettelmann, Nadine',
     'Morley, Caroline V.',
     'Lupu, Roxana E.',
     'Visscher, Channon',
     'Jeremic, Pavle',
     'Khadder, Wade G.',
     'Hargrave, Mason'],
    'pub': 'The Astrophysical Journal',
    'title': ['The Hunt for Planet Nine: Atmosphere, Spectra, Evolution, and Detectability']}]}}

    fortney22 = {'responseHeader': {'status': 0,
  'QTime': 5,
  'params': {'q': 'author:"^fortney, j" year:2000-2018 property:refereed',
   'x-amzn-trace-id': 'Root=1-5c4a254f-60d6a554efe020ac848fab48',
   'fl': 'title,author,year,bibcode,pub',
   'start': '2',
   'sort': 'pubdate desc',
   'rows': '2',
   'wt': 'json'}},
 'response': {'numFound': 26,
  'start': 2,
  'docs': [{'year': '2013',
    'bibcode': '2013ApJ...775...80F',
    'author': ['Fortney, Jonathan J.',
     'Mordasini, Christoph',
     'Nettelmann, Nadine',
     'Kempton, Eliza M. -R.',
     'Greene, Thomas P.',
     'Zahnle, Kevin'],
    'pub': 'The Astrophysical Journal',
    'title': ['A Framework for Characterizing the Atmospheres of Low-mass Low-density Transiting Planets']},
   {'year': '2012',
    'bibcode': '2012ApJ...747L..27F',
    'author': ['Fortney, Jonathan J.'],
    'pub': 'The Astrophysical Journal',
    'title': ['On the Carbon-to-oxygen Ratio Measurement in nearby Sun-like Stars: Implications for Planet Formation and the Determination of Stellar Abundances']}]}}

    fortney04 = {'responseHeader': {'status': 0,
  'QTime': 5,
  'params': {'q': 'author:"^fortney, j" year:2000-2018 property:refereed',
   'x-amzn-trace-id': 'Root=1-5caf8e80-c7f9332402b5b36c491f9222',
   'fl': 'title,author,year,bibcode,pub',
   'start': '0',
   'sort': 'pubdate desc',
   'rows': '4',
   'wt': 'json'}},
 'response': {'numFound': 26,
  'start': 0,
  'docs': [{'year': '2018',
    'bibcode': '2018Natur.555..168F',
    'author': ['Fortney, Jonathan'],
    'pub': 'Nature',
    'title': ['A deeper look at Jupiter']},
   {'year': '2016',
    'bibcode': '2016ApJ...824L..25F',
    'author': ['Fortney, Jonathan J.',
     'Marley, Mark S.',
     'Laughlin, Gregory',
     'Nettelmann, Nadine',
     'Morley, Caroline V.',
     'Lupu, Roxana E.',
     'Visscher, Channon',
     'Jeremic, Pavle',
     'Khadder, Wade G.',
     'Hargrave, Mason'],
    'pub': 'The Astrophysical Journal',
    'title': ['The Hunt for Planet Nine: Atmosphere, Spectra, Evolution, and Detectability']},
   {'year': '2013',
    'bibcode': '2013ApJ...775...80F',
    'author': ['Fortney, Jonathan J.',
     'Mordasini, Christoph',
     'Nettelmann, Nadine',
     'Kempton, Eliza M. -R.',
     'Greene, Thomas P.',
     'Zahnle, Kevin'],
    'pub': 'The Astrophysical Journal',
    'title': ['A Framework for Characterizing the Atmospheres of Low-mass Low-density Transiting Planets']},
   {'year': '2012',
    'bibcode': '2012ApJ...747L..27F',
    'author': ['Fortney, Jonathan J.'],
    'pub': 'The Astrophysical Journal',
    'title': ['On the Carbon-to-oxygen Ratio Measurement in nearby Sun-like Stars: Implications for Planet Formation and the Determination of Stellar Abundances']}]}}

    fortney44 = {'responseHeader': {'status': 0,
  'QTime': 157,
  'params': {'q': 'author:"^fortney, j" year:2000-2018 property:refereed',
   'x-amzn-trace-id': 'Root=1-5caf915e-f7f2037343699e5e3e50dde8',
   'fl': 'title,author,year,bibcode,pub',
   'start': '4',
   'sort': 'pubdate desc',
   'rows': '4',
   'wt': 'json'}},
 'response': {'numFound': 26,
  'start': 4,
  'docs': [{'year': '2011',
    'bibcode': '2011ApJS..197....9F',
    'author': ['Fortney, Jonathan J.',
     'Demory, Brice-Olivier', 'Désert, Jean-Michel',
     'Rowe, Jason',          'Marcy, Geoffrey W.',
     'Isaacson, Howard',     'Buchhave, Lars A.',
     'Ciardi, David',        'Gautier, Thomas N.',
     'Batalha, Natalie M.',  'Caldwell, Douglas A.',
     'Bryson, Stephen T.',   'Nutzman, Philip',
     'Jenkins, Jon M.',      'Howard, Andrew',
     'Charbonneau, David',   'Knutson, Heather A.',
     'Howell, Steve B.',     'Everett, Mark',
     'Fressin, François',    'Deming, Drake',
     'Borucki, William J.',  'Brown, Timothy M.',
     'Ford, Eric B.',        'Gilliland, Ronald L.',
     'Latham, David W.',     'Miller, Neil',
     'Seager, Sara',         'Fischer, Debra A.',
     'Koch, David',          'Lissauer, Jack J.',
     'Haas, Michael R.',     'Still, Martin',
     'Lucas, Philip',        'Gillon, Michael',
     'Christiansen, Jessie L.',
     'Geary, John C.'],
    'pub': 'The Astrophysical Journal Supplement Series',
    'title': ['Discovery and Atmospheric Characterization of Giant Planet Kepler-12b: An Inflated Radius Outlier']},
   {'year': '2011',
    'bibcode': '2011ApJ...729...32F',
    'author': ['Fortney, J. J.',
     'Ikoma, M.',
     'Nettelmann, N.',
     'Guillot, T.',
     'Marley, M. S.'],
    'pub': 'The Astrophysical Journal',
    'title': ["Self-consistent Model Atmospheres and the Cooling of the Solar System's Giant Planets"]},
   {'year': '2010',
    'bibcode': '2010SSRv..152..423F',
    'author': ['Fortney, Jonathan J.', 'Nettelmann, Nadine'],
    'pub': 'Space Science Reviews',
    'title': ['The Interior Structure, Composition, and Evolution of Giant Planets']},
   {'year': '2010',
    'bibcode': '2010PhyOJ...3...26F',
    'author': ['Fortney, Jonathan'],
    'pub': 'Physics Online Journal',
    'title': ['Peering into Jupiter']}]}}


    # post json's:
    payne = {'msg': 'Retrieved 1 abstracts, starting with number 1.',
 'export': '@PHDTHESIS{1925PhDT.........1P,\n       author = {{Payne}, Cecilia Helena},\n        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",\n     keywords = {Astronomy},\n       school = {RADCLIFFE COLLEGE.},\n         year = 1925,\n        month = Jan,\n       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},\n      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n}\n\n'}

    folsom = {'msg': 'Retrieved 1 abstracts, starting with number 1.',
 'export': '@ARTICLE{2018MNRAS.481.5286F,\n       author = {{Folsom}, C.~P. and {Fossati}, L. and {Wood}, B.~E. and {Sreejith},\n        A.~G. and {Cubillos}, P.~E. and {Vidotto}, A.~A. and {Alecian},\n        E. and {Girish}, V. and {Lichtenegger}, H. and {Murthy}, J. and\n        {Petit}, P. and {Valyavin}, G.},\n        title = "{Characterization of the HD 219134 multiplanet system I. Observations of stellar magnetism, wind, and high-energy flux}",\n      journal = {\\mnras},\n     keywords = {techniques: polarimetric, stars: individual: HD 219134, stars: late-type, stars: magnetic field, stars: winds, outflows, Astrophysics - Solar and Stellar Astrophysics, Astrophysics - Earth and Planetary Astrophysics},\n         year = 2018,\n        month = Dec,\n       volume = {481},\n        pages = {5286-5295},\n          doi = {10.1093/mnras/sty2494},\narchivePrefix = {arXiv},\n       eprint = {1808.00406},\n primaryClass = {astro-ph.SR},\n       adsurl = {https://ui.adsabs.harvard.edu/abs/2018MNRAS.481.5286F},\n      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n}\n\n'}


    # The mocks:
    start, cache_rows, sort = 0, 200, 'pubdate+desc'  #am.search.__defaults__
    query = 'author:"^mayor" year:1995 property:refereed'
    quote_query = urllib.parse.quote(query)
    URL = ('https://api.adsabs.harvard.edu/v1/search/query?'
          f'q={quote_query}&start={start}&rows={cache_rows}'
          f'&sort={sort}&fl=title,author,year,bibcode,pub')
    requests_mock.get(URL, json=mayor)

    start, cache_rows = 0, 2
    query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    quote_query = urllib.parse.quote(query)
    URL = ('https://api.adsabs.harvard.edu/v1/search/query?'
          f'q={quote_query}&start={start}&rows={cache_rows}'
          f'&sort={sort}&fl=title,author,year,bibcode,pub')
    requests_mock.get(URL, json=fortney02)

    start, cache_rows = 2, 2
    #query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    URL = ('https://api.adsabs.harvard.edu/v1/search/query?'
          f'q={quote_query}&start={start}&rows={cache_rows}'
          f'&sort={sort}&fl=title,author,year,bibcode,pub')
    requests_mock.get(URL, json=fortney22)

    start, cache_rows = 0, 4
    query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    quote_query = urllib.parse.quote(query)
    URL = ('https://api.adsabs.harvard.edu/v1/search/query?'
          f'q={quote_query}&start={start}&rows={cache_rows}'
          f'&sort={sort}&fl=title,author,year,bibcode,pub')
    requests_mock.get(URL, json=fortney04)

    start, cache_rows = 4, 4
    #query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    #quote_query = urllib.parse.quote(query)
    URL = ('https://api.adsabs.harvard.edu/v1/search/query?'
          f'q={quote_query}&start={start}&rows={cache_rows}'
          f'&sort={sort}&fl=title,author,year,bibcode,pub')
    requests_mock.get(URL, json=fortney44)

    start, cache_rows, sort = 0, 200, 'pubdate+desc'
    query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    quote_query = urllib.parse.quote(query)
    URL = ('https://api.adsabs.harvard.edu/v1/search/query?'
          f'q={quote_query}&start={start}&rows={cache_rows}'
          f'&sort={sort}&fl=title,author,year,bibcode,pub')
    requests_mock.get(URL, status_code=401, json={'error': 'Unauthorized'})


    def request_payne(request):
        return '1925PhDT.........1P' in request.text
    def request_invalid(request):
        return '1925PhDT.....X...1P' in request.text
    def request_invalid_folsom(request):
        return ('1925PhDT.....X...1P' in request.text and
                '2018MNRAS.481.5286F' in request.text)

    requests_mock.post("https://api.adsabs.harvard.edu/v1/export/bibtex",
        additional_matcher=request_payne,
        json=payne)

    requests_mock.post("https://api.adsabs.harvard.edu/v1/export/bibtex",
        additional_matcher=request_invalid,
        status_code=404,
        json={'error': 'no result from solr'})

    requests_mock.post("https://api.adsabs.harvard.edu/v1/export/bibtex",
        additional_matcher=request_invalid_folsom,
        json=folsom)

    requests_mock.register_uri('GET',
        'https://ui.adsabs.harvard.edu/link_gateway/success/PUB_PDF',
        headers={'Content-Type':'application/pdf'},
        status_code=200)

    requests_mock.register_uri('GET',
        'https://ui.adsabs.harvard.edu/link_gateway/exception/PUB_PDF',
        exc=requests.exceptions.ConnectionError)

    requests_mock.register_uri('GET',
        'https://ui.adsabs.harvard.edu/link_gateway/forbidden/PUB_PDF',
        headers={'Content-Type':'application/pdf'},
        reason='Forbidden',
        status_code=403)

    requests_mock.register_uri('GET',
        'https://ui.adsabs.harvard.edu/link_gateway/captcha/PUB_PDF',
        headers={'Content-Type':'text/html'},
        content=b'CAPTCHA',
        status_code=200)

    requests_mock.register_uri('GET',
        'https://ui.adsabs.harvard.edu/link_gateway/paywall/PUB_PDF',
        headers={'Content-Type':'text/html'},
        content=b'',
        status_code=200)

    gateway = 'https://ui.adsabs.harvard.edu/link_gateway'
    # Successful Journal request:
    requests_mock.register_uri('GET',
        f'{gateway}/1957RvMP...29..547B/PUB_PDF',
        headers={'Content-Type':'application/pdf'},
        content=b'PDF content',
        status_code=200)

    # Successful Journal request (bibcode not in database):
    requests_mock.register_uri('GET',
        f'{gateway}/1957RvMP...00..000B/PUB_PDF',
        headers={'Content-Type':'application/pdf'},
        content=b'PDF content',
        status_code=200)

    # No network Journal request:
    requests_mock.register_uri('GET',
        f'{gateway}/1918ApJ....48..154S/PUB_PDF',
        exc=requests.exceptions.ConnectionError)

    # Fail Journal, no network ADS request:
    requests_mock.register_uri('GET',
        f'{gateway}/2009ApJ...699..564S/PUB_PDF',
        reason='Forbidden', status_code=403)

    requests_mock.register_uri('GET',
        f'{gateway}/2009ApJ...699..564S/ADS_PDF',
        exc=requests.exceptions.ConnectionError)

    # Fail Journal, successful ADS request:
    requests_mock.register_uri('GET',
        f'{gateway}/1913LowOB...2...56S/PUB_PDF',
        reason='Forbidden', status_code=403)

    requests_mock.register_uri('GET',
        f'{gateway}/1913LowOB...2...56S/ADS_PDF',
        headers={'Content-Type':'application/pdf'},
        content=b'PDF content',
        status_code=200)

    # Fail Journal, fail ADS, successful ArXiv request:
    requests_mock.register_uri('GET',
        f'{gateway}/1917PASP...29..206C/PUB_PDF',
        reason='Forbidden', status_code=403)

    requests_mock.register_uri('GET',
        f'{gateway}/1917PASP...29..206C/ADS_PDF',
        reason='NOT FOUND', status_code=404)

    requests_mock.register_uri('GET',
        f'{gateway}/1917PASP...29..206C/EPRINT_PDF',
        headers={'Content-Type':'application/pdf'},
        content=b'PDF content',
        status_code=200)

    # All failed request:
    requests_mock.register_uri('GET',
        f'{gateway}/2010arXiv1007.0324B/PUB_PDF',
        reason='Forbidden', status_code=403)

    requests_mock.register_uri('GET',
        f'{gateway}/2010arXiv1007.0324B/ADS_PDF',
        reason='NOT FOUND', status_code=404)

    requests_mock.register_uri('GET',
        f'{gateway}/2010arXiv1007.0324B/EPRINT_PDF',
        reason='NOT FOUND', status_code=404)

