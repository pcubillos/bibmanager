# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import sys
import pathlib
import pickle
import pytest

import bibmanager
import bibmanager.utils as u
import bibmanager.ads_manager as am
import bibmanager.bib_manager as bm
import bibmanager.config_manager as cm
import bibmanager.__main__ as cli
from conftest import nentries


# Main help text:
main_description = "\n".join([
    f"  {line}" for line in cli.main_description.strip().split("\n")])

# Prepend and append rest of text:
main_description = (
    "usage: bibm [-h] [-v] command ...\n\n"
    "optional arguments:\n"
    "  -h, --help     show this help message and exit\n"
    "  -v, --version  Show bibmanager's version.\n\n"
    "These are the bibmanager commands:\n  \n"
    + main_description + "\n\n  command\n")

ads_add_prompt = \
"""Enter pairs of ADS bibcodes and BibTeX keys (plus optional tags)
Use one line for each BibTeX entry, separate fields with blank spaces.
(press META+ENTER or ESCAPE ENTER when done):

"""

expected_sympy = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mSymPy: symbolic computing in Python, 2017\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mMeurer, Aaron; et al.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mMeurerEtal2017pjcsSYMPY\x1b[0m\r\n\x1b[0m"

expected_slipher = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mThe radial velocity of the Andromeda Nebula, 1913\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Slipher}, V. M.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mSlipher1913lobAndromedaRarialVelocity\x1b[0m\r\n\x1b[0m"


def test_cli_version(capsys):
    sys.argv = "bibm --version".split()
    try:
        cli.main()
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert captured.out == f"bibmanager version {bibmanager.__version__}\n"


def test_cli_help(capsys):
    sys.argv = "bibm -h".split()
    try:
        cli.main()
    except:
        pass
    captured = capsys.readouterr()
    assert captured.out == main_description


def test_cli_reset_all(capsys, mock_init_sample):
    pathlib.Path(u.BM_BIBFILE()).touch()
    cm.set("ads_display", "10")
    captured = capsys.readouterr()
    # Simulate user input:
    sys.argv = "bibm reset".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "Initializing new bibmanager database.\n" \
                           "Resetting config parameters.\n"
    assert set(os.listdir(u.HOME)) == set(["config", "examples", "pdf"])


def test_cli_reset_database(capsys, mock_init_sample):
    pathlib.Path(u.BM_BIBFILE()).touch()
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
    assert set(os.listdir(u.HOME)) == set(["config", "examples", "pdf"])


def test_cli_reset_config(capsys, mock_init_sample):
    pathlib.Path(u.BM_BIBFILE()).touch()
    # Simulate user input:
    sys.argv = "bibm reset -c".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "Resetting config parameters.\n"
    #assert filecmp.cmp(u.HOME+"config", u.ROOT+"config")
    assert set(os.listdir(u.HOME)) == set([
        "bm_database.pickle",
        "bm_bibliography.bib",
        "config",
        "examples",
        "pdf",
        ])


def test_cli_reset_keep_database(capsys, mock_init_sample):
    bibfile = u.HOME + "examples/sample.bib"
    # Simulate user input:
    sys.argv = f"bibm reset {bibfile}".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        f"Initializing new bibmanager database with BibTeX file: '{bibfile}'.\n"
        "Resetting config parameters.\n")
    assert set(os.listdir(u.HOME)) == set([
        "bm_database.pickle",
        "bm_bibliography.bib",
        "config",
        "examples",
        "pdf",
        ])
    bibs = bm.read_file(bibfile)
    assert len(bibs) == nentries


def test_cli_reset_error(capsys, mock_init):
    # Simulate user input:
    sys.argv = "bibm reset fake_file.bib".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: Input BibTeX file 'fake_file.bib' does not exist.\n"


def test_cli_merge_default(capsys, mock_init):
    bibfile = u.HOME+"examples/sample.bib"
    # Simulate user input:
    sys.argv = f"bibm merge {bibfile}".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        f"\nMerged {nentries} new entries.\n\n"
        f"Merged BibTeX file '{bibfile}' into bibmanager database.\n")

def test_cli_merge_error(capsys, mock_init):
    # Simulate user input:
    sys.argv = "bibm merge fake_file.bib".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: Input BibTeX file 'fake_file.bib' does not exist.\n"


# cli_edit() and cli_add() are direct calls (no need for testing).


@pytest.mark.parametrize('mock_prompt_session', [['']], indirect=True)
def test_cli_search_null(capsys, mock_init_sample, mock_prompt_session):
    # Expect empty return (basically check bibm does not complain).
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "(Press 'tab' for autocomplete)\n\n"


@pytest.mark.parametrize('mock_prompt_session',
    [['year:1913'],
     ['year: 1913'],
     ['year:1910-1913'],
     ['year:-1913']], indirect=True)
def test_cli_search_year(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == expected_slipher


@pytest.mark.parametrize('mock_prompt_session', [['year:2020-']], indirect=True)
def test_cli_search_year_open_e(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mArray programming with NumPy, 2020\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Harris}, Charles R.; et al.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mHarrisEtal2020natNumpy\x1b[0m\r\n\x1b[0m\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mSciPy 1.0: fundamental algorithms for scientific computing in Python,\r\n    2020\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Virtanen}, Pauli; et al.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mVirtanenEtal2020natmeScipy\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['year:1984a']], indirect=True)
def test_cli_search_year_invalid(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "(Press 'tab' for autocomplete)\n\n"


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"virtanen"'],
     ['author:"Virtanen"'],
     ['author:"virtanen, p"']], indirect=True)
def test_cli_search_author(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mArray programming with NumPy, 2020\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Harris}, Charles R.; et al.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mHarrisEtal2020natNumpy\x1b[0m\r\n\x1b[0m\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mSciPy 1.0: fundamental algorithms for scientific computing in Python,\r\n    2020\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Virtanen}, Pauli; et al.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mVirtanenEtal2020natmeScipy\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"^virtanen"'],
     ['author:"^virtanen, p"']], indirect=True)
def test_cli_search_first_author(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mSciPy 1.0: fundamental algorithms for scientific computing in Python,\r\n    2020\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Virtanen}, Pauli; et al.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mVirtanenEtal2020natmeScipy\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"granger" author:"meurer, a"']], indirect=True)
def test_cli_search_multiple_authors(
        capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == expected_sympy


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"granger" year:2017']], indirect=True)
def test_cli_search_author_year(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == expected_sympy


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"slipher" year:1913 year:2001']], indirect=True)
def test_cli_search_author_year_ignore_second_year(capsys, mock_init_sample,
        mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == expected_slipher


@pytest.mark.parametrize('mock_prompt_session',
    [['title:"Andromeda" title:"radial velocity"']], indirect=True)
def test_cli_search_multiple_title_kws(capsys, mock_init_sample,
        mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == expected_slipher


@pytest.mark.parametrize('mock_prompt_session',
    [['bibcode:2013A&A...558A..33A'],
     ['bibcode:2013A%26A...558A..33A']], indirect=True)
def test_cli_search_bibcode(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mAstropy: A community Python package for astronomy, 2013\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Astropy Collaboration}; et al.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mAstropycollab2013aaAstropy\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['bibcode:1917PASP...29..206C bibcode:1918ApJ....48..154S']],
    indirect=True)
def test_cli_search_multiple_bibcodes(capsys, mock_init_sample,
        mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mNovae in the Spiral Nebulae and the Island Universe Theory, 1917\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Curtis}, H. D.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mCurtis1917paspIslandUniverseTheory\x1b[0m\r\n\x1b[0m\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mStudies based on the colors and magnitudes in stellar clusters. VII.\r\n    The distances, distribution in space, and dimensions of 69 globular\r\n    clusters., 1918\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Shapley}, H.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mShapley1918apjDistanceGlobularClusters\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize(
    'mock_prompt_session',
    [['key:Slipher1913lobAndromedaRarialVelocity']],
    indirect=True)
def test_cli_search_key(capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == expected_slipher


@pytest.mark.parametrize('mock_prompt_session',
    [['key:Curtis1917paspIslandUniverseTheory key:Shapley1918apjDistanceGlobularClusters']],
    indirect=True)
def test_cli_search_multiple_keys(capsys, mock_init_sample,
        mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mNovae in the Spiral Nebulae and the Island Universe Theory, 1917\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Curtis}, H. D.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mCurtis1917paspIslandUniverseTheory\x1b[0m\r\n\x1b[0m\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mStudies based on the colors and magnitudes in stellar clusters. VII.\r\n    The distances, distribution in space, and dimensions of 69 globular\r\n    clusters., 1918\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Shapley}, H.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mShapley1918apjDistanceGlobularClusters\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_cli_search_verbosity_negative(
        capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search -v -1".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n
Keys:
BurbidgeEtal1957rvmpStellarElementSynthesis\n"""


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_cli_search_verbosity_default_zero(capsys, mock_init_sample,
        mock_prompt_session):
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mSynthesis of the Elements in Stars, 1957\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Burbidge}, E. Margaret; et al.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mBurbidgeEtal1957rvmpStellarElementSynthesis\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_cli_search_verbosity_explicitly_zero(
        capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search -v 0".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mSynthesis of the Elements in Stars, 1957\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Burbidge}, E. Margaret; et al.\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mBurbidgeEtal1957rvmpStellarElementSynthesis\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_cli_search_verbosity_deprecated_one(
        capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search -v".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\nDeprecation warning:\nThe verbosity argument must be set to an integer value\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mSynthesis of the Elements in Stars, 1957\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Burbidge}, E. Margaret; et al.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;130m1957RvMP...29..547B\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mBurbidgeEtal1957rvmpStellarElementSynthesis\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_cli_search_verbosity_one(
        capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search -v 1".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mSynthesis of the Elements in Stars, 1957\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Burbidge}, E. Margaret; et al.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;130m1957RvMP...29..547B\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mBurbidgeEtal1957rvmpStellarElementSynthesis\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Slipher, V"']], indirect=True)
def test_cli_search_verbosity_meta(
        capsys, mock_init_sample, mock_prompt_session):
    sys.argv = "bibm search -v 1".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mThe radial velocity of the Andromeda Nebula, 1913\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Slipher}, V. M.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/1913LowOB...2...56S\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;130m1913LowOB...2...56S\x1b[0m\r\n\x1b[0;38;5;33mPDF file\x1b[0m: \x1b[0;38;5;248;3mSlipher1913.pdf\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mSlipher1913lobAndromedaRarialVelocity\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_cli_search_verbosity_two(capsys, mock_init_sample,mock_prompt_session):
    sys.argv = "bibm search -v 2".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mSynthesis of the Elements in Stars, 1957\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130m{Burbidge}, E. Margaret; {Burbidge}, G. R.; {Fowler}, William A.; and\r\n    {Hoyle}, F.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;130m1957RvMP...29..547B\x1b[0m\r\n\x1b[0;38;5;33mkey\x1b[0m: \x1b[0;38;5;142mBurbidgeEtal1957rvmpStellarElementSynthesis\x1b[0m\r\n\x1b[0m"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"Burbidge, E"']], indirect=True)
def test_cli_search_verbosity_three(capfd, mock_init_sample,
        mock_prompt_session):
    sys.argv = "bibm search -v 3".split()
    cli.main()
    captured = capfd.readouterr()
    assert captured.out == '(Press \'tab\' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0;38;5;248;3m\r\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\r\n\x1b[0m\x1b[0;38;5;248;3m\x1b[0;38;5;34;1;4m@ARTICLE\x1b[0m{\x1b[0;38;5;142mBurbidgeEtal1957rvmpStellarElementSynthesis\x1b[0m,\r\n       \x1b[0;38;5;33mauthor\x1b[0m = \x1b[0;38;5;130m{{Burbidge}, E. Margaret and {Burbidge}, G.~R. and {Fowler}, William A.\r\n        and {Hoyle}, F.}\x1b[0m,\r\n        \x1b[0;38;5;33mtitle\x1b[0m = \x1b[0;38;5;130m"{Synthesis of the Elements in Stars}"\x1b[0m,\r\n      \x1b[0;38;5;33mjournal\x1b[0m = \x1b[0;38;5;130m{Reviews of Modern Physics}\x1b[0m,\r\n         \x1b[0;38;5;33myear\x1b[0m = \x1b[0;38;5;30m1957\x1b[0m,\r\n        \x1b[0;38;5;33mmonth\x1b[0m = \x1b[0;38;5;124mJan\x1b[0m,\r\n       \x1b[0;38;5;33mvolume\x1b[0m = \x1b[0;38;5;130m{29}\x1b[0m,\r\n        \x1b[0;38;5;33mpages\x1b[0m = \x1b[0;38;5;130m{547-650}\x1b[0m,\r\n          \x1b[0;38;5;33mdoi\x1b[0m = \x1b[0;38;5;130m{10.1103/RevModPhys.29.547}\x1b[0m,\r\n       \x1b[0;38;5;33madsurl\x1b[0m = \x1b[0;38;5;130m{https://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B}\x1b[0m,\r\n      \x1b[0;38;5;33madsnote\x1b[0m = \x1b[0;38;5;130m{Provided by the SAO/NASA Astrophysics Data System}\x1b[0m\r\n}\r\n\r\n\x1b[0m'


@pytest.mark.skip(reason='How in the world can I test this?')
def test_cli_search_bottom_toolbar():
    pass


def test_cli_export_bibfile(capsys, tmp_path, mock_init_sample):
    bibfile = f'{tmp_path}/my_file.bib'
    sys.argv = f"bibm export {bibfile}".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_cli_export_invalid_path(capsys, mock_init_sample):
    sys.argv = "bibm export invalid_path/my_file.bib".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "\nError: Output dir does not exists: "
        f"'{os.path.realpath('invalid_path')}'\n")


def test_cli_export_invalid_bbl(capsys, mock_init_sample):
    sys.argv = "bibm export my_file.bbl".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nSorry, export to .bbl output is not implemented yet.\n"


def test_cli_export_invalid_extension(capsys, mock_init_sample):
    sys.argv = "bibm export my_file.tex".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: Invalid file extension ('.tex'), must be '.bib' or '.bbl'.\n"


def test_cli_config_display(capsys, mock_init_sample):
    sys.argv = "bibm config".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "\nbibmanager configuration file:\n"
        "PARAMETER    VALUE\n"
        "-----------  -----\n"
        "style        autumn\n"
        "text_editor  default\n"
        "paper        letter\n"
        "ads_token    None\n"
        "ads_display  20\n"
       f"home         {u.HOME}\n")

def test_cli_config_help(capsys, mock_init_sample):
    sys.argv = "bibm config paper".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == ("\nThe 'paper' parameter sets the default paper "
      "format for latex compilation outputs\n"
      "(not for pdflatex, which is automatic).  Typical options are 'letter'\n"
      "(e.g., for ApJ articles) or 'A4' (e.g., for A&A).\n\n"
      "The current paper format is: 'letter'.\n")


def test_cli_config_set(capsys, mock_init_sample):
    sys.argv = "bibm config paper A4".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == ("paper updated to: A4.\n")


def test_cli_config_invalid_param(capsys, mock_init_sample):
    sys.argv = "bibm config invalid_param A4".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """
Error: 'invalid_param' is not a valid bibmanager config parameter.
The available parameters are:
  ['style', 'text_editor', 'paper', 'ads_token', 'ads_display', 'home']\n"""


def test_cli_config_invalid_value(capsys, mock_init_sample):
    sys.argv = "bibm config ads_display A224".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: The ads_display value must be a positive integer.\n"


# cli_bibtex(), cli_latex(), and cli_pdflatex() are direct
# calls to their respective functions.  So, no need to test the
# command-line interface).


@pytest.mark.parametrize('directive', ['latex', 'pdflatex'])
def test_cli_latex_error(capsys, mock_init_sample, directive):
    sys.argv = f"bibm {directive} non_existing_file.tex".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: Input .tex file does not exist\n"


@pytest.mark.parametrize('directive', ['latex', 'pdflatex'])
def test_cli_latex_invalid_extension(capsys, mock_init_sample, directive):
    sys.argv = f"bibm {directive} invalid_file.tecs".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: Input file does not have a .tex extension\n"


@pytest.mark.parametrize(
    'mock_prompt_session',
    [['author:"^fortney, j" year:2000-2018 property:refereed']],
    indirect=True)
def test_cli_ads_search(capsys, reqs, mock_prompt_session, mock_init):
    cm.set('ads_display', '2')
    am.search.__defaults__ = 0, 2, 'pubdate+desc'
    sys.argv = "bibm ads-search".split()
    captured = capsys.readouterr()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mA deeper look at Jupiter\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2018Natur.555..168F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2018Natur.555..168F\x1b[0m\r\n\x1b[0m\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mThe Hunt for Planet Nine: Atmosphere, Spectra, Evolution, and\r\n    Detectability\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan J.; et al.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2016ApJ...824L..25F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2016ApJ...824L..25F\x1b[0m\r\n\x1b[0m\nShowing entries 1--2 out of 26 matches.  To show the next set, execute:\nbibm ads-search -n\n"
    assert captured.out == expected_output


@pytest.mark.parametrize(
    'mock_prompt_session',
    [['author:"^fortney, j" year:2000-2018 property:refereed']],
    indirect=True)
def test_cli_ads_search_next(capsys, reqs, mock_prompt_session, mock_init):
    cm.set('ads_display', '2')
    am.search.__defaults__ = 0, 2, 'pubdate+desc'
    sys.argv = "bibm ads-search".split()
    cli.main()
    captured = capsys.readouterr()
    sys.argv = "bibm ads-search -n".split()
    cli.main()
    captured = capsys.readouterr()
    expected_output = '\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mA Framework for Characterizing the Atmospheres of Low-mass Low-density\r\n    Transiting Planets\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan J.; et al.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2013ApJ...775...80F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2013ApJ...775...80F\x1b[0m\r\n\x1b[0m\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mOn the Carbon-to-oxygen Ratio Measurement in nearby Sun-like Stars:\r\n    Implications for Planet Formation and the Determination of Stellar\r\n    Abundances\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan J.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2012ApJ...747L..27F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2012ApJ...747L..27F\x1b[0m\r\n\x1b[0m\nShowing entries 3--4 out of 26 matches.  To show the next set, execute:\nbibm ads-search -n\n'
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['', 'author:"^fortney, j" year:2000-2018 property:refereed']],
    indirect=True)
def test_cli_ads_search_empty_next(
        capsys, reqs, mock_prompt_session, mock_init):
    cm.set('ads_display', '2')
    am.search.__defaults__ = 0, 2, 'pubdate+desc'
    sys.argv = "bibm ads-search".split()
    cli.main()
    captured = capsys.readouterr()
    cli.main()
    captured = capsys.readouterr()
    expected_output = "(Press 'tab' for autocomplete)\n\n\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mA Framework for Characterizing the Atmospheres of Low-mass Low-density\r\n    Transiting Planets\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan J.; et al.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2013ApJ...775...80F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2013ApJ...775...80F\x1b[0m\r\n\x1b[0m\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mOn the Carbon-to-oxygen Ratio Measurement in nearby Sun-like Stars:\r\n    Implications for Planet Formation and the Determination of Stellar\r\n    Abundances\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan J.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2012ApJ...747L..27F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2012ApJ...747L..27F\x1b[0m\r\n\x1b[0m\nShowing entries 3--4 out of 26 matches.  To show the next set, execute:\nbibm ads-search -n\n"
    assert captured.out == expected_output


@pytest.mark.parametrize('mock_prompt_session',
    [['', 'author:"^fortney, j" year:2000-2018 property:refereed']],
    indirect=True)
def test_cli_ads_search_next_empty(capsys, reqs, mock_prompt_session,mock_init):
    sys.argv = "bibm ads-search -n".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """There are no more entries for this query.\n"""


@pytest.mark.parametrize('mock_prompt_session', [['']], indirect=True)
def test_cli_ads_search_empty(capsys, reqs, mock_prompt_session, mock_init):
    sys.argv = "bibm ads-search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """(Press 'tab' for autocomplete)\n\n"""


def test_cli_ads_add_with_bibcode_key(capsys, reqs, mock_init):
    sys.argv = (
        'bibm ads-add '
        '1925PhDT.........1P Payne1925phdStellarAtmospheres').split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nMerged 1 new entries.""\n(Not counting updated references)\n"""
    bibs = bm.load()
    assert len(bibs) == 1
    assert repr(bibs[0]) == \
"""@PHDTHESIS{Payne1925phdStellarAtmospheres,
       author = {{Payne}, Cecilia Helena},
        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
     keywords = {Astronomy},
       school = {RADCLIFFE COLLEGE.},
         year = 1925,
        month = Jan,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""


def test_cli_ads_add_with_bibcode_key_1tag(capsys, reqs, mock_init):
    sys.argv = (
        'bibm ads-add '
        '1925PhDT.........1P Payne1925phdStellarAtmospheres thesis').split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nMerged 1 new entries.""\n(Not counting updated references)\n"""
    assert repr(bm.load()[0]) == \
"""tags: thesis
@PHDTHESIS{Payne1925phdStellarAtmospheres,
       author = {{Payne}, Cecilia Helena},
        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
     keywords = {Astronomy},
       school = {RADCLIFFE COLLEGE.},
         year = 1925,
        month = Jan,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""


def test_cli_ads_add_with_bibcode_key_tags(capsys, reqs, mock_init):
    sys.argv = (
        'bibm ads-add '
        '1925PhDT.........1P Payne1925phdStellarAtmospheres '
        'thesis stars').split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nMerged 1 new entries.""\n(Not counting updated references)\n"""
    assert repr(bm.load()[0]) == \
"""tags: thesis stars
@PHDTHESIS{Payne1925phdStellarAtmospheres,
       author = {{Payne}, Cecilia Helena},
        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
     keywords = {Astronomy},
       school = {RADCLIFFE COLLEGE.},
         year = 1925,
        month = Jan,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""


@pytest.mark.parametrize(
    'mock_prompt',
    [['1925PhDT.........1P Payne1925phdStellarAtmospheres']],
    indirect=True)
def test_cli_ads_add_prompt_bibcode_key(capsys, reqs, mock_prompt, mock_init):
    sys.argv = 'bibm ads-add'.split()
    cli.main()
    captured = capsys.readouterr()
    # Screen output:
    assert captured.out == (
        ads_add_prompt
        + "\nMerged 1 new entries.\n(Not counting updated references)\n")
    # Check that entry is in database:
    bibs = bm.load()
    assert len(bibs) == 1
    assert repr(bibs[0]) == \
"""@PHDTHESIS{Payne1925phdStellarAtmospheres,
       author = {{Payne}, Cecilia Helena},
        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
     keywords = {Astronomy},
       school = {RADCLIFFE COLLEGE.},
         year = 1925,
        month = Jan,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""


@pytest.mark.parametrize(
    'mock_prompt',
    [['1925PhDT.........1P Payne1925phdStellarAtmospheres thesis']],
    indirect=True)
def test_cli_ads_add_prompt_1tag(capsys, reqs, mock_prompt, mock_init):
    sys.argv = 'bibm ads-add'.split()
    cli.main()
    captured = capsys.readouterr()
    # Screen output:
    assert captured.out == (
        ads_add_prompt
        + "\nMerged 1 new entries.\n(Not counting updated references)\n")
    # Check that entry is in database:
    assert repr(bm.load()[0]) == \
"""tags: thesis
@PHDTHESIS{Payne1925phdStellarAtmospheres,
       author = {{Payne}, Cecilia Helena},
        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
     keywords = {Astronomy},
       school = {RADCLIFFE COLLEGE.},
         year = 1925,
        month = Jan,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""


@pytest.mark.parametrize(
    'mock_prompt',
    [['1925PhDT.........1P Payne1925phdStellarAtmospheres thesis stars']],
    indirect=True)
def test_cli_ads_add_prompt_tags(capsys, reqs, mock_prompt, mock_init):
    sys.argv = 'bibm ads-add'.split()
    cli.main()
    captured = capsys.readouterr()
    # Screen output:
    assert captured.out == (
        ads_add_prompt
        + "\nMerged 1 new entries.\n(Not counting updated references)\n")
    # Check that entry is in database:
    assert repr(bm.load()[0]) == \
"""tags: thesis stars
@PHDTHESIS{Payne1925phdStellarAtmospheres,
       author = {{Payne}, Cecilia Helena},
        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
     keywords = {Astronomy},
       school = {RADCLIFFE COLLEGE.},
         year = 1925,
        month = Jan,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""


@pytest.mark.parametrize(
    'mock_prompt',
    [['1925PhDT.........1P Payne1925phdStellarAtmospheres\n'
      '1957RvMP...29..547B BurbidgeEtal1957rvmpStellarSynthesis']],
    indirect=True)
def test_cli_ads_add_prompt_multiline_no_tags(
        capsys, reqs, mock_prompt, mock_init):
    sys.argv = 'bibm ads-add'.split()
    cli.main()
    captured = capsys.readouterr()
    # Screen output:
    assert captured.out == (
        ads_add_prompt
        + "\nMerged 2 new entries.\n(Not counting updated references)\n")
    # Check that entries are in database:
    bibs = bm.load()
    assert len(bibs) == 2
    assert repr(bibs[0]) == \
"""@ARTICLE{BurbidgeEtal1957rvmpStellarSynthesis,
       author = {{Burbidge}, E. Margaret and {Burbidge}, G.~R. and {Fowler}, William A. and {Hoyle}, F.},
        title = "{Synthesis of the Elements in Stars}",
      journal = {Reviews of Modern Physics},
         year = 1957,
        month = jan,
       volume = {29},
       number = {4},
        pages = {547-650},
          doi = {10.1103/RevModPhys.29.547},
       adsurl = {https://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""
    assert repr(bibs[1]) == \
"""@PHDTHESIS{Payne1925phdStellarAtmospheres,
       author = {{Payne}, Cecilia Helena},
        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
     keywords = {Astronomy},
       school = {RADCLIFFE COLLEGE.},
         year = 1925,
        month = Jan,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""


@pytest.mark.parametrize(
    'mock_prompt',
    [['1925PhDT.........1P Payne1925phdStellarAtmospheres thesis stars\n'
      '1957RvMP...29..547B BurbidgeEtal1957rvmpStellarSynthesis stars']],
    indirect=True)
def test_cli_ads_add_prompt_multiline_with_tags(
        capsys, reqs, mock_prompt, mock_init):
    sys.argv = 'bibm ads-add'.split()
    cli.main()
    captured = capsys.readouterr()
    # Screen output:
    assert captured.out == (
        ads_add_prompt
        + "\nMerged 2 new entries.\n(Not counting updated references)\n")
    # Check that entries are in database:
    bibs = bm.load()
    assert len(bibs) == 2
    assert repr(bibs[0]) == \
"""tags: stars
@ARTICLE{BurbidgeEtal1957rvmpStellarSynthesis,
       author = {{Burbidge}, E. Margaret and {Burbidge}, G.~R. and {Fowler}, William A. and {Hoyle}, F.},
        title = "{Synthesis of the Elements in Stars}",
      journal = {Reviews of Modern Physics},
         year = 1957,
        month = jan,
       volume = {29},
       number = {4},
        pages = {547-650},
          doi = {10.1103/RevModPhys.29.547},
       adsurl = {https://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""
    assert repr(bibs[1]) == \
"""tags: thesis stars
@PHDTHESIS{Payne1925phdStellarAtmospheres,
       author = {{Payne}, Cecilia Helena},
        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
     keywords = {Astronomy},
       school = {RADCLIFFE COLLEGE.},
         year = 1925,
        month = Jan,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""


@pytest.mark.parametrize('mock_prompt', [['']], indirect=True)
def test_cli_ads_add_prompt_empty(capsys, reqs, mock_prompt, mock_init):
    sys.argv = 'bibm ads-add'.split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == ads_add_prompt


def test_cli_ads_add_fail(capsys, reqs, mock_init):
    sys.argv = "bibm ads-add 1925PhDT.....X...1P Payne1925phdStars".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: There were no entries found for the requested bibcodes.\n"


@pytest.mark.parametrize('keycode',
    ['1957RvMP...29..547B',
     'BurbidgeEtal1957rvmpStellarElementSynthesis'])
def test_cli_fetch_keycode(capsys, mock_init_sample, reqs, keycode):
    sys.argv = f"bibm fetch {keycode}".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""Fetching PDF file from Journal website:
Saved PDF to: '{u.BM_PDF()}Burbidge1957_RvMP_29_547.pdf'.

To open the PDF file, execute:
bibm open BurbidgeEtal1957rvmpStellarElementSynthesis\n"""


def test_cli_fetch_keycode_filename(capsys, mock_init_sample, reqs):
    sys.argv = "bibm fetch 1957RvMP...29..547B Burbidge1957.pdf".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""Fetching PDF file from Journal website:
Saved PDF to: '{u.BM_PDF()}Burbidge1957.pdf'.

To open the PDF file, execute:
bibm open BurbidgeEtal1957rvmpStellarElementSynthesis\n"""


def test_cli_fetch_keycode_open(capsys, mock_init_sample, reqs, mock_call,
        mock_open):
    sys.argv = "bibm fetch 1957RvMP...29..547B -o".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""Fetching PDF file from Journal website:
Saved PDF to: '{u.BM_PDF()}Burbidge1957_RvMP_29_547.pdf'.\n"""


def test_cli_fetch_keycode_not_in_database(capsys, mock_init_sample, reqs):
    sys.argv = "bibm fetch 1957RvMP...00..000B".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """
Fetching PDF file from Journal website:
Saved PDF to: '1957RvMP...00..000B.pdf'.
(Note that BibTex entry is not in the Bibmanager database)\n"""
    os.remove('1957RvMP...00..000B.pdf')


@pytest.mark.parametrize('mock_prompt_session',
     [['bibcode: 1957RvMP...29..547B'],
      ['key: BurbidgeEtal1957rvmpStellarElementSynthesis']], indirect=True)
def test_cli_fetch_prompt(capsys, mock_init_sample, reqs, mock_prompt_session):
    sys.argv = "bibm fetch".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""Syntax is:  key: KEY_VALUE FILENAME
       or:  bibcode: BIBCODE_VALUE FILENAME
       (FILENAME is optional.  Press 'tab' for autocomplete)

Fetching PDF file from Journal website:
Saved PDF to: '{u.BM_PDF()}Burbidge1957_RvMP_29_547.pdf'.

To open the PDF file, execute:
bibm open BurbidgeEtal1957rvmpStellarElementSynthesis\n"""


@pytest.mark.parametrize('mock_prompt_session',
     [['key: BurbidgeEtal1957rvmpStellarElementSynthesis Burbidge1957.pdf']],
     indirect=True)
def test_cli_fetch_prompt_key_filename(capsys, mock_init_sample, reqs,
        mock_prompt_session):
    sys.argv = "bibm fetch".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""Syntax is:  key: KEY_VALUE FILENAME
       or:  bibcode: BIBCODE_VALUE FILENAME
       (FILENAME is optional.  Press 'tab' for autocomplete)

Fetching PDF file from Journal website:
Saved PDF to: '{u.BM_PDF()}Burbidge1957.pdf'.

To open the PDF file, execute:
bibm open BurbidgeEtal1957rvmpStellarElementSynthesis\n"""


@pytest.mark.parametrize('mock_prompt_session',
     [['bibcode: 1957RvMP...29..547B  Burbidge1957.pdf  extra']], indirect=True)
def test_cli_fetch_prompt_ignore_extra(capsys, mock_init_sample, reqs,
        mock_prompt_session):
    sys.argv = "bibm fetch".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"""Syntax is:  key: KEY_VALUE FILENAME
       or:  bibcode: BIBCODE_VALUE FILENAME
       (FILENAME is optional.  Press 'tab' for autocomplete)

Fetching PDF file from Journal website:
Saved PDF to: '{u.BM_PDF()}Burbidge1957.pdf'.

To open the PDF file, execute:
bibm open BurbidgeEtal1957rvmpStellarElementSynthesis\n"""


@pytest.mark.parametrize('mock_prompt_session',
     [['']], indirect=True)
def test_cli_fetch_prompt_bad_syntax(capsys, mock_init_sample, reqs,
        mock_prompt_session):
    sys.argv = "bibm fetch".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """Syntax is:  key: KEY_VALUE FILENAME
       or:  bibcode: BIBCODE_VALUE FILENAME
       (FILENAME is optional.  Press 'tab' for autocomplete)


Error: Invalid syntax.\n"""


@pytest.mark.parametrize('mock_prompt_session',
     [['key: Burbidge1957']], indirect=True)
def test_cli_fetch_prompt_invalid_bib(capsys, mock_init_sample, reqs,
        mock_prompt_session):
    sys.argv = "bibm fetch".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == """Syntax is:  key: KEY_VALUE FILENAME
       or:  bibcode: BIBCODE_VALUE FILENAME
       (FILENAME is optional.  Press 'tab' for autocomplete)


Error: BibTex entry is not in Bibmanager database.\n"""


@pytest.mark.parametrize('mock_prompt_session',
     [['key: AASteamHendrickson2018aastex62']], indirect=True)
def test_cli_fetch_prompt_invalid_ads(capsys, mock_init_sample, reqs,
        mock_prompt_session):
    sys.argv = "bibm fetch AASteamHendrickson2018aastex62".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "\nError: BibTex entry is not in ADS database.\n"


def test_cli_fetch_pathed_filename(capsys, mock_init_sample, reqs):
    sys.argv = "bibm fetch 1957RvMP...29..547B ./new.pdf".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Fetching PDF file from Journal website:\n"
        "\nError: filename must not have a path\n")


def test_cli_fetch_invalid_name(capsys, mock_init_sample, reqs):
    sys.argv = "bibm fetch 1957RvMP...29..547B pdf_file".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Fetching PDF file from Journal website:\n"
        "\nError: Invalid filename, must have a .pdf extension\n")


@pytest.mark.parametrize('keycode', [
    'Slipher1913lobAndromedaRarialVelocity',
    '1913LowOB...2...56S',
    'Slipher1913.pdf'])
def test_cli_open_keycode(capsys, mock_init_sample, mock_call, mock_open,
        keycode):
    pathlib.Path(f"{u.BM_PDF()}Slipher1913.pdf").touch()
    sys.argv = f"bibm open {keycode}".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_cli_open_keycode_invalid(capsys, mock_init_sample, mock_call):
    pathlib.Path(f"{u.BM_PDF()}Slipher1913.pdf").touch()
    sys.argv = "bibm open bad_keycode".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        '\nError: Input is no key, bibcode, or PDF '
        'of any entry in Bibmanager database\n')


@pytest.mark.parametrize('mock_prompt_session',
     [['key: Slipher1913lobAndromedaRarialVelocity'],
      ['bibcode: 1913LowOB...2...56S'],
      ['pdf: Slipher1913.pdf']], indirect=True)
def test_cli_open_prompt(capsys, mock_init_sample, mock_call, mock_open,
        mock_prompt_session):
    pathlib.Path(f"{u.BM_PDF()}Slipher1913.pdf").touch()
    sys.argv = "bibm open".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Syntax is:  key: KEY_VALUE\n"
        "       or:  bibcode: BIBCODE_VALUE\n"
        "       or:  pdf: PDF_VALUE\n"
        "(Press 'tab' for autocomplete)\n\n")


@pytest.mark.parametrize('mock_prompt_session',
     [['bibcode: ']], indirect=True)
def test_cli_open_prompt_error(capsys, mock_init_sample, mock_call,
        mock_prompt_session):
    pathlib.Path(f"{u.BM_PDF()}Slipher1913.pdf").touch()
    sys.argv = "bibm open".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Syntax is:  key: KEY_VALUE\n"
        "       or:  bibcode: BIBCODE_VALUE\n"
        "       or:  pdf: PDF_VALUE\n"
        "(Press 'tab' for autocomplete)\n\n\n"
        "Error: Invalid syntax.\n")


@pytest.mark.parametrize('mock_input', [['yes']], indirect=True)
def test_cli_open_fetch(capsys, mock_init_sample, mock_call, reqs, mock_input):
    sys.argv = "bibm open 1957RvMP...29..547B".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "\nError: Entry does not have a PDF in the database\n"
        "Fetch from ADS?\n"
        "[]yes [n]o\n\n"
        "Fetching PDF file from Journal website:\n"
        f"Saved PDF to: '{u.BM_PDF()}Burbidge1957_RvMP_29_547.pdf'.\n")


@pytest.mark.parametrize('keycode',
    ['1957RvMP...29..547B', 'BurbidgeEtal1957rvmpStellarElementSynthesis'])
def test_cli_pdf_set_keycode(capsys, mock_init_sample, mock_call, keycode):
    sys.argv = f"bibm pdf {keycode} file.pdf".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"Saved PDF to: '{u.BM_PDF()}file.pdf'.\n"
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf == 'file.pdf'
    assert 'file.pdf' in os.listdir(u.BM_PDF())


def test_cli_pdf_set_renamed(capsys, mock_init_sample, mock_call):
    sys.argv = "bibm pdf 1957RvMP...29..547B file.pdf new.pdf".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == f"Saved PDF to: '{u.BM_PDF()}new.pdf'.\n"
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf == 'new.pdf'
    assert 'new.pdf' in os.listdir(u.BM_PDF())


def test_cli_pdf_set_guessed(capsys, mock_init_sample, mock_call):
    sys.argv = "bibm pdf 1957RvMP...29..547B file.pdf guess".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        f"Saved PDF to: '{u.BM_PDF()}Burbidge1957_RvMP_29_547.pdf'.\n"
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf == 'Burbidge1957_RvMP_29_547.pdf'
    assert 'Burbidge1957_RvMP_29_547.pdf' in os.listdir(u.BM_PDF())


@pytest.mark.parametrize('mock_prompt_session',
    [['key: BurbidgeEtal1957rvmpStellarElementSynthesis file.pdf']],
    indirect=True)
def test_cli_pdf_set_prompt_key(capsys, mock_init_sample, mock_call,
        mock_prompt_session):
    sys.argv = "bibm pdf".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Syntax is:  key: KEY_VALUE PDF_FILE FILENAME\n"
        "       or:  bibcode: BIBCODE_VALUE PDF_FILE FILENAME\n"
        "(output FILENAME is optional, set it to guess for automated naming)\n"
        f"\nSaved PDF to: '{u.BM_PDF()}file.pdf'.\n")
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf == 'file.pdf'
    assert 'file.pdf' in os.listdir(u.BM_PDF())


@pytest.mark.parametrize('mock_prompt_session',
    [['bibcode: 1957RvMP...29..547B file.pdf']], indirect=True)
def test_cli_pdf_set_prompt_bibcode(capsys, mock_init_sample, mock_call,
        mock_prompt_session):
    sys.argv = "bibm pdf".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Syntax is:  key: KEY_VALUE PDF_FILE FILENAME\n"
        "       or:  bibcode: BIBCODE_VALUE PDF_FILE FILENAME\n"
        "(output FILENAME is optional, set it to guess for automated naming)\n"
        f"\nSaved PDF to: '{u.BM_PDF()}file.pdf'.\n")
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf == 'file.pdf'
    assert 'file.pdf' in os.listdir(u.BM_PDF())


@pytest.mark.parametrize('mock_prompt_session',
    [['bibcode: 1957RvMP...29..547B file.pdf new.pdf']], indirect=True)
def test_cli_pdf_set_prompt_rename(capsys, mock_init_sample, mock_call,
        mock_prompt_session):
    sys.argv = "bibm pdf".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Syntax is:  key: KEY_VALUE PDF_FILE FILENAME\n"
        "       or:  bibcode: BIBCODE_VALUE PDF_FILE FILENAME\n"
        "(output FILENAME is optional, set it to guess for automated naming)\n"
        f"\nSaved PDF to: '{u.BM_PDF()}new.pdf'.\n")
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf == 'new.pdf'
    assert 'new.pdf' in os.listdir(u.BM_PDF())


@pytest.mark.parametrize('mock_prompt_session',
    [['bibcode: 1957RvMP...29..547B file.pdf guess']], indirect=True)
def test_cli_pdf_set_prompt_guess(capsys, mock_init_sample, mock_call,
        mock_prompt_session):
    sys.argv = "bibm pdf".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Syntax is:  key: KEY_VALUE PDF_FILE FILENAME\n"
        "       or:  bibcode: BIBCODE_VALUE PDF_FILE FILENAME\n"
        "(output FILENAME is optional, set it to guess for automated naming)\n"
        f"\nSaved PDF to: '{u.BM_PDF()}Burbidge1957_RvMP_29_547.pdf'.\n")
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf == 'Burbidge1957_RvMP_29_547.pdf'
    assert 'Burbidge1957_RvMP_29_547.pdf' in os.listdir(u.BM_PDF())


def test_cli_pdf_set_missing_pdf(capsys, mock_init_sample):
    sys.argv = "bibm pdf 1957RvMP...29..547B".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "\nError: Path to PDF file is missing.\n"
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf is None
    os.remove('file.pdf')


def test_cli_pdf_set_missing_bib(capsys, mock_init_sample):
    sys.argv = "bibm pdf 1957RvMP...00..000X file.pdf".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: BibTex entry is not in Bibmanager database.\n"
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf is None
    os.remove('file.pdf')


def test_cli_pdf_set_missing_pdf_file(capsys, mock_init_sample):
    sys.argv = "bibm pdf 1957RvMP...29..547B file.pdf".split()
    with u.ignored(OSError):
        os.remove('file.pdf')
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "\nError: input PDF file does not exist.\n"
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf is None


def test_cli_pdf_set_pathed_filename(capsys, mock_init_sample):
    sys.argv = "bibm pdf 1957RvMP...29..547B file.pdf ./new.pdf".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == "\nError: filename must not have a path\n"
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf is None
    os.remove('file.pdf')


def test_cli_pdf_set_invalid_name(capsys, mock_init_sample):
    sys.argv = "bibm pdf 1957RvMP...29..547B file.pdf pdf_file".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == \
        "\nError: Invalid filename, must have a .pdf extension\n"
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf is None
    os.remove('file.pdf')


@pytest.mark.parametrize('mock_prompt_session',
    [['bibcode: 1957RvMP...29..547B']], indirect=True)
def test_cli_pdf_set_prompt_missing_pdf(capsys, mock_init_sample,
        mock_prompt_session):
    sys.argv = "bibm pdf".split()
    pathlib.Path("file.pdf").touch()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Syntax is:  key: KEY_VALUE PDF_FILE FILENAME\n"
        "       or:  bibcode: BIBCODE_VALUE PDF_FILE FILENAME\n"
        "(output FILENAME is optional, set it to guess for automated naming)\n"
        "\n\nError: Path to PDF file is missing.\n")
    bib = bm.find(bibcode='1957RvMP...29..547B')
    assert bib.pdf is None
    os.remove('file.pdf')


@pytest.mark.parametrize('mock_prompt_session',
    [['author:"^slipher"']], indirect=True)
def test_cli_older_pickle(capsys, mock_init_sample, mock_prompt_session):
    # Mock pickle DB file with older version than bibmanager:
    with open(u.BM_DATABASE(), 'wb') as handle:
        pickle.dump([], handle, protocol=4)

    # Simulate user input:
    sys.argv = "bibm search".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Updating database file from version 0.0.0 to version "
        f"{bibmanager.__version__}.\n"
        + expected_slipher)


def test_cli_future_pickle(capsys, mock_init_sample):
    # Mock pickle DB file with later version than bibmanager:
    future_version = '2.0.0'
    with open(u.BM_DATABASE(), 'wb') as handle:
        pickle.dump([], handle, protocol=4)
        pickle.dump(future_version, handle, protocol=4)

    # Simulate user input:
    sys.argv = "bibm reset".split()
    cli.main()
    captured = capsys.readouterr()
    assert captured.out == (
        f"Bibmanager version ({bibmanager.__version__}) is older than "
        f"saved database.  Please update to a version >= {future_version}.\n")

