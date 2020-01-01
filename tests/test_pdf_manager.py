# Copyright (c) 2018-2020 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

import pytest

import bibmanager.bib_manager as bm
import bibmanager.pdf_manager as pm


def test_guess_name_no_bibcode():
    bib = bm.Bib('''@ARTICLE{Raftery1995BIC,
       author = {{Raftery}, A.~E},
        title = "{Bayesian Model Selection in Social Research}",
         year = 1995,
    }''')
    assert pm.guess_name(bib) == 'Raftery1995.pdf'


def test_guess_name_with_bibcode():
    bib = bm.Bib('''@ARTICLE{FortneyEtal2008apjTwoClasses,
           author = {{Fortney}, J.~J. and {Lodders}, K. and {Marley}, M.~S. and
             {Freedman}, R.~S.},
            title = "{A Unified Theory for the Atmospheres of the Hot and Very Hot Jupiters: Two Classes of Irradiated Atmospheres}",
             year = "2008",
           adsurl = {https://ui.adsabs.harvard.edu/abs/2008ApJ...678.1419F},
    }''')
    assert pm.guess_name(bib) == 'Fortney2008_ApJ_678_1419.pdf'


def test_guess_name_arxiv_query():
    bib = bm.Bib('''@ARTICLE{FortneyEtal2008apjTwoClasses,
           author = {{Fortney}, J.~J. and {Lodders}, K. and {Marley}, M.~S. and
             {Freedman}, R.~S.},
            title = "{A Unified Theory for the Atmospheres of the Hot and Very Hot Jupiters: Two Classes of Irradiated Atmospheres}",
             year = "2008",
           adsurl = {https://ui.adsabs.harvard.edu/abs/2008ApJ...678.1419F},
    }''')
    assert pm.guess_name(bib, arxiv=True) == \
        'Fortney2008_arxiv_ApJ_678_1419.pdf'


def test_guess_name_arxiv_arxiv():
    bib = bm.Bib('''@ARTICLE{AndraeEtal2010arxivChiSquareStats,
           author = {{Andrae}, Rene and {Schulze-Hartung}, Tim and {Melchior}, Peter},
            title = "{Dos and don'ts of reduced chi-squared}",
             year = "2010",
           adsurl = {https://ui.adsabs.harvard.edu/abs/2010arXiv1012.3754A},
        }''')
    assert pm.guess_name(bib, arxiv=True) == \
        'Andrae2010_arXiv_1012_3754.pdf'


def test_guess_name_blanks():
    bib = bm.Bib('''@MISC{AASteamHendrickson2018aastex62,
           author = {{AAS Journals Team}, and {Hendrickson}, Amy},
            title = "{Aasjournals/Aastex60: Version 6.2 Official Release}",
             year = "2018",
           adsurl = {https://ui.adsabs.harvard.edu/abs/2018zndo...1209290T},
    }''')
    assert pm.guess_name(bib) == 'AASJournalsTeam2018_zndo_12_9290.pdf'


def test_guess_name_non_letter_characters():
    bib = bm.Bib(r'''@ARTICLE{GarciaMunoz2007pssHD209458bAeronomy,
           author = {{Garc{\'\i}a-Mu{\~n}oz}, A.},
            title = "{Physical and chemical aeronomy of HD 209458b}",
             year = "2007",
           adsurl = {https://ui.adsabs.harvard.edu/abs/2007P&SS...55.1426G},
    }''')
    assert pm.guess_name(bib) == 'GarciaMunoz2007_PSS_55_1426.pdf'


def test_guess_name_non_ascii():
    bib = bm.Bib('''@ARTICLE{HuangEtal2014jqsrtCO2,
      author = {{Huang (黄新川)}, Xinchuan and {Gamache}, Robert R.},
       title = "{Reliable infrared line lists for 13 CO$_{2}$}",
        year = "2014",
      adsurl = {https://ui.adsabs.harvard.edu/abs/2014JQSRT.147..134H},
    }''')
    assert pm.guess_name(bib) == 'Huang2014_JQSRT_147_134.pdf'


def test_guess_name_bibcode_no_volume():
    bib = bm.Bib('''@PHDTHESIS{Payne1925phdStellarAtmospheres,
           author = {{Payne}, Cecilia Helena},
            title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
             year = "1925",
           adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
    }''')
    assert pm.guess_name(bib) == 'Payne1925_PhDT_1.pdf'


def test_guess_name_bibcode_no_pages():
    bib = bm.Bib('''@BOOK{Chase1986jttJANAF,
           author = {{Chase}, M.~W.},
            title = "{JANAF thermochemical tables}",
             year = "1986",
           adsurl = {https://ui.adsabs.harvard.edu/abs/1986jtt..book.....C},
    }''')
    assert pm.guess_name(bib) == 'Chase1986_jtt_book.pdf'


@pytest.mark.skip(reason='Is this even testable?')
def test_open():
    pass


def test_open_no_pdf(mock_init_sample):
    with pytest.raises(ValueError,
            match='Entry does not have a PDF in the database.'):
        pm.open('AASteamHendrickson2018aastex62')


def test_open_no_bibtex(mock_init_sample):
    with pytest.raises(ValueError,
            match='Input key is not in the database.'):
        pm.open('AASteamHendrickson2018')


def test_request_ads_success(capsys, reqs):
    req = pm.request_ads('success', source='journal')
    captured = capsys.readouterr()
    assert captured.out == ''
    assert req.ok is True


def test_request_ads_no_connection(capsys, reqs):
    req = pm.request_ads('exception', source='journal')
    captured = capsys.readouterr()
    assert captured.out == 'Failed to establish a web connection.\n'


def test_request_ads_forbidden(capsys, reqs):
    req = pm.request_ads('forbidden', source='journal')
    captured = capsys.readouterr()
    assert captured.out == 'Request failed with status code 403: Forbidden\n'
    assert req.ok is False
    assert req.reason == 'Forbidden'


@pytest.mark.parametrize('mock_input', [['n']], indirect=True)
def test_request_ads_captcha(capsys, reqs, mock_input):
    req = pm.request_ads('captcha', source='journal')
    captured = capsys.readouterr()
    assert captured.out == ('There are issues with CAPTCHA verification, '
        'try to open PDF in browser?\n'
        '[]yes [n]o.\n\n')
    assert req.status_code == -102


@pytest.mark.parametrize('mock_input', [['']], indirect=True)
def test_request_ads_captcha_open(capsys, reqs, mock_input, mock_webbrowser):
    req = pm.request_ads('captcha', source='journal')
    captured = capsys.readouterr()
    assert captured.out == (
        "There are issues with CAPTCHA verification, "
        "try to open PDF in browser?\n"
        "[]yes [n]o.\n\n\n"
        "If you managed to download the PDF, add the PDF into the database\n"
        "with the following command (and right path):\n"
        "bibm pdf-set 'captcha' PATH/TO/FILE.pdf filename\n")
    assert req.status_code == -101


def test_request_ads_wrong_content(capsys, reqs):
    req = pm.request_ads('paywall', source='journal')
    captured = capsys.readouterr()
    assert captured.out == (
        'Request succeeded, but fetched content is not a PDF (might '
        'have been\nredirected to website due to paywall).\n')
    assert req.status_code == -100


def test_request_ads_invalid_source(capsys, reqs):
    with pytest.raises(ValueError, match=
            r"Source argument must be one of \['journal', 'arxiv', 'ads'\]"):
        req = pm.request_ads('success', source='invalid_source')

