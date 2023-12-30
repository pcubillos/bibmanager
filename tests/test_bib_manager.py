# Copyright (c) 2018-2024 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import datetime
import pickle
import shutil
import pathlib
import pytest

import bibmanager as bibm
import bibmanager.utils as u
import bibmanager.bib_manager as bm
from conftest import nentries


def test_Bib_minimal(entries):
    # Minimal entry (key, author, title, and year):
    bib = bm.Bib(entries['jones_minimal'])
    assert bib.content == entries['jones_minimal']
    assert bib.key  == "JonesEtal2001scipy"
    assert bib.authors == [
        u.Author(last='Jones', first='Eric', von='', jr=''),
        u.Author(last='Oliphant', first='Travis', von='', jr=''),
        u.Author(last='Peterson', first='Pearu', von='', jr='')]
    assert bib.sort_author == u.Sort_author(
        last='jones', first='e', von='', jr='', year=2001, month=13)
    assert bib.year == 2001
    assert bib.title == "SciPy: Open source scientific tools for Python"
    assert bib.doi == None
    assert bib.bibcode == None
    assert bib.adsurl == None
    assert bib.eprint == None
    assert bib.isbn == None
    assert bib.month == 13
    assert bib.pdf is None
    assert bib.freeze is None


def test_Bib_ads_entry(entries):
    # Entry with more fields:
    bib = bm.Bib(entries['sing'])
    assert bib.content == entries['sing']
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
    assert bib.sort_author == u.Sort_author(
        last='sing', first='dk', von='', jr='', year=2016, month=1)
    assert bib.year == 2016
    assert bib.title == "A continuum from clear to cloudy hot-Jupiter exoplanets without primordial water depletion"
    assert bib.doi == "10.1038/nature16068"
    assert bib.bibcode == "2016Natur.529...59S"
    assert bib.adsurl == "http://adsabs.harvard.edu/abs/2016Natur.529...59S"
    assert bib.eprint == "1512.04341"
    assert bib.isbn == None
    assert bib.month == 1


def test_Bib_update_content_bib_info(entries):
    bib1 = bm.Bib(entries['jones_minimal'])
    bib1.bibcode = 'bibcode1'
    bib2 = bm.Bib(entries['jones_minimal'])
    bib1.update_content(bib2)
    # bibcode gets updated to None since it's bibtex info:
    assert bib1.bibcode is None


def test_Bib_update_content_keep_meta(entries):
    bib1 = bm.Bib(entries['jones_minimal'])
    bib1.bibcode = 'bibcode1'
    bib1.pdf = 'pdf1'
    bib1.freeze = True
    bib1.tags = ['tag']
    bib2 = bm.Bib(entries['jones_minimal'])
    bib1.update_content(bib2)
    # pdf, freeze, and tags remeain as in bib1 since they are None in bib2:
    assert bib1.pdf == 'pdf1'
    assert bib1.freeze is True
    assert bib1.tags == ['tag']


def test_Bib_update_content_update_meta(entries):
    bib1 = bm.Bib(entries['jones_minimal'])
    bib1.bibcode = 'bibcode1'
    bib1.pdf = 'pdf1'
    bib1.tags = ['tag1']
    bib2 = bm.Bib(entries['jones_minimal'])
    bib2.pdf = 'pdf2'
    bib2.freeze = True
    bib1.tags = ['tag2']
    bib1.update_content(bib2)
    # pdf, freeze, and tags get updated since they are not None:
    assert bib1.pdf == 'pdf2'
    assert bib1.freeze is True
    assert bib1.tags == ['tag2']


def test_Bib_mismatched_braces_raise(entries):
    with pytest.raises(ValueError, match="Mismatched braces in entry."):
        bib = bm.Bib(entries['jones_braces'])


def test_Bib_update_key(entries):
    bib = bm.Bib(entries['jones_minimal'])
    assert bib.key  == "JonesEtal2001scipy"
    bib.update_key("JonesOliphantPeterson2001scipy")
    assert bib.key == "JonesOliphantPeterson2001scipy"
    assert bib.content == '''\
@Misc{JonesOliphantPeterson2001scipy,
  author = {Eric Jones and Travis Oliphant and Pearu Peterson},
  title  = {{SciPy}: Open source scientific tools for {Python}},
  year   = {2001},
}'''


def test_Bib_contains(bibs):
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


@pytest.mark.parametrize('month_in, month_out',
    [('', 13),
     ('month  = {},', 13),
     ('month  = {Jan},', 1),
     ('month  = {1},', 1),
    ])
def test_Bib_month(month_in, month_out):
    e = '''@Misc{JonesEtal2001scipy,
       author = {Eric Jones},
       title  = {SciPy},
       year   = {2001},
       ''' + month_in + '}'
    bib = bm.Bib(e)
    assert bib.month == month_out


def test_Bib_lower_than_no_author():
    b1 = bm.Bib('''@MISC{1978windEnergyReport,
        title = "{Wind energy systems: Program summary}",
         year = 1978,
    }''')
    b2 = bm.Bib('''@Misc{ZJones2001Scipy,
       author = {Eric ZJones},
       title  = {SciPy},
         year = 2001,
    }''')
    assert b1 > b2


def test_Bib_lower_than_both_no_author():
    b1 = bm.Bib('''@MISC{1978windEnergyReport,
        title = "{Wind energy systems: Program summary}",
         year = 1978,
    }''')
    b2 = bm.Bib('''@MISC{1979windEnergyReport,
        title = "{Wind energy systems: Program summary}",
         year = 1979,
    }''')
    assert b2 > b1


def test_Bib_lower_than_no_year():
    b1 = bm.Bib('''@Misc{JonesEtal2001scipy,
       author = {Eric Jones},
       title  = {SciPy},
       year   = {2001},
    }''')
    b2 = bm.Bib('''@Misc{JonesEtalScipy_noyear,
       author = {Eric Jones},
       title  = {SciPy},
    }''')
    assert b1 < b2


def test_Bib_equal_no_author():
    b1 = bm.Bib('''@MISC{1978windEnergyReport,
        title = "{Wind energy systems: Program summary}",
         year = 1978,
    }''')
    b2 = bm.Bib('''@Misc{ZJones2001Scipy,
       author = {Eric ZJones},
       title  = {SciPy},
         year = 2001,
    }''')
    assert b1 != b2


def test_Bib_equal_both_no_author():
    b1 = bm.Bib('''@MISC{1978windEnergyReport,
        title = "{Wind energy systems: Program summary}",
         year = 1978,
    }''')
    b2 = bm.Bib('''@MISC{1978NewWindEnergyReport,
        title = "{New wind energy systems: Program summary}",
         year = 1978,
    }''')
    assert b2 == b1


def test_Bib_not_equal_both_no_author():
    b1 = bm.Bib('''@MISC{1978windEnergyReport,
        title = "{Wind energy systems: Program summary}",
         year = 1978,
    }''')
    b2 = bm.Bib('''@MISC{1979NewWindEnergyReport,
        title = "{New wind energy systems: Program summary}",
         year = 1979,
    }''')
    assert b2 != b1


def test_Bib_not_equal_no_year():
    b1 = bm.Bib('''@Misc{JonesEtal2001scipy,
       author = {Eric Jones},
       title  = {SciPy},
       year   = {2001},
    }''')
    b2 = bm.Bib('''@Misc{JonesEtalScipy_noyear,
       author = {Eric Jones},
       title  = {SciPy},
    }''')
    assert b1 != b2


def test_Bib_equal_no_year():
    b1 = bm.Bib('''@Misc{JonesEtal2001scipy,
       author = {Eric Jones},
       title  = {SciPy},
    }''')
    b2 = bm.Bib('''@Misc{JonesEtalScipy_noyear,
       author = {Eric Jones},
       title  = {SciPy},
    }''')
    assert b1 == b2


def test_Bib_meta():
    e = '''@Misc{JonesEtal2001scipy,
       author = {Eric Jones},
       title  = {SciPy},
       year   = {2001},
    }'''
    bib = bm.Bib(e)
    assert bib.meta() == ''
    bib = bm.Bib(e, freeze=True, pdf='file.pdf')
    assert bib.meta() == 'freeze\npdf: file.pdf\n'


def test_Bib_warning_year():
    e = '''@Misc{JonesEtal2001scipy,
       author = {Eric Jones},
       title  = {SciPy},
       year   = {200X},
    }'''
    with pytest.warns(Warning) as record:
        bib = bm.Bib(e)
        assert str(record[0].message) == \
            "Bad year format value '200X' for entry 'JonesEtal2001scipy'"


@pytest.mark.parametrize('month', ['15', 'tuesday',])
def test_Bib_warning_month(month):
    e = '''@Misc{JonesEtal2001scipy,
       author = {Eric Jones},
       title  = {SciPy},
       year   = {2001},
       ''' + f'month = {month}' + ',}'
    with pytest.warns(Warning) as record:
        bib = bm.Bib(e)
        assert str(record[0].message) == \
            f"Invalid month value '{month}' for entry 'JonesEtal2001scipy'"


def test_Bib_warning_authors_comma_typo():
    e = '''@article{Joint2017ALMAGuide,
    title = {{ALMA Proposer's Guide}},
    year = {2017},
    author = {{Andreani}, P and {Trigo}, M, D, and {Remijan}, A},
    }'''
    with pytest.warns(Warning) as record:
        bib = bm.Bib(e)
        assert str(record[0].message) == (
            "Too many commas in name '{Trigo}, M, D,' "
            "for entry 'Joint2017ALMAGuide'")
        assert len(bib.authors) == 3
        # Corrected name:
        assert bib.authors[1].first == 'M D'


def test_Bib_warning_authors_missing_and():
    e = '''@article{Joint2017ALMAGuide,
    title = {{ALMA Proposer's Guide}},
    year = {2017},
    author = {{Andreani}, P and {Trigo}, M, {Remijan}, A},
    }'''
    with pytest.warns(Warning) as record:
        bib = bm.Bib(e)
        assert str(record[0].message) == (
            "Too many commas in name '{Trigo}, M, {Remijan}, A' "
            "for entry 'Joint2017ALMAGuide'")
        assert len(bib.authors) == 2
        # 'Corrected' name (seems to be how bibtex interprets the entry):
        assert bib.authors[1].first == 'M {Remijan} A'


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
    expected_capture = '\r\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\r\nDATABASE:\r\n@Misc{JonesEtal2001scipy,\r\n       author = {Eric Jones},\r\n       title  = {SciPy},\r\n       year   = {2001},\r\n    }\r\n\r\nNEW:\r\n@Misc{Jones2001,\r\n       author = {Travis Oliphant},\r\n       title  = {tools for Python},\r\n       year   = {2001},\r\n    }\r\n\r\n'
    assert captured.out == expected_capture


def test_display_bibs_meta_not_shown(capfd, mock_init):
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
    bibs = [bm.Bib(e1), bm.Bib(e2, freeze=True, pdf='file.pdf')]
    bm.display_bibs(["DATABASE:\n", "NEW:\n"], bibs, meta=False)
    captured = capfd.readouterr()
    expected_capture = '\r\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\r\nDATABASE:\r\n@Misc{JonesEtal2001scipy,\r\n       author = {Eric Jones},\r\n       title  = {SciPy},\r\n       year   = {2001},\r\n    }\r\n\r\nNEW:\r\n@Misc{Jones2001,\r\n       author = {Travis Oliphant},\r\n       title  = {tools for Python},\r\n       year   = {2001},\r\n    }\r\n\r\n'
    assert captured.out == expected_capture


def test_display_bibs_meta_shown(capfd, mock_init):
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
    bibs = [bm.Bib(e1), bm.Bib(e2, freeze=True, pdf='file.pdf')]
    bm.display_bibs(["DATABASE:\n", "NEW:\n"], bibs, meta=True)
    captured = capfd.readouterr()
    expected_capture = '\r\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\r\nDATABASE:\r\n@Misc{JonesEtal2001scipy,\r\n       author = {Eric Jones},\r\n       title  = {SciPy},\r\n       year   = {2001},\r\n    }\r\n\r\nNEW:\r\nfreeze\r\npdf: file.pdf\r\n@Misc{Jones2001,\r\n       author = {Travis Oliphant},\r\n       title  = {tools for Python},\r\n       year   = {2001},\r\n    }\r\n\r\n'
    assert captured.out == expected_capture


def test_display_list_no_verb(capfd, mock_init, mock_init_sample):
    bibs = bm.load()
    bm.display_list(bibs[0:4])
    captured = capfd.readouterr()
    assert captured.out == (
        '\nKeys:\n'
        'AASteamHendrickson2018aastex62\n'
        'Astropycollab2013aaAstropy\n'
        'BeaulieuEtal2010arxivGJ436b\n'
        'BurbidgeEtal1957rvmpStellarElementSynthesis\n')


def test_display_list_verb_neg(capfd, mock_init, mock_init_sample):
    bibs = bm.load()
    bm.display_list(bibs[0:4], verb=-1)
    captured = capfd.readouterr()
    assert captured.out == (
        '\nKeys:\n'
        'AASteamHendrickson2018aastex62\n'
        'Astropycollab2013aaAstropy\n'
        'BeaulieuEtal2010arxivGJ436b\n'
        'BurbidgeEtal1957rvmpStellarElementSynthesis\n')


def test_display_list_verb_zero(capfd, mock_init, mock_init_sample):
    bibs = bm.load()
    bibs = [bibs[11], bibs[13]]
    bm.display_list(bibs, verb=0)
    captured = capfd.readouterr()
    # Trick to see how the screen output looks:
    #print(repr(captured.out))
    #print(captured.out)
    expected_output = '\r\nTitle: Studies based on the colors and magnitudes in stellar clusters. VII.\r\n    The distances, distribution in space, and dimensions of 69 globular\r\n    clusters., 1918\r\nAuthors: {Shapley}, H.\r\nkey: Shapley1918apjDistanceGlobularClusters\r\n\r\nTitle: The radial velocity of the Andromeda Nebula, 1913\r\nAuthors: {Slipher}, V. M.\r\nkey: Slipher1913lobAndromedaRarialVelocity\r\n'
    assert captured.out == expected_output


def test_display_list_no_author(capfd, mock_init, mock_init_sample):
    bibs = bm.read_file(text='''@ARTICLE{Slipher1913lobAndromedaRarialVelocity,
        title = "{The radial velocity of the Andromeda Nebula}",
         year = 1913,
}''')
    bm.display_list(bibs, verb=0)
    captured = capfd.readouterr()
    expected_output = '\r\nTitle: The radial velocity of the Andromeda Nebula, 1913\r\nkey: Slipher1913lobAndromedaRarialVelocity\r\n'
    assert captured.out == expected_output


def test_display_list_no_year(capfd, mock_init, mock_init_sample):
    bibs = bm.read_file(text='''@ARTICLE{Slipher1913lobAndromedaRarialVelocity,
       author = {{Slipher}, V.~M.},
        title = "{The radial velocity of the Andromeda Nebula}",
}''')
    bm.display_list(bibs, verb=0)
    captured = capfd.readouterr()
    expected_output = '\r\nTitle: The radial velocity of the Andromeda Nebula\r\nAuthors: {Slipher}, V. M.\r\nkey: Slipher1913lobAndromedaRarialVelocity\r\n'
    assert captured.out == expected_output


def test_display_list_no_title(capfd, mock_init, mock_init_sample):
    bibs = bm.read_file(text='''@ARTICLE{Slipher1913lobAndromedaRarialVelocity,
       author = {{Slipher}, V.~M.},
         year = 1913,
}''')
    bm.display_list(bibs, verb=0)
    captured = capfd.readouterr()
    expected_output = '\r\nTitle: None, 1913\r\nAuthors: {Slipher}, V. M.\r\nkey: Slipher1913lobAndromedaRarialVelocity\r\n'
    assert captured.out == expected_output


def test_display_list_verb_one(capfd, mock_init, mock_init_sample):
    bibs = bm.load()
    bibs = [bibs[11], bibs[13]]
    bm.display_list(bibs, verb=1)
    captured = capfd.readouterr()
    expected_output = '\r\nTitle: Studies based on the colors and magnitudes in stellar clusters. VII.\r\n    The distances, distribution in space, and dimensions of 69 globular\r\n    clusters., 1918\r\nAuthors: {Shapley}, H.\r\nADS URL: http://adsabs.harvard.edu/abs/1918ApJ....48..154S\r\nbibcode: 1918ApJ....48..154S\r\nkey: Shapley1918apjDistanceGlobularClusters\r\n\r\nTitle: The radial velocity of the Andromeda Nebula, 1913\r\nAuthors: {Slipher}, V. M.\r\nADS URL: https://ui.adsabs.harvard.edu/abs/1913LowOB...2...56S\r\nbibcode: 1913LowOB...2...56S\r\nPDF file: Slipher1913.pdf\r\nkey: Slipher1913lobAndromedaRarialVelocity\r\n'
    assert captured.out == expected_output


def test_display_list_verb_two(capfd, mock_init, mock_init_sample):
    bibs = bm.load()
    bm.display_list(bibs[3:4], verb=2)
    captured = capfd.readouterr()
    expected_output = '\r\nTitle: Synthesis of the Elements in Stars, 1957\r\nAuthors: {Burbidge}, E. Margaret; {Burbidge}, G. R.; {Fowler}, William A.; and\r\n    {Hoyle}, F.\r\nADS URL: https://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B\r\nbibcode: 1957RvMP...29..547B\r\nkey: BurbidgeEtal1957rvmpStellarElementSynthesis\r\n'
    assert captured.out == expected_output


def test_display_list_no_arxiv(capfd, mock_init, mock_init_sample):
    bibs = bm.read_file(text='''@ARTICLE{Slipher1913lobAndromedaRarialVelocity,
       author = {{Slipher}, V.~M.},
        title = "{The radial velocity of the Andromeda Nebula}",
         year = 1913,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1913LowOB...2...56S},
}''')
    bm.display_list(bibs, verb=1)
    captured = capfd.readouterr()
    expected_output = '\r\nTitle: The radial velocity of the Andromeda Nebula, 1913\r\nAuthors: {Slipher}, V. M.\r\nADS URL: https://ui.adsabs.harvard.edu/abs/1913LowOB...2...56S\r\nbibcode: 1913LowOB...2...56S\r\nkey: Slipher1913lobAndromedaRarialVelocity\r\n'
    assert captured.out == expected_output


def test_display_list_no_ads(capfd, mock_init, mock_init_sample):
    bibs = bm.read_file(text='''@ARTICLE{Slipher1913lobAndromedaRarialVelocity,
       author = {{Slipher}, V.~M.},
        title = "{The radial velocity of the Andromeda Nebula}",
         year = 1913,
       eprint = {0000.2000},
}''')
    bm.display_list(bibs, verb=1)
    captured = capfd.readouterr()
    expected_output = '\r\nTitle: The radial velocity of the Andromeda Nebula, 1913\r\nAuthors: {Slipher}, V. M.\r\nArXiv URL: http://arxiv.org/abs/0000.2000\r\nkey: Slipher1913lobAndromedaRarialVelocity\r\n'
    assert captured.out == expected_output


def test_display_list_verb_full(capfd, mock_init, mock_init_sample):
    bibs = bm.load()
    bibs = [bibs[11], bibs[13]]
    bm.display_list(bibs, verb=3)
    captured = capfd.readouterr()
    print(repr(captured.out))
    expected_capture = '\r\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\r\n@ARTICLE{Shapley1918apjDistanceGlobularClusters,\r\n   author = {{Shapley}, H.},\r\n    title = "{Studies based on the colors and magnitudes in stellar clusters. VII. The distances, distribution in space, and dimensions of 69 globular clusters.}",\r\n  journal = {\\apj},\r\n     year = 1918,\r\n    month = oct,\r\n   volume = 48,\r\n      doi = {10.1086/142423},\r\n   adsurl = {http://adsabs.harvard.edu/abs/1918ApJ....48..154S},\r\n  adsnote = {Provided by the SAO/NASA Astrophysics Data System}\r\n}\r\n\r\npdf: Slipher1913.pdf\r\n@ARTICLE{Slipher1913lobAndromedaRarialVelocity,\r\n       author = {{Slipher}, V.~M.},\r\n        title = "{The radial velocity of the Andromeda Nebula}",\r\n      journal = {Lowell Observatory Bulletin},\r\n     keywords = {GALAXIES: MOTION IN LINE OF SIGHT, ANDROMEDA GALAXY},\r\n         year = 1913,\r\n        month = Jan,\r\n       volume = {1},\r\n        pages = {56-57},\r\n       adsurl = {https://ui.adsabs.harvard.edu/abs/1913LowOB...2...56S},\r\n      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\r\n}\r\n\r\n'
    assert captured.out == expected_capture


def test_remove_duplicates_no_duplicates(bibs):
    # No duplicates, no removal:
    my_bibs = [bibs['beaulieu_apj'], bibs['stodden']]
    dups = bm.remove_duplicates(my_bibs, "doi")
    assert len(my_bibs) == 2
    assert len(dups) == 0

def test_remove_duplicates_identical(bibs):
    # Identical entries:
    my_bibs = [bibs["beaulieu_apj"], bibs["beaulieu_apj"]]
    dups = bm.remove_duplicates(my_bibs, "doi")
    assert my_bibs == [bibs["beaulieu_apj"]]
    assert len(dups) == 0


def test_remove_duplicates_diff_published(bibs):
    # Duplicate, differente published status
    my_bibs = [bibs["beaulieu_apj"], bibs["beaulieu_arxiv"]]
    dups = bm.remove_duplicates(my_bibs, "eprint")
    assert len(my_bibs) == 1
    assert my_bibs == [bibs["beaulieu_apj"]]
    assert dups == {
        'BeaulieuEtal2010arxivGJ436b': 'BeaulieuEtal2011apjGJ436bMethane',
    }


@pytest.mark.parametrize('mock_input', [['2']], indirect=True)
def test_remove_duplicates_query(bibs, mock_input, mock_init):
    # Query-solve duplicate:
    my_bibs = [bibs["beaulieu_arxiv"], bibs["beaulieu_arxiv_dup"]]
    bm.remove_duplicates(my_bibs, "eprint")
    assert len(my_bibs) == 1
    # Note that the mocked input '2' applies on the sorted entries
    # (which, in fact, has swapped the values as seen above in my_bibs)
    assert my_bibs == [bibs["beaulieu_arxiv"]]


def test_filter_field_no_conflict(bibs, mock_init):
    # No modification to my_bibs nor new lists:
    my_bibs = [bibs["beaulieu_apj"]]
    new     = [bibs["stodden"]]
    bm.filter_field(my_bibs, new, "doi", "old")
    assert bibs["beaulieu_apj"] in my_bibs
    assert bibs["stodden"]      in new


def test_filter_field_take_published(bibs):
    # Take from new, regardless of 'take' argument:
    my_bibs = [bibs["beaulieu_arxiv"]]
    new     = [bibs["beaulieu_apj"]]
    bm.filter_field(my_bibs, new, "eprint", "old")
    assert bibs["beaulieu_apj"] in my_bibs
    assert len(my_bibs) == 1
    assert new == []


def test_filter_field_take_old(bibs):
    # Take from old:
    my_bibs = [bibs["beaulieu_arxiv"]]
    new     = [bibs["beaulieu_arxiv_dup"]]
    bm.filter_field(my_bibs, new, "eprint", "old")
    assert bibs["beaulieu_arxiv"] in my_bibs
    assert len(my_bibs) == 1
    assert new == []


def test_filter_field_take_new(bibs):
    # Take from new:
    my_bibs = [bibs["beaulieu_arxiv"]]
    new     = [bibs["beaulieu_arxiv_dup"]]
    bm.filter_field(my_bibs, new, "eprint", "new")
    assert bibs["beaulieu_arxiv_dup"] in my_bibs
    assert len(my_bibs) == 1
    assert new == []


@pytest.mark.parametrize('mock_input', [['']], indirect=True)
def test_filter_field_take_ask(bibs, mock_input, mock_init):
    # Ask, keep old:
    my_bibs = [bibs["beaulieu_arxiv"]]
    new     = [bibs["beaulieu_arxiv_dup"]]
    bm.filter_field(my_bibs, new, "eprint", "ask")
    assert bibs["beaulieu_arxiv"] in my_bibs
    assert len(my_bibs) == 1
    assert new == []


@pytest.mark.parametrize('mock_input', [['n']], indirect=True)
def test_filter_field_take_ask2(bibs, mock_input, mock_init):
    # Ask, keep new:
    my_bibs = [bibs["beaulieu_arxiv"]]
    new     = [bibs["beaulieu_arxiv_dup"]]
    bm.filter_field(my_bibs, new, "eprint", "ask")
    assert bibs["beaulieu_arxiv_dup"] in my_bibs
    assert len(my_bibs) == 1
    assert new == []


def test_read_file_bibfile(mock_init):
    bibs = bm.read_file(u.ROOT+'examples/sample.bib')
    assert len(bibs) == nentries


def test_read_file_text(mock_init):
    with open(u.ROOT+'examples/sample.bib') as f:
       text = f.read()
    bibs = bm.read_file(text=text)
    assert len(bibs) == nentries


def test_read_file_single_line_entry(mock_init):
    text = """@Article{Adams1991ApJ, author = {{Adams}, F.~C.}, title = "{Asymptotic theory for the spatial distribution of protostellar emission}", journal = {\apj}, keywords = {ASYMPTOTIC METHODS, EMISSION SPECTRA, PROTOSTARS, SPATIAL DISTRIBUTION, STAR FORMATION, COMPUTATIONAL ASTROPHYSICS, DENSITY DISTRIBUTION, PRE-MAIN SEQUENCE STARS, STELLAR ENVELOPES, STELLAR LUMINOSITY, TEMPERATURE DISTRIBUTION}, year = 1991, month = dec, volume = 382, pages = {544-554}, doi = {10.1086/170741}, adsurl = {http://adsabs.harvard.edu/abs/1991ApJ...382..544A}, adsnote = {Provided by the SAO/NASA Astrophysics Data System} }

@Misc{JonesOliphantPeterson2001scipy,
  author = {Eric Jones and Travis Oliphant and Pearu Peterson},
  title  = {{SciPy}: Open source scientific tools for {Python}},
  year   = {2001},
}"""
    bibs = bm.read_file(text=text)
    assert len(bibs) == 2
    assert bibs[0].key == 'Adams1991ApJ'


def test_read_file_ignore_comment(mock_init):
    text = """
@comment{Jones2000comment,
  author = {Eric Jones},
  title  = {{SciPy}: Open source scientific fools for {Python}},
  year   = {2000},
}

@Misc{JonesEtal2001scipy,
  author = {Eric Jones and Travis Oliphant and Pearu Peterson},
  title  = {{SciPy}: Open source scientific tools for {Python}},
  year   = {2001},
}
"""
    bibs = bm.read_file(text=text)
    assert len(bibs) == 1


def test_read_file_ignore_comment_no_commas(mock_init):
    text = """@Comment{jabref-meta: databaseType:biblatex;}"""
    bibs = bm.read_file(text=text)
    assert len(bibs) == 0


@pytest.mark.skip(reason='TBD')
def test_read_file_replacements(mock_init):
    bibs, reps = bm.read_file(
        u.ROOT+'examples/sample.bib',
        return_replacements=True,
    )
    assert len(bibs) == nentries
    assert reps == {}


def test_read_file_meta():
    with open(u.ROOT+'examples/sample.bib') as f:
       text = f.read()
    # prepend meta info before first entry:
    text = 'freeze\npdf: file.pdf\n'+ text
    bibs = bm.read_file(text=text)

    assert bibs[0].pdf == 'file.pdf'
    assert bibs[0].freeze is True
    assert bibs[1].pdf is None
    assert bibs[1].freeze is None


def test_read_file_pdf_with_path(tmp_path, mock_init):
    pdf_path = str(tmp_path) + '/pathed_file.pdf'
    pathlib.Path(pdf_path).touch()
    with open(u.ROOT+'examples/sample.bib') as f:
       text = f.read()
    text = f'pdf: {pdf_path}\n{text}'
    bibs = bm.read_file(text=text)
    assert bibs[0].pdf == 'pathed_file.pdf'
    assert 'pathed_file.pdf' in os.listdir(u.BM_PDF())
    assert not os.path.isfile(pdf_path)


def test_read_file_pdf_with_bad_path(tmp_path, mock_init):
    pdf_path = str(tmp_path) + '/pathed_file.pdf'
    # (no touch)
    with open(u.ROOT+'examples/sample.bib') as f:
       text = f.read()
    text = f'pdf: {pdf_path}\n{text}'
    bibs = bm.read_file(text=text)
    assert bibs[0].pdf is None


def test_read_file_error_bad_format(mock_init):
    text = '@this will fail}'
    with pytest.raises(
            ValueError,
            match="Mismatched braces at/after line 0:\n@this will fail}"):
        bibs = bm.read_file(text=text)


def test_read_file_error_open_end(mock_init):
    text = '@misc{key,\n author={name}'
    with pytest.raises(
            ValueError,
            match="Mismatched braces at/after line 0:\n@misc{key,"):
        bibs = bm.read_file(text=text)


def test_save(bibs, mock_init):
    my_bibs = [bibs["beaulieu_apj"]]
    bm.save(my_bibs)
    assert "bm_database.pickle" in os.listdir(u.HOME)


def test_load(bibs, mock_init):
    my_bibs = [bibs["beaulieu_apj"], bibs["stodden"]]
    bm.save(my_bibs)
    loaded_bibs = bm.load()
    assert loaded_bibs == my_bibs


def test_load_filed(tmp_path, bibs, mock_init):
    my_bibs = [bibs["beaulieu_apj"], bibs["stodden"]]
    bm.save(my_bibs)
    db = f'{tmp_path}/bm_database.pickle'
    shutil.copy(u.BM_DATABASE(), db)
    loaded_bibs = bm.load(db)
    assert loaded_bibs == my_bibs


def test_find_key(mock_init_sample):
    key = 'AASteamHendrickson2018aastex62'
    bib = bm.find(key=key)
    assert bib is not None
    assert bib.key == key


def test_find_bibcode(mock_init_sample):
    bibcode = '2013A&A...558A..33A'
    bib = bm.find(bibcode=bibcode)
    assert bib is not None
    assert bib.bibcode == bibcode


def test_find_key_bibcode(mock_init_sample):
    key = 'AASteamHendrickson2018aastex62'
    bibcode = '2013A&A...558A..33A'
    bib = bm.find(key=key, bibcode=bibcode)
    assert bib is not None
    assert bib.key == key
    assert bib.bibcode != bibcode


def test_find_key_not_found(mock_init_sample):
    bib = bm.find(key='non_existing_key')
    assert bib is None


def test_find_bibcode_not_found(mock_init_sample):
    bib = bm.find(bibcode='non_existing_bibcode')
    assert bib is None


def test_find_bibs(bibs):
    key = 'StoddenEtal2009ciseRRlegal'
    my_bibs = [bibs["beaulieu_apj"], bibs["stodden"]]
    bib = bm.find(key=key, bibs=my_bibs)
    assert bib is not None
    assert bib.key == key


def test_find_no_arguments(mock_init_sample):
    with pytest.raises(ValueError,
            match="Either key or bibcode arguments must be specified."):
        bib = bm.find()


def test_get_version_older(mock_init):
    # Mock pickle DB file without version:
    with open(u.BM_DATABASE(), 'wb') as handle:
        pickle.dump([], handle, protocol=4)
    assert bm.get_version() == '0.0.0'


def test_get_version_no_pickle(mock_init):
    # Make sure there's no database:
    with u.ignored(OSError):
        os.remove(u.BM_DATABASE())
    assert bm.get_version() == bibm.__version__


def test_get_version_existing(mock_init):
    expected_version = '1.0.0'
    # Mock pickle DB file with version:
    with open(u.BM_DATABASE(), 'wb') as handle:
        pickle.dump([], handle, protocol=4)
        pickle.dump(expected_version, handle, protocol=4)
    assert bm.get_version() == expected_version


def test_get_version_filed(tmp_path, mock_init):
    expected_version = '1.0.0'
    db = f'{tmp_path}/bm_database.pickle'
    with open(db, 'wb') as handle:
        pickle.dump([], handle, protocol=4)
        pickle.dump(expected_version, handle, protocol=4)
    assert bm.get_version(db) == expected_version


def test_export_home(bibs, mock_init):
    my_bibs = [bibs["stodden"], bibs["beaulieu_apj"]]
    bm.export(my_bibs, u.BM_BIBFILE())
    assert "bm_bibliography.bib" in os.listdir(u.HOME)
    with open(u.BM_BIBFILE(), "r") as f:
        lines = f.readlines()
    assert lines[0] == "This file was created by bibmanager\n"
    loaded_bibs = bm.read_file(u.BM_BIBFILE())
    assert loaded_bibs == sorted(my_bibs)


def test_export_no_overwrite(bibs, mock_init):
    with open(u.BM_BIBFILE(), "w") as f:
        f.write("placeholder file.")
    my_bibs = [bibs["beaulieu_apj"], bibs["stodden"]]
    bm.export(my_bibs, u.BM_BIBFILE())
    assert "bm_bibliography.bib" in os.listdir(u.HOME)
    assert f"orig_{datetime.date.today()}_bm_bibliography.bib" \
           in os.listdir(u.HOME)


def test_export_meta(mock_init_sample):
    bibs = bm.load()
    bm_export = u.HOME+'tmp_bm.bib'
    bm.export(bibs, bm_export, meta=True)
    with open(bm_export, "r") as f:
        lines = f.readlines()
    assert "pdf: Slipher1913.pdf\n" in lines


def test_export_no_meta(mock_init_sample):
    bibs = bm.load()
    bm_export = u.HOME+'tmp_bm.bib'
    bm.export(bibs, bm_export, meta=False)
    with open(bm_export, "r") as f:
        lines = f.readlines()
    assert "pdf: Slipher1913.pdf\n" not in lines


def test_merge_bibfile(capfd, mock_init):
    bm.merge(u.HOME + "examples/sample.bib")
    captured = capfd.readouterr()
    assert captured.out == f"\nMerged {nentries} new entries.\n"


def test_merge_bibs(capfd, mock_init):
    new = bm.read_file(u.HOME + "examples/sample.bib")
    bm.merge(new=new)
    captured = capfd.readouterr()
    assert captured.out == f"\nMerged {nentries} new entries.\n"


def test_merge_no_new(capfd, bibs, mock_init_sample):
    bm.merge(new=[bibs['hunter']])
    captured = capfd.readouterr()
    assert captured.out == ""


def test_merge_base(bibs):
    merged = bm.merge(new=[bibs['hunter']], base=[bibs['stodden']])
    assert len(merged) == 2
    assert merged[0] == bibs['hunter']
    assert merged[1] == bibs['stodden']


def test_merge_bibs_no_titles(capfd, mock_init):
    e1 = """@Misc{Jones2001scipy,
   author = {Eric Jones},
   year   = {2001},
 }"""
    e2 = """@Misc{Oliphant2001scipy,
   author = {Travis Oliphant},
   year   = {2001},
 }"""
    bibs = [bm.Bib(e1), bm.Bib(e2)]
    bm.merge(new=bibs)
    captured = capfd.readouterr()
    assert captured.out == "\nMerged 2 new entries.\n"


@pytest.mark.parametrize('mock_input', [['n']], indirect=True)
def test_merge_duplicate_key_ingnore(bibs, mock_init_sample, mock_input):
    bm.merge(new=[bibs['slipher_dup']])
    loaded_bibs = bm.load()
    assert len(loaded_bibs) == nentries
    assert bibs['slipher_dup'] in loaded_bibs


@pytest.mark.parametrize('mock_input', [['Slipher1913lobAnd']], indirect=True)
def test_merge_duplicate_key_rename(bibs, mock_init_sample, mock_input):
    bm.merge(new=[bibs['slipher_dup']])
    loaded_bibs = bm.load()
    assert len(loaded_bibs) == nentries + 1
    assert 'Slipher1913lobAnd' in [e.key for e in loaded_bibs]


@pytest.mark.parametrize('mock_input', [['']], indirect=True)
def test_merge_duplicate_title_ignore(bibs, mock_init_sample, mock_input):
    bm.merge(new=[bibs['slipher_guy']])
    loaded_bibs = bm.load()
    assert len(loaded_bibs) == nentries
    assert bibs['slipher_guy'] not in loaded_bibs


@pytest.mark.parametrize('mock_input', [['a']], indirect=True)
def test_merge_duplicate_title_add(bibs, mock_init_sample, mock_input):
    bm.merge(new=[bibs['slipher_guy']])
    loaded_bibs = bm.load()
    assert len(loaded_bibs) == nentries + 1
    assert bibs['slipher_guy'] in loaded_bibs


# bm.filter_field() is actually getting the job done here
@pytest.mark.parametrize('doi', ['', 'doi = {10.1007/978-3-319-21846-5}'])
def test_merge_duplicate_isbn_same_doi(doi):
    base_bibs = [bm.Bib(
    """@incollection{OConnor2017,
        title = "{The Core-Collapse Supernova-Black Hole Connection}",
        author = "O'Connor, Evan",
        year = "2016",
        booktitle = "Handbook of Supernovae",
        isbn = "9783319218465",
        DOI
    }""".replace('DOI', doi)
    )]
    new_bibs = [bm.Bib(
    """@incollection{Alsabti2016,
        title = {{Supernovae and Supernova Remnants: The Big Picture in Low Resolution}},
        author = {Alsabti, Athem W. and Murdin, Paul},
        year = {2017},
        booktitle = {Handbook of Supernovae},
        isbn = {9783319218465},
        DOI
    }""".replace('DOI', doi)
    )]
    merged = bm.merge(base=base_bibs, new=new_bibs)

    assert len(merged) == 1
    assert merged[0] == base_bibs[0]


# bm.filter_field() is actually getting the job done here
@pytest.mark.parametrize(
    'dois',
    [
        ('doi = "10.1007/978-3-319-20794-0"', 'doi = {10.1007/978-3-319-21846-5}'),
        ('doi = "10.1007/978-3-319-20794-0"', ''),
        ('', 'doi = {10.1007/978-3-319-21846-5}')
    ]
)
def test_merge_duplicate_isbn_different_doi(dois):
    base_bibs = [bm.Bib(
    """@incollection{OConnor2017,
        title = "{The Core-Collapse Supernova-Black Hole Connection}",
        author = "O'Connor, Evan",
        year = "2016",
        booktitle = "Handbook of Supernovae",
        isbn = "9783319218465",
        DOI
    }""".replace('DOI', dois[0])
    )]
    new_bibs = [bm.Bib(
    """@incollection{Alsabti2016,
        title = {{Supernovae and Supernova Remnants: The Big Picture in Low Resolution}},
        author = {Alsabti, Athem W. and Murdin, Paul},
        year = {2017},
        booktitle = {Handbook of Supernovae},
        isbn = {9783319218465},
        DOI
    }""".replace('DOI', dois[1])
    )]
    merged = bm.merge(base=base_bibs, new=new_bibs)

    assert len(merged) == 2
    assert merged[0] == new_bibs[0]
    assert merged[1] == base_bibs[0]


def test_duplicate_isbn_different_doi(capfd, entries):
    text = entries['isbn_doi1'] + entries['isbn_doi2']
    bibs = bm.read_file(text=text)
    assert len(bibs) == 2
    captured = capfd.readouterr()
    assert captured.out == ''


def test_duplicate_isbn_doi_vs_no_doi(capfd, entries):
    text = entries['isbn_doi1'] + entries['isbn_no_doi2']
    bibs = bm.read_file(text=text)
    assert len(bibs) == 2
    captured = capfd.readouterr()
    assert captured.out == ''


@pytest.mark.parametrize('mock_input', [['']], indirect=True)
def test_duplicate_isbn_same_unknown_doi(mock_init, mock_input, entries):
    text = entries['isbn_no_doi1'] + entries['isbn_no_doi2']
    bibs = bm.read_file(text=text)
    assert len(bibs) == 1


def test_init_from_scratch(mock_home):
    shutil.rmtree(u.HOME, ignore_errors=True)
    bm.init(bibfile=None)
    assert set(os.listdir(u.HOME)) == set(["config", "examples", "pdf"])

    with open(u.HOME+"config", 'r') as f:
        home = f.read()
    with open(u.ROOT+"config", 'r') as f:
        root = f.read()
    assert home == root.replace('HOME/', u.HOME)

    assert set(os.listdir(u.HOME+"examples")) \
        == set(['aastex62.cls', 'apj_hyperref.bst', 'sample.bib', 'sample.tex',
                'top-apj.tex'])


@pytest.mark.parametrize('mock_prompt', [['']], indirect=True)
def test_add_entries_dry(capfd, mock_init, mock_prompt):
    bm.add_entries('new')
    captured = capfd.readouterr()
    assert captured.out == (
        "Enter a BibTeX entry (press META+ENTER or ESCAPE ENTER when done):\n"
        "\nNo new entries to add.\n")


# TBD: Can I pass a fixure to the decorator?
@pytest.mark.parametrize('mock_prompt',
 [['''@Misc{JonesEtal2001scipy,
   author = {Eric Jones and Travis Oliphant and Pearu Peterson},
   title  = {{SciPy}: Open source scientific tools for {Python}},
   year   = {2001},
   }''']], indirect=True)
def test_add_entries(capfd, mock_init, mock_prompt, entries):
    bm.add_entries('new')
    captured = capfd.readouterr()
    assert captured.out == (
        "Enter a BibTeX entry (press META+ENTER or ESCAPE ENTER when done):\n"
        "\n\nMerged 1 new entries.\n")


@pytest.mark.skip(reason='No clue how to test this')
def test_edit():
    pass


def test_search_author_lastname(mock_init_sample):
    matches = bm.search(authors="oliphant")
    assert len(matches) == 2
    keys = [m.key for m in matches]
    assert 'HarrisEtal2020natNumpy' in keys
    assert 'VirtanenEtal2020natmeScipy' in keys


def test_search_author_last_initials(mock_init_sample):
    matches = bm.search(authors="oliphant, t")
    assert len(matches) == 2
    keys = [m.key for m in matches]
    assert 'HarrisEtal2020natNumpy' in keys
    assert 'VirtanenEtal2020natmeScipy' in keys


def test_search_author_first(mock_init_sample):
    matches = bm.search(authors="^virtanen, p")
    assert len(matches) == 1
    keys = [m.key for m in matches]
    assert 'VirtanenEtal2020natmeScipy' in keys


def test_search_author_multiple(mock_init_sample):
    # Multiple-author querries act with AND logic:
    matches = bm.search(authors=["oliphant, t", "jones, e"])
    assert len(matches) == 1
    keys = [m.key for m in matches]
    assert 'VirtanenEtal2020natmeScipy' in keys


def test_search_author_year_title(mock_init_sample):
    # Combined-fields querries act with AND logic:
    matches = bm.search(authors="oliphant, t", year=2020, title="numpy")
    assert len(matches) == 1
    keys = [m.key for m in matches]
    assert 'HarrisEtal2020natNumpy'  in keys


def test_search_title_multiple(mock_init_sample):
    # Multiple-title querries act with AND logic:
    matches = bm.search(title=['HD 209458b', 'atmospheric circulation'])
    assert len(matches) == 1
    keys = [m.key for m in matches]
    assert 'ShowmanEtal2009apjRadGCM' in keys


def test_search_title_entry_without_title(mock_init_sample, entries):
    # Multiple-title querries act with AND logic:
    bib = bm.Bib(entries['jones_no_title'])
    bm.merge(new=[bib])
    matches = bm.search(title=['HD 209458b', 'atmospheric circulation'])
    assert len(matches) == 1
    keys = [m.key for m in matches]
    assert 'ShowmanEtal2009apjRadGCM' in keys


def test_search_year_specific(mock_init_sample):
    matches = bm.search(authors="granger", year=2007)
    assert len(matches) == 1
    keys = [m.key for m in matches]
    assert 'PerezGranger2007cseIPython' in keys


def test_search_year_range(mock_init_sample):
    matches = bm.search(authors="granger, b", year=[2007,2018])
    assert len(matches) == 2
    keys = [m.key for m in matches]
    assert 'PerezGranger2007cseIPython' in keys
    assert 'MeurerEtal2017pjcsSYMPY' in keys


def test_search_bibcode(mock_init_sample):
    matches = bm.search(bibcode="2013A&A...558A..33A")
    assert len(matches) == 1
    keys = [m.key for m in matches]
    assert 'Astropycollab2013aaAstropy' in keys


def test_search_bibcode_utf8(mock_init_sample):
    # UTF8 decoding is done at run time, so this works as well:
    matches = bm.search(bibcode="2013A%26A...558A..33A")
    assert len(matches) == 1
    keys = [m.key for m in matches]
    assert 'Astropycollab2013aaAstropy' in keys


def test_search_bibcode_multiple(mock_init_sample):
    # Multiple-bibcode querries act with OR logic:
    matches = bm.search(bibcode=["2013A%26A...558A..33A","1957RvMP...29..547B"])
    assert len(matches) == 2
    keys = [m.key for m in matches]
    assert 'Astropycollab2013aaAstropy' in keys
    assert 'BurbidgeEtal1957rvmpStellarElementSynthesis' in keys


def test_search_key(mock_init_sample):
    matches = bm.search(key="BurbidgeEtal1957rvmpStellarElementSynthesis")
    assert len(matches) == 1
    keys = [m.key for m in matches]
    assert 'BurbidgeEtal1957rvmpStellarElementSynthesis' in keys


def test_search_key_multiple(mock_init_sample):
    # Multiple-key querries act with OR logic:
    matches = bm.search(key=["Astropycollab2013aaAstropy",
                             "BurbidgeEtal1957rvmpStellarElementSynthesis"])
    assert len(matches) == 2
    keys = [m.key for m in matches]
    assert 'Astropycollab2013aaAstropy' in keys
    assert 'BurbidgeEtal1957rvmpStellarElementSynthesis' in keys


@pytest.mark.skip(reason='TBD')
def test_search_single_tag():
    pass


@pytest.mark.skip(reason='TBD')
def test_search_multiple_tags():
    pass


@pytest.mark.parametrize('mock_prompt_session',
     [['key: BurbidgeEtal1957rvmpStellarElementSynthesis']], indirect=True)
def test_prompt_search_kw1(capsys, mock_init_sample, mock_prompt_session):
    keywords = ['key', 'bibcode']
    field = 'bibcode'
    prompt_text = ("Test search  (Press 'tab' for autocomplete):\n")
    prompt_input = bm.prompt_search(keywords, field, prompt_text)
    assert prompt_input[0] == \
        ['BurbidgeEtal1957rvmpStellarElementSynthesis', None]
    assert prompt_input[1] == [None]
    captured = capsys.readouterr()
    assert captured.out == prompt_text + '\n'


@pytest.mark.parametrize('mock_prompt_session',
     [['bibcode: 1957RvMP...29..547B']], indirect=True)
def test_prompt_search_kw2(mock_init_sample, mock_prompt_session):
    keywords = ['key', 'bibcode']
    field = 'bibcode'
    prompt_text = ("Test search  (Press 'tab' for autocomplete):\n")
    prompt_input = bm.prompt_search(keywords, field, prompt_text)
    assert prompt_input[0] == [None, '1957RvMP...29..547B']
    assert prompt_input[1] == [None]


@pytest.mark.parametrize('mock_prompt_session',
     [['bibcode: 1957RvMP...29..547B extra']], indirect=True)
def test_prompt_search_extra(mock_init_sample, mock_prompt_session):
    keywords = ['key', 'bibcode']
    field = 'bibcode'
    prompt_text = ("Test search  (Press 'tab' for autocomplete):\n")
    prompt_input = bm.prompt_search(keywords, field, prompt_text)
    assert prompt_input[0] == \
        [None, '1957RvMP...29..547B']
    assert prompt_input[1] == ['extra']


@pytest.mark.parametrize('mock_prompt_session',
    [['']], indirect=True)
def test_prompt_search_empty_prompt(mock_init_sample, mock_prompt_session):
    keywords = ['key', 'bibcode']
    field = 'bibcode'
    prompt_text = ("Test search  (Press 'tab' for autocomplete):\n")
    with pytest.raises(ValueError, match='Invalid syntax.'):
        prompt_input = bm.prompt_search(keywords, field, prompt_text)


@pytest.mark.parametrize('mock_prompt_session',
     [['bibcode:']], indirect=True)
def test_prompt_search_empty_value(mock_init_sample, mock_prompt_session):
    keywords = ['key', 'bibcode']
    field = 'bibcode'
    prompt_text = ("Test search  (Press 'tab' for autocomplete):\n")
    with pytest.raises(ValueError, match='Invalid syntax.'):
        prompt_input = bm.prompt_search(keywords, field, prompt_text)


@pytest.mark.parametrize('mock_prompt_session',
     [['bibcode: ']], indirect=True)
def test_prompt_search_blank_value(mock_init_sample, mock_prompt_session):
    keywords = ['key', 'bibcode']
    field = 'bibcode'
    prompt_text = ("Test search  (Press 'tab' for autocomplete):\n")
    with pytest.raises(ValueError, match='Invalid syntax.'):
        prompt_input = bm.prompt_search(keywords, field, prompt_text)


@pytest.mark.parametrize('mock_prompt_session',
     [['bibcode: VAL1  key: VAL2']], indirect=True)
def test_prompt_search_double_def(mock_init_sample, mock_prompt_session):
    keywords = ['key', 'bibcode']
    field = 'bibcode'
    prompt_text = ("Test search  (Press 'tab' for autocomplete):\n")
    with pytest.raises(ValueError, match='Invalid syntax.'):
        prompt_input = bm.prompt_search(keywords, field, prompt_text)


