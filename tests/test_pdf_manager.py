# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import pytest
import pathlib

import bibmanager.bib_manager as bm
import bibmanager.pdf_manager as pm
import bibmanager.config_manager as cm
import bibmanager.utils as u


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


def test_guess_name_no_author_no_year():
    bib = bm.Bib('''@ARTICLE{Raftery1995BIC,
        title = "{Bayesian Model Selection in Social Research}",
    }''')
    with pytest.raises(ValueError,
            match='Could not guess a good filename since entry does not '
                  'have author nor year fields'):
        pm.guess_name(bib)


@pytest.mark.skip(reason='Is this even testable?')
def test_open():
    pass


def test_open_nones(mock_init_sample):
    with pytest.raises(ValueError,
            match='At least one of the arguments must be not None'):
        pm.open()


def test_open_no_pdf(mock_init_sample):
    with pytest.raises(ValueError,
            match='Entry does not have a PDF in the database'):
        pm.open(key='AASteamHendrickson2018aastex62')


def test_open_no_bibtex(mock_init_sample):
    with pytest.raises(ValueError,
            match='Requested entry does not exist in database'):
        pm.open(key='AASteamHendrickson2018')


def test_open_file_not_found(mock_init_sample):
    with pytest.raises(ValueError,
            match="Requested PDF file 'AASteam2018.pdf' does not exist "
                 f"in database PDF dir '{u.BM_PDF()[:-1]}'"):
        pm.open(pdf='AASteam2018.pdf')


@pytest.mark.parametrize('name', ['new.pdf', None])
def test_set_pdf_out_new(mock_init_sample, name):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    pdf = 'file.pdf'
    pathlib.Path(pdf).touch()
    out_filename = pm.set_pdf(bib, pdf=pdf, filename=name)
    filename = 'file.pdf' if name is None else name
    assert filename in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == filename
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{filename}"


@pytest.mark.parametrize('name', ['new.pdf', 'file.pdf', None])
def test_set_pdf_in_new(mock_init_sample, name):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    pdf = u.BM_PDF() + 'file.pdf'
    pathlib.Path(pdf).touch()
    out_filename = pm.set_pdf(bib, pdf=pdf, filename=name)
    filename = 'file.pdf' if name is None else name
    assert filename in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == filename
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{filename}"


@pytest.mark.parametrize('bib',
    ['ShowmanEtal2009apjRadGCM', '2009ApJ...699..564S'])
def test_set_pdf_str_bib(mock_init_sample, bib):
    pdf = 'file.pdf'
    name = 'new.pdf'
    pathlib.Path(pdf).touch()
    out_filename = pm.set_pdf(bib, pdf=pdf, filename=name)
    assert name in os.listdir(u.BM_PDF())
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    assert bib.pdf == name
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{name}"


def test_set_pdf_replace(mock_init_sample):
    bib = bm.find(key='Slipher1913lobAndromedaRarialVelocity')
    pdf = 'file.pdf'
    name = 'new.pdf'
    old = f"{u.BM_PDF()}{bib.pdf}"
    pathlib.Path(old).touch()
    pathlib.Path(pdf).touch()
    out_filename = pm.set_pdf(bib, pdf=pdf, filename=name, replace=True)
    filename = 'file.pdf' if name is None else name
    assert filename in os.listdir(u.BM_PDF())
    assert os.path.basename(old) not in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == filename
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{filename}"


@pytest.mark.parametrize('mock_input', [['y']], indirect=True)
def test_set_pdf_replace_ask_yes(mock_init_sample, mock_input):
    bib = bm.find(key='Slipher1913lobAndromedaRarialVelocity')
    pdf = 'file.pdf'
    name = 'new.pdf'
    old = f"{u.BM_PDF()}{bib.pdf}"
    pathlib.Path(old).touch()
    pathlib.Path(pdf).touch()
    out_filename = pm.set_pdf(bib, pdf=pdf, filename=name)
    filename = 'file.pdf' if name is None else name
    assert filename in os.listdir(u.BM_PDF())
    assert os.path.basename(old) not in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == filename
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{filename}"


@pytest.mark.parametrize('mock_input', [['n']], indirect=True)
def test_set_pdf_replace_ask_no(mock_init_sample, mock_input):
    bib = bm.find(key='Slipher1913lobAndromedaRarialVelocity')
    old = f"{u.BM_PDF()}{bib.pdf}"
    pdf = 'file.pdf'
    name = 'new.pdf'
    pathlib.Path(old).touch()
    out_filename = pm.set_pdf(bib, pdf=pdf, filename=name)
    assert name not in os.listdir(u.BM_PDF())
    assert os.path.basename(old) in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == os.path.basename(old)
    assert out_filename is not None
    assert out_filename == old


@pytest.mark.parametrize('replace', [True, False])
def test_set_pdf_rename(mock_init_sample, replace):
    bib = bm.find(key='Slipher1913lobAndromedaRarialVelocity')
    old = f"{u.BM_PDF()}{bib.pdf}"
    pdf = old
    name = 'new.pdf'
    pathlib.Path(old).touch()
    out_filename = pm.set_pdf(bib, pdf=pdf, filename=name, replace=replace)
    assert name in os.listdir(u.BM_PDF())
    assert old not in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == name
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{name}"


@pytest.mark.parametrize('mock_input', [['y']], indirect=True)
def test_set_pdf_overwrite_yes(mock_init_sample, mock_input):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    pdf = 'file.pdf'
    name = 'new.pdf'
    pathlib.Path(pdf).touch()
    pathlib.Path(f"{u.BM_PDF()}{name}").touch()
    out_filename = pm.set_pdf(bib, pdf=pdf, filename=name)
    assert name in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == name
    # TBD: Check if previous file belongs to another entry?
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{name}"


@pytest.mark.parametrize('mock_input', [['n']], indirect=True)
def test_set_pdf_overwrite_no(mock_init_sample, mock_input):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    pdf = 'file.pdf'
    name = 'new.pdf'
    pathlib.Path(pdf).touch()
    pathlib.Path(f"{u.BM_PDF()}{name}").touch()
    out_filename = pm.set_pdf(bib, pdf=pdf, filename=name)
    assert name in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf is None
    assert out_filename is None


@pytest.mark.parametrize('mock_input', [['new_new.pdf']], indirect=True)
def test_set_pdf_overwrite_rename(mock_init_sample, mock_input):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    pdf = 'file.pdf'
    name = 'new.pdf'
    pathlib.Path(pdf).touch()
    pathlib.Path(f"{u.BM_PDF()}{name}").touch()
    out_filename = pm.set_pdf(bib, pdf=pdf, filename=name)
    assert 'new_new.pdf' in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == 'new_new.pdf'
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}new_new.pdf"


@pytest.mark.parametrize('name', ['new.pdf', None])
def test_set_pdf_bin_new(mock_init_sample, name):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    bin_pdf = b'file.pdf'
    out_filename = pm.set_pdf(bib, bin_pdf=bin_pdf, filename=name)
    filename = 'Showman2009_ApJ_699_564.pdf' if name is None else name
    assert filename in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == filename
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{filename}"


def test_set_pdf_bin_replace(mock_init_sample):
    bib = bm.find(key='Slipher1913lobAndromedaRarialVelocity')
    bin_pdf = b'file.pdf'
    pdf = 'file.pdf'
    name = 'new.pdf'
    old = f"{u.BM_PDF()}{bib.pdf}"
    pathlib.Path(old).touch()
    out_filename = pm.set_pdf(bib, bin_pdf=bin_pdf, filename=name, replace=True)
    filename = 'file.pdf' if name is None else name
    assert filename in os.listdir(u.BM_PDF())
    assert os.path.basename(old) not in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == filename
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{filename}"


@pytest.mark.parametrize('mock_input', [['y']], indirect=True)
def test_set_pdf_bin_replace_ask_yes(mock_init_sample, mock_input):
    bib = bm.find(key='Slipher1913lobAndromedaRarialVelocity')
    bin_pdf = b'file.pdf'
    name = 'new.pdf'
    old = f"{u.BM_PDF()}{bib.pdf}"
    pathlib.Path(old).touch()
    out_filename = pm.set_pdf(bib, bin_pdf=bin_pdf, filename=name)
    filename = 'file.pdf' if name is None else name
    assert filename in os.listdir(u.BM_PDF())
    assert os.path.basename(old) not in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == filename
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{filename}"


@pytest.mark.parametrize('mock_input', [['n']], indirect=True)
def test_set_pdf_bin_replace_ask_no(mock_init_sample, mock_input):
    bib = bm.find(key='Slipher1913lobAndromedaRarialVelocity')
    bin_pdf = b'file.pdf'
    old = f"{u.BM_PDF()}{bib.pdf}"
    name = 'new.pdf'
    pathlib.Path(old).touch()
    out_filename = pm.set_pdf(bib, bin_pdf=bin_pdf, filename=name)
    assert name not in os.listdir(u.BM_PDF())
    assert os.path.basename(old) in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == os.path.basename(old)
    assert out_filename is not None
    assert out_filename == old


@pytest.mark.parametrize('mock_input', [['y']], indirect=True)
def test_set_pdf_bin_overwrite_yes(mock_init_sample, mock_input):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    bin_pdf = b'file.pdf'
    name = 'new.pdf'
    pathlib.Path(f"{u.BM_PDF()}{name}").touch()
    out_filename = pm.set_pdf(bib, bin_pdf=bin_pdf, filename=name)
    assert name in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == name
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}{name}"


@pytest.mark.parametrize('mock_input', [['n']], indirect=True)
def test_set_pdf_bin_overwrite_no(mock_init_sample, mock_input):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    bin_pdf = b'file.pdf'
    name = 'new.pdf'
    pathlib.Path(f"{u.BM_PDF()}{name}").touch()
    out_filename = pm.set_pdf(bib, bin_pdf=bin_pdf, filename=name)
    assert name in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf is None
    assert out_filename is None


@pytest.mark.parametrize('mock_input', [['new_new.pdf']], indirect=True)
def test_set_pdf_bin_overwrite_rename(mock_init_sample, mock_input):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    bin_pdf = b'file.pdf'
    name = 'new.pdf'
    pathlib.Path(f"{u.BM_PDF()}{name}").touch()
    out_filename = pm.set_pdf(bib, bin_pdf=bin_pdf, filename=name)
    assert 'new_new.pdf' in os.listdir(u.BM_PDF())
    bib = bm.find(key=bib.key)
    assert bib.pdf == 'new_new.pdf'
    assert out_filename is not None
    assert out_filename == f"{u.BM_PDF()}new_new.pdf"


def test_set_pdf_bad_bib(mock_init_sample):
    key = 'not_in_database'
    pdf = 'file.pdf'
    with pytest.raises(ValueError,
            match='BibTex entry is not in Bibmanager database'):
        pm.set_pdf(key, pdf)


def test_set_pdf_duplicate_pdf(mock_init_sample):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    pdf = 'file.pdf'
    bin_pdf = b'file.pdf'
    with pytest.raises(ValueError,
            match='Exactly one of pdf or bin_pdf must be not None'):
        pm.set_pdf(bib, pdf=pdf, bin_pdf=bin_pdf)


def test_set_pdf_undefined_pdf(mock_init_sample):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    with pytest.raises(ValueError,
            match='Exactly one of pdf or bin_pdf must be not None'):
        pm.set_pdf(bib)


def test_set_pdf_pathed_filename(mock_init_sample):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    bin_pdf = b'file.pdf'
    with pytest.raises(ValueError,
            match='filename must not have a path'):
        pm.set_pdf(bib, bin_pdf=bin_pdf, filename='./file.pdf')


def test_set_pdf_invalid_extension(mock_init_sample):
    bib = bm.find(key='ShowmanEtal2009apjRadGCM')
    bin_pdf = b'file.pdf'
    with pytest.raises(ValueError,
            match='Invalid filename, must have a .pdf extension'):
        pm.set_pdf(bib, bin_pdf=bin_pdf, filename='pdf_file')


def test_request_ads_success(capsys, reqs):
    req = pm.request_ads('success', source='journal')
    captured = capsys.readouterr()
    assert captured.out == ''
    assert req.ok is True
    assert req.status_code == 200


def test_request_ads_no_connection(capsys, reqs):
    req = pm.request_ads('exception', source='journal')
    captured = capsys.readouterr()
    assert captured.out == 'Failed to establish a web connection.\n'
    assert req is None


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


def test_fetch_journal(capsys, mock_init_sample, reqs):
    bibcode = '1957RvMP...29..547B'
    filename = None
    out_filename = pm.fetch(bibcode, filename=filename)
    captured = capsys.readouterr()
    assert captured.out == (
        "Fetching PDF file from Journal website:\n"
        "Saved PDF to: "
        f"'{u.BM_PDF()}Burbidge1957_RvMP_29_547.pdf'.\n")
    assert out_filename == f"{u.BM_PDF()}Burbidge1957_RvMP_29_547.pdf"


def test_fetch_journal_nonetwork(capsys, mock_init_sample, reqs):
    bibcode = '1918ApJ....48..154S'
    filename = None
    out_filename = pm.fetch(bibcode, filename=filename)
    captured = capsys.readouterr()
    assert captured.out == (
        "Fetching PDF file from Journal website:\n"
        "Failed to establish a web connection.\n")
    assert out_filename is None


def test_fetch_ads(capsys, mock_init_sample, reqs):
    bibcode = '1913LowOB...2...56S'
    filename = None
    out_filename = pm.fetch(bibcode, filename=filename)
    captured = capsys.readouterr()
    assert captured.out == (
        "Fetching PDF file from Journal website:\n"
        "Request failed with status code 403: Forbidden\n"
        "Fetching PDF file from ADS website:\n"
        f"Saved PDF to: '{u.BM_PDF()}Slipher1913_LowOB_2_56.pdf'.\n")
    assert out_filename == f"{u.BM_PDF()}Slipher1913_LowOB_2_56.pdf"


def test_fetch_ads_nonetwork(capsys, mock_init_sample, reqs):
    bibcode = '2009ApJ...699..564S'
    filename = None
    out_filename = pm.fetch(bibcode, filename=filename)
    captured = capsys.readouterr()
    assert captured.out == (
        "Fetching PDF file from Journal website:\n"
        "Request failed with status code 403: Forbidden\n"
        "Fetching PDF file from ADS website:\n"
        "Failed to establish a web connection.\n")
    assert out_filename is None


def test_fetch_arxiv(capsys, mock_init_sample, reqs):
    bibcode = '1917PASP...29..206C'
    filename = None
    out_filename = pm.fetch(bibcode, filename=filename)
    captured = capsys.readouterr()
    assert captured.out == (
        "Fetching PDF file from Journal website:\n"
        "Request failed with status code 403: Forbidden\n"
        "Fetching PDF file from ADS website:\n"
        "Request failed with status code 404: NOT FOUND\n"
        "Fetching PDF file from ArXiv website:\n"
        "Saved PDF to: "
        f"'{u.BM_PDF()}Curtis1917_arxiv_PASP_29_206.pdf'.\n")
    assert out_filename == f"{u.BM_PDF()}Curtis1917_arxiv_PASP_29_206.pdf"


def test_fetch_arxiv_fail(capsys, mock_init_sample, reqs):
    bibcode = '2010arXiv1007.0324B'
    filename = None
    out_filename = pm.fetch(bibcode, filename=filename)
    captured = capsys.readouterr()
    assert captured.out == (
        "Fetching PDF file from Journal website:\n"
        "Request failed with status code 403: Forbidden\n"
        "Fetching PDF file from ADS website:\n"
        "Request failed with status code 404: NOT FOUND\n"
        "Fetching PDF file from ArXiv website:\n"
        "Request failed with status code 404: NOT FOUND\n"
        "Could not fetch PDF from any source.\n")
    assert out_filename is None


def test_fetch_non_database(tmp_path, capsys, mock_init, reqs):
    os.chdir(tmp_path)
    bibcode = '1957RvMP...29..547B'
    filename = None
    out_filename = pm.fetch(bibcode, filename=filename)
    captured = capsys.readouterr()
    assert captured.out == (
        "Fetching PDF file from Journal website:\n"
        "Saved PDF to: '1957RvMP...29..547B.pdf'.\n"
        "(Note that BibTex entry is not in the Bibmanager database)\n")
    assert out_filename == f"{bibcode}.pdf"


def test_fetch_pathed_filename(mock_init_sample, reqs):
    bibcode = '1917PASP...29..206C'
    filename = 'path/file.pdf'
    with pytest.raises(ValueError, match='filename must not have a path'):
        pm.fetch(bibcode, filename=filename)


def test_fetch_invalid_filename(mock_init_sample, reqs):
    bibcode = '1917PASP...29..206C'
    filename = 'pdf_file'
    with pytest.raises(ValueError,
            match='Invalid filename, must have a .pdf extension'):
        pm.fetch(bibcode, filename=filename)

