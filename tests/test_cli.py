import os
import sys
import filecmp
import pathlib
import pytest

import bibmanager
import bibmanager.utils as u
import bibmanager.ads_manager    as am
import bibmanager.bib_manager    as bm
import bibmanager.config_manager as cm
import bibmanager.__main__ as cli


# Main help text:
main_description = "\n".join([f"  {line}" for line in
                              cli.main_description.strip().split("\n")])
# Prepend and append rest of text:
main_description = ("usage: bibm [-h] [-v] command ...\n\n"
                    "optional arguments:\n"
                    "  -h, --help     show this help message and exit\n"
                    "  -v, --version  Show bibmanager's version.\n\n"
                    "These are the bibmanager commands:\n  \n"
                    + main_description + "\n\n  command\n")


def test_version(capsys):
    sys.argv = "bibm --version".split()
    try:
        cli.main()
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert captured.out == f"bibmanager version {bibmanager.__version__}\n"


def test_help(capsys):
    sys.argv = "bibm -h".split()
    try:
        cli.main()
    except:
        pass
    captured = capsys.readouterr()
    assert captured.out == main_description


def test_reset_all(capsys, mock_init):
    pathlib.Path(u.BM_DATABASE).touch()
    pathlib.Path(u.BM_BIBFILE).touch()
    cm.set("ads_display", "10")
    captured = capsys.readouterr()
    # Simulate user input:
    sys.argv = "bibm reset".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "Initializing new bibmanager database.\n" \
                           "Resetting config parameters.\n"
    assert set(os.listdir(u.HOME)) == set(["config", "examples"])
    assert filecmp.cmp(u.HOME+"config", u.ROOT+"config")


def test_reset_database(capsys, mock_init):
    pathlib.Path(u.BM_DATABASE).touch()
    pathlib.Path(u.BM_BIBFILE).touch()
    cm.set("ads_display", "10")
    captured = capsys.readouterr()
    # Simulate user input:
    sys.argv = "bibm reset -d".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "Initializing new bibmanager database.\n"
    # filecmp does not seem to work fine, will do manually:
    # assert not filecmp.cmp(u.HOME+"config", u.ROOT+"config")
    with open(u.ROOT+"config", "r") as f:
        rconfig = f.read()
    with open(u.HOME+"config", "r") as f:
        hconfig = f.read()
    assert rconfig != hconfig
    assert set(os.listdir(u.HOME)) == set(["config", "examples"])


def test_reset_config(capsys, mock_init):
    pathlib.Path(u.BM_DATABASE).touch()
    pathlib.Path(u.BM_BIBFILE).touch()
    # Simulate user input:
    sys.argv = "bibm reset -c".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "Resetting config parameters.\n"
    assert filecmp.cmp(u.HOME+"config", u.ROOT+"config")
    assert set(os.listdir(u.HOME)) == \
        set(["bm_database.pickle", "bm_bibliography.bib", "config", "examples"])


def test_reset_keep_database(capsys, mock_init_sample):
    bibfile = u.HOME+"examples/sample.bib"
    # Simulate user input:
    sys.argv = f"bibm reset {bibfile}".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"Initializing new bibmanager database with BibTeX file: '{bibfile}'.\n" \
                           "Resetting config parameters.\n"
    assert set(os.listdir(u.HOME)) == set(["bm_database.pickle",
                                  "bm_bibliography.bib", "config", "examples"])
    bibs = bm.loadfile(bibfile)
    assert len(bibs) == 17


def test_reset_error(capsys, mock_init):
    # Simulate user input:
    sys.argv = f"bibm reset fake_file.bib".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out \
           == "\nError: Input BibTeX file 'fake_file.bib' does not exist.\n"


def test_merge_default(capsys, mock_init):
    bibfile = u.HOME+"examples/sample.bib"
    # Simulate user input:
    sys.argv = f"bibm merge {bibfile}".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out  == "\nMerged 17 new entries.\n\n" \
                  f"Merged BibTeX file '{bibfile}' into bibmanager database.\n"


def test_merge_error(capsys, mock_init):
    # Simulate user input:
    sys.argv = f"bibm merge fake_file.bib".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out \
           == "\nError: Input BibTeX file 'fake_file.bib' does not exist.\n"


# cli_edit() and cli_add() are direct, calls (no need for testing).

@pytest.mark.parametrize('mock_prompt_session', [['']], indirect=True)
def test_search_null(capsys, mock_init_sample, mock_prompt_session):
    # Expect empty return (basically check bibm does not complain).
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "(Press 'tab' for autocomplete)\n\n"


@pytest.mark.parametrize('mock_prompt_session',
    [['year:1984'],
     ['year: 1984'],
     ['year:1984-1985'],
     ['year:-1884'],
     ['year:2020-']], indirect=True)
def test_search_year(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "(Press 'tab' for autocomplete)\n\n"


@pytest.mark.parametrize('mock_prompt_session',
    [['year:1984a']], indirect=True)
def test_search_year_invalid(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == ("(Press 'tab' for autocomplete)\n\n"
                            "\nInvalid format for input year: 1984a\n")

@pytest.mark.parametrize('mock_prompt_session',
    [['author:"oliphant"'],
     ['author:"oliphant, t"']], indirect=True)
def test_search_author(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: SciPy: Open source scientific tools for Python, 2001
Authors: Jones, Eric; et al.
key: JonesEtal2001scipy

Title: Numpy: A guide to NumPy, 2006
Authors: Oliphant, Travis
key: Oliphant2006numpy\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"^oliphant"'],
     ['author:"^oliphant, t"']], indirect=True)
def test_search_first_author(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Numpy: A guide to NumPy, 2006
Authors: Oliphant, Travis
key: Oliphant2006numpy\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"oliphant" author:"jones, e"']], indirect=True)
def test_search_multiple_authors(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: SciPy: Open source scientific tools for Python, 2001
Authors: Jones, Eric; et al.
key: JonesEtal2001scipy\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"oliphant, t" year:2006']], indirect=True)
def test_search_author_year(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Numpy: A guide to NumPy, 2006
Authors: Oliphant, Travis
key: Oliphant2006numpy\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"oliphant, t" year:2006 year:2001']], indirect=True)
def test_search_author_year_ignore_second_year(capsys, mock_init_sample,
        mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Numpy: A guide to NumPy, 2006
Authors: Oliphant, Travis
key: Oliphant2006numpy\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['title:"HD 209458b" title:"atmospheric circulation"']], indirect=True)
def test_search_multiple_title_kws(capsys, mock_init_sample,
        mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Atmospheric Circulation of Hot Jupiters: Coupled Radiative-Dynamical
       General Circulation Model Simulations of HD 189733b and HD 209458b,
       2009
Authors: {Showman}, Adam P.; et al.
key: ShowmanEtal2009apjRadGCM\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['bibcode:2013A&A...558A..33A'],
     ['bibcode:2013A%26A...558A..33A']], indirect=True)
def test_search_bibcode(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Astropy: A community Python package for astronomy, 2013
Authors: {Astropy Collaboration}; et al.
key: Astropycollab2013aaAstropy\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['bibcode:1917PASP...29..206C bibcode:1918ApJ....48..154S']],
    indirect=True)
def test_search_multiple_bibcodes(capsys, mock_init_sample,
        mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Novae in the Spiral Nebulae and the Island Universe Theory, 1917
Authors: {Curtis}, H. D.
key: Curtis1917paspIslandUniverseTheory

Title: Studies based on the colors and magnitudes in stellar clusters. VII.
       The distances, distribution in space, and dimensions of 69 globular
       clusters., 1918
Authors: {Shapley}, H.
key: Shapley1918apjDistanceGlobularClusters\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['key:Shapley1918apjDistanceGlobularClusters']], indirect=True)
def test_search_key(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Studies based on the colors and magnitudes in stellar clusters. VII.
       The distances, distribution in space, and dimensions of 69 globular
       clusters., 1918
Authors: {Shapley}, H.
key: Shapley1918apjDistanceGlobularClusters\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['key:Curtis1917paspIslandUniverseTheory key:Shapley1918apjDistanceGlobularClusters']],
    indirect=True)
def test_search_multiple_keys(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Novae in the Spiral Nebulae and the Island Universe Theory, 1917
Authors: {Curtis}, H. D.
key: Curtis1917paspIslandUniverseTheory

Title: Studies based on the colors and magnitudes in stellar clusters. VII.
       The distances, distribution in space, and dimensions of 69 globular
       clusters., 1918
Authors: {Shapley}, H.
key: Shapley1918apjDistanceGlobularClusters\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_search_verbosity_zero(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Synthesis of the Elements in Stars, 1957
Authors: {Burbidge}, E. Margaret; et al.
key: BurbidgeEtal1957rvmpStellarElementSynthesis\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_search_verbosity_one(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search -v".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Synthesis of the Elements in Stars, 1957
Authors: {Burbidge}, E. Margaret; et al.
bibcode:   1957RvMP...29..547B
ADS url:   https://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B
key: BurbidgeEtal1957rvmpStellarElementSynthesis\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_search_verbosity_two(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search -vv".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Title: Synthesis of the Elements in Stars, 1957
Authors: {Burbidge}, E. Margaret; {Burbidge}, G. R.; {Fowler}, William A.; and
         {Hoyle}, F.
bibcode:   1957RvMP...29..547B
ADS url:   https://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B
key: BurbidgeEtal1957rvmpStellarElementSynthesis\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_search_verbosity_three(capfd, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search -vvv".split()
    cli.main()
    captured = capfd.readouterr()
    assert captured.out == '''(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0;38;5;248;3m\r\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\r\n\x1b[0m\x1b[0;38;5;34;1;4m@ARTICLE\x1b[0m{\x1b[0;38;5;142mBurbidgeEtal1957rvmpStellarElementSynthesis\x1b[0m,\x1b[0m\r\n       \x1b[0;38;5;33mauthor\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130m{\x1b[0;38;5;130mBurbidge\x1b[0;38;5;130m}\x1b[0;38;5;130m, E. Margaret and \x1b[0;38;5;130m{\x1b[0;38;5;130mBurbidge\x1b[0;38;5;130m}\x1b[0;38;5;130m, G.~R. and \x1b[0;38;5;130m{\x1b[0;38;5;130mFowler\x1b[0;38;5;130m}\x1b[0;38;5;130m, William A.\r\n        and \x1b[0;38;5;130m{\x1b[0;38;5;130mHoyle\x1b[0;38;5;130m}\x1b[0;38;5;130m, F.\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n        \x1b[0;38;5;33mtitle\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;130m"\x1b[0;38;5;130m{\x1b[0;38;5;130mSynthesis of the Elements in Stars\x1b[0;38;5;130m}\x1b[0;38;5;130m"\x1b[0m,\x1b[0m\r\n      \x1b[0;38;5;33mjournal\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130mReviews of Modern Physics\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n         \x1b[0;38;5;33myear\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;30m1957\x1b[0m,\x1b[0m\r\n        \x1b[0;38;5;33mmonth\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;124mJan\x1b[0m,\x1b[0m\r\n       \x1b[0;38;5;33mvolume\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130m29\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n        \x1b[0;38;5;33mpages\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130m547-650\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n          \x1b[0;38;5;33mdoi\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130m10.1103/RevModPhys.29.547\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n       \x1b[0;38;5;33madsurl\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B\x1b[0;38;5;130m}\x1b[0m,\x1b[0m\r\n      \x1b[0;38;5;33madsnote\x1b[0m \x1b[0m=\x1b[0m \x1b[0;38;5;130m{\x1b[0;38;5;130mProvided by the SAO/NASA Astrophysics Data System\x1b[0;38;5;130m}\x1b[0m\r\n\x1b[0m}\x1b[0m\r\n\x1b[0m\r\n\x1b[0m\x1b[0m'''


def test_export_bibfile(capsys, mock_init_sample):
    sys.argv = "bibm export my_file.bib".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_export_invalid_path(capsys, mock_init_sample):
    sys.argv = "bibm export invalid_path/my_file.bib".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "\nError: Output dir does not exists: " \
                          f"'{os.path.realpath('invalid_path')}'\n"


def test_export_invalid_bbl(capsys, mock_init_sample):
    sys.argv = "bibm export my_file.bbl".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nSorry, export to .bbl output is not implemented yet.\n"


def test_export_invalid_extension(capsys, mock_init_sample):
    sys.argv = "bibm export my_file.tex".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: Invalid file extension ('.tex'), must be '.bib' or '.bbl'.\n"


def test_config_display(capsys, mock_init_sample):
    sys.argv = "bibm config".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == ("\nbibmanager configuration file:\n"
                              "PARAMETER    VALUE\n"
                              "-----------  -----\n"
                              "style        autumn\n"
                              "text_editor  default\n"
                              "paper        letter\n"
                              "ads_token    None\n"
                              "ads_display  20\n")

def test_config_help(capsys, mock_init_sample):
    sys.argv = "bibm config paper".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == ("\nThe 'paper' parameter sets the default paper "
      "format for latex compilation outputs\n"
      "(not for pdflatex, which is automatic).  Typical options are 'letter'\n"
      "(e.g., for ApJ articles) or 'A4' (e.g., for A&A).\n\n"
      "The current paper format is: 'letter'.\n")


def test_config_set(capsys, mock_init_sample):
    sys.argv = "bibm config paper A4".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == ("paper updated to: A4.\n")


def test_config_invalid_param(capsys, mock_init_sample):
    sys.argv = "bibm config invalid_param A4".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """
Error: 'invalid_param' is not a valid bibmanager config parameter.
The available parameters are:
  ['style', 'text_editor', 'paper', 'ads_token', 'ads_display']\n"""


def test_config_invalid_value(capsys, mock_init_sample):
    sys.argv = "bibm config ads_display A224".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: The ads_display value must be a positive integer.\n"


# cli_bibtex(), cli_latex(), and cli_pdflatex() are direct
# calls to their respective functions.  So, no need to test the
# command-line interface).


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"^fortney, j" year:2000-2018 property:refereed']], indirect=True)
def test_ads_search(capsys, reqs, mock_prompt_session):
    cm.set('ads_display', '2')
    am.search.__defaults__ = 0, 2, 'pubdate+desc'
    sys.argv = "bibm ads-search".split()
    captured = capsys.readouterr()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""(Press 'tab' for autocomplete)\n

Title: A deeper look at Jupiter
Authors: Fortney, Jonathan
adsurl:  https://ui.adsabs.harvard.edu/abs/2018Natur.555..168F
{u.BOLD}bibcode{u.END}: 2018Natur.555..168F

Title: The Hunt for Planet Nine: Atmosphere, Spectra, Evolution, and
       Detectability
Authors: Fortney, Jonathan J.; et al.
adsurl:  https://ui.adsabs.harvard.edu/abs/2016ApJ...824L..25F
{u.BOLD}bibcode{u.END}: 2016ApJ...824L..25F

Showing entries 1--2 out of 26 matches.  To show the next set, execute:
bibm ads-search -n\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"^fortney, j" year:2000-2018 property:refereed']],
    indirect=True)
def test_ads_search_next(capsys, reqs, mock_prompt_session):
    cm.set('ads_display', '2')
    am.search.__defaults__ = 0, 2, 'pubdate+desc'
    sys.argv = "bibm ads-search".split()
    cli.main()
    captured = capsys.readouterr()
    sys.argv = "bibm ads-search -n".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""
Title: A Framework for Characterizing the Atmospheres of Low-mass Low-density
       Transiting Planets
Authors: Fortney, Jonathan J.; et al.
adsurl:  https://ui.adsabs.harvard.edu/abs/2013ApJ...775...80F
{u.BOLD}bibcode{u.END}: 2013ApJ...775...80F

Title: On the Carbon-to-oxygen Ratio Measurement in nearby Sun-like Stars:
       Implications for Planet Formation and the Determination of Stellar
       Abundances
Authors: Fortney, Jonathan J.
adsurl:  https://ui.adsabs.harvard.edu/abs/2012ApJ...747L..27F
{u.BOLD}bibcode{u.END}: 2012ApJ...747L..27F

Showing entries 3--4 out of 26 matches.  To show the next set, execute:
bibm ads-search -n\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['', 'author:"^fortney, j" year:2000-2018 property:refereed']],
    indirect=True)
def test_ads_search_empty_next(capsys, reqs, mock_prompt_session, mock_init):
    cm.set('ads_display', '2')
    am.search.__defaults__ = 0, 2, 'pubdate+desc'
    sys.argv = "bibm ads-search".split()
    cli.main()
    captured = capsys.readouterr()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""(Press 'tab' for autocomplete)\n

Title: A Framework for Characterizing the Atmospheres of Low-mass Low-density
       Transiting Planets
Authors: Fortney, Jonathan J.; et al.
adsurl:  https://ui.adsabs.harvard.edu/abs/2013ApJ...775...80F
{u.BOLD}bibcode{u.END}: 2013ApJ...775...80F

Title: On the Carbon-to-oxygen Ratio Measurement in nearby Sun-like Stars:
       Implications for Planet Formation and the Determination of Stellar
       Abundances
Authors: Fortney, Jonathan J.
adsurl:  https://ui.adsabs.harvard.edu/abs/2012ApJ...747L..27F
{u.BOLD}bibcode{u.END}: 2012ApJ...747L..27F

Showing entries 3--4 out of 26 matches.  To show the next set, execute:
bibm ads-search -n\n"""

@pytest.mark.parametrize('mock_prompt_session',
    [['', 'author:"^fortney, j" year:2000-2018 property:refereed']],
    indirect=True)
def test_ads_search_next_empty(capsys, reqs, mock_prompt_session, mock_init):
    sys.argv = "bibm ads-search -n".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""There are no more entries for this querry.\n"""


@pytest.mark.parametrize('mock_prompt_session', [['']], indirect=True)
def test_ads_search_empty(capsys, reqs, mock_prompt_session, mock_init):
    sys.argv = "bibm ads-search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""(Press 'tab' for autocomplete)\n\n"""


@pytest.mark.skip(reason="Is this even possible?")
def test_ads_add():
    pass


# cli_ads_update() is a direct call to its respective function in
# ads_manager.  So, no need to test the command-line interface.
