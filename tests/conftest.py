import os
import shutil
import pytest

import bibmanager
import bibmanager.bib_manager as bm
import bibmanager.utils as u
 

@pytest.fixture(scope="session")
def bibs():
    beaulieu_apj = bm.Bib("""@ARTICLE{BeaulieuEtal2011apjGJ436bMethane,
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
}""")

    beaulieu_arxiv = bm.Bib("""@ARTICLE{BeaulieuEtal2010arxivGJ436b,
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
}""")

    beaulieu_arxiv_dup = bm.Bib("""@ARTICLE{BeaulieuEtal2010,
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
}""")

    stodden = bm.Bib("""@article{StoddenEtal2009ciseRRlegal,
  author = {Stodden, Victoria},
   title = "The legal framework for reproducible scientific research:
                  {Licensing} and copyright",
  journal= {Computing in Science \& Engineering},
  volume = 11,
  number = 1,
  pages  = {35--40},
  year   = 2009,
  publisher={AIP Publishing}
}""")

    data = {'beaulieu_apj':    beaulieu_apj,
            'beaulieu_arxiv':  beaulieu_arxiv,
            'beaulieu_arxiv_dup': beaulieu_arxiv_dup,
            'stodden': stodden,
           }
    return data


@pytest.fixture
def mock_input(monkeypatch, request):
    def mock_input(s):
        print(s)
        return request.param.pop()
    monkeypatch.setattr('builtins.input', mock_input)


#@pytest.fixture(scope="session")
#def some_resource(request):
#    print('\nIn some_resource()')
# 
#    def some_resource_fin():
#            print('\nIn some_resource_fin()')
#    request.addfinalizer(some_resource_fin)


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
