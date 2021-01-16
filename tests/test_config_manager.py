# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import filecmp
import shutil
import textwrap
import pathlib
import pytest

from pygments.styles import STYLE_MAP

import bibmanager.utils as u
import bibmanager.bib_manager as bm
import bibmanager.config_manager as cm
import bibmanager.ads_manager as am


def test_help_style(capsys, mock_init):
    styles = textwrap.fill(", ".join(style for style in iter(STYLE_MAP)),
                 width=79, initial_indent="  ", subsequent_indent="  ")
    cm.help("style")
    captured = capsys.readouterr()
    assert captured.out == f"""
The 'style' parameter sets the color-syntax style of displayed BibTeX entries.
The default style is 'autumn'.  Available options are:
{styles}
See http://pygments.org/demo/6780986/ for a demo of the style options.

The current style is 'autumn'.\n"""


def test_help_editor(capsys, mock_init):
    cm.help("text_editor")
    captured = capsys.readouterr()
    assert captured.out == """
The 'text_editor' parameter sets the text editor to use when editing the
bibmanager manually (i.e., a call to: bibm edit).  By default, bibmanager
uses the OS-default text editor.

Typical text editors are: emacs, vim, gedit.
To set the OS-default editor, set text_editor to 'default'.
Note that aliases defined in the .bash are not accessible.

The current text editor is 'default'.\n"""


def test_help_paper(capsys, mock_init):
    cm.help("paper")
    captured = capsys.readouterr()
    assert captured.out == """
The 'paper' parameter sets the default paper format for latex compilation outputs
(not for pdflatex, which is automatic).  Typical options are 'letter'
(e.g., for ApJ articles) or 'A4' (e.g., for A&A).

The current paper format is: 'letter'.\n"""


def test_help_ads_token(capsys, mock_init):
    cm.help("ads_token")
    captured = capsys.readouterr()
    assert captured.out == """
The 'ads_token' parameter sets the ADS token required for ADS requests.
To obtain a token, follow the steps described here:
  https://github.com/adsabs/adsabs-dev-api#access

The current ADS token is 'None'\n"""


def test_help_ads_display(capsys, mock_init):
    cm.help("ads_display")
    captured = capsys.readouterr()
    assert captured.out == """
The 'ads_display' parameter sets the number of entries to show at a time,
for an ADS search query.

The current number of entries to display is 20.\n"""


def test_help_home(capsys, mock_init):
    cm.help("home")
    captured = capsys.readouterr()
    assert captured.out == f"""
The 'home' parameter sets the home directory for the Bibmanager database.

The current directory is '{u.HOME}'.\n"""


def test_help_raise(mock_init):
    # Note that match only matches until the linebreak character.
    with pytest.raises(ValueError,
           match="'invalid_param' is not a valid bibmanager config parameter."):
        cm.help("invalid_param")


def test_display_all(capsys, mock_init):
    cm.display()
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


def test_display_each(capsys, mock_init):
    cm.display("style")
    captured = capsys.readouterr()
    assert captured.out == "style: autumn\n"
    cm.display("text_editor")
    captured = capsys.readouterr()
    assert captured.out == "text_editor: default\n"
    cm.display("paper")
    captured = capsys.readouterr()
    assert captured.out == "paper: letter\n"
    cm.display("ads_token")
    captured = capsys.readouterr()
    assert captured.out == "ads_token: None\n"
    cm.display("ads_display")
    captured = capsys.readouterr()
    assert captured.out == "ads_display: 20\n"


def test_display_each_raises(mock_init):
    with pytest.raises(ValueError,
           match="'invalid_param' is not a valid bibmanager config parameter."):
        cm.display("invalid_param")


def test_update_default(mock_init):
    cm.update_keys()
    with open(u.HOME+"config", 'r') as f:
        home = f.read()
    with open(u.ROOT+"config", 'r') as f:
        root = f.read()
    assert home == root.replace('HOME/', u.HOME)


def test_get(mock_init):
    assert cm.get("style")       == "autumn"
    assert cm.get("text_editor") == "default"
    assert cm.get("paper")       == "letter"
    assert cm.get("ads_token")   == "None"
    assert cm.get("ads_display") == "20"


def test_get_raise(mock_init):
    with pytest.raises(ValueError,
           match="'invalid_param' is not a valid bibmanager config parameter."):
        cm.get("invalid_param")


def test_set_style(mock_init):
    cm.set("style", "fruity")
    assert cm.get("style") == "fruity"


def test_set_style_raises(mock_init):
    # Value must be a valid pygments style:
    with pytest.raises(ValueError, match="'invalid_pygment' is not a valid style option.  Available options are:"):
        cm.set("style", "invalid_pygment")


def test_set_editor(mock_init):
    # This is the only way to make sure vi is valid I can think of:
    if shutil.which("vi") is not None:
        cm.set("text_editor", "vi")
        assert cm.get("text_editor") == "vi"
    else:
        pass


def test_set_editor_default(mock_init):
    cm.set("text_editor", "default")
    assert cm.get("text_editor") == "default"


def test_set_editor_raises(mock_init):
    # Value must be a valid pygments style:
    with pytest.raises(ValueError,
             match="'invalid_editor' is not a valid text editor."):
        cm.set("text_editor", "invalid_editor")


def test_set_paper(mock_init):
    cm.set("paper", "A4")
    assert cm.get("paper") == "A4"


def test_set_ads_token(mock_init):
    cm.set("ads_token", "abc12345")
    assert cm.get("ads_token") == "abc12345"


def test_set_ads_display(mock_init):
    cm.set("ads_display", "50")
    assert cm.get("ads_display") == "50"


def test_set_ads_display_raises(mock_init):
    with pytest.raises(ValueError,
            match="The ads_display value must be a positive integer."):
        cm.set("ads_display", "fifty")


def test_set_home_success(capsys, tmp_path, mock_init_sample):
    new_home = f'{tmp_path}/bm'
    cm.set('home', new_home)
    assert cm.get('home') == new_home + '/'
    # 'constants' now point to new home:
    assert u.BM_DATABASE() == f'{new_home}/bm_database.pickle'
    assert u.BM_BIBFILE() == f'{new_home}/bm_bibliography.bib'
    assert u.BM_TMP_BIB() == f'{new_home}/tmp_bibliography.bib'
    assert u.BM_CACHE() == f'{new_home}/cached_ads_query.pickle'
    assert u.BM_HISTORY_SEARCH() == f'{new_home}/history_search'
    assert u.BM_HISTORY_ADS() == f'{new_home}/history_ads_search'
    assert u.BM_PDF() == f'{new_home}/pdf/'
    captured = capsys.readouterr()
    assert captured.out == f'home updated to: {new_home}/.\n'
    # These files/folders stay:
    assert set(os.listdir(u.HOME)) == set(["config", "examples", "pdf"])
    # These files have been moved/created:
    assert set(os.listdir(str(new_home))) == \
        set(['pdf', 'bm_bibliography.bib', 'bm_database.pickle'])


def test_set_home_pdf_success(tmp_path, mock_init_sample):
    new_home = f'{tmp_path}/bm'
    old_pdf_home = u.BM_PDF()
    pathlib.Path(f"{u.BM_PDF()}Rubin1980.pdf").touch()
    pathlib.Path(f"{u.BM_PDF()}Slipher1913.pdf").touch()
    cm.set('home', new_home)
    # Not registered in database, not moved:
    assert 'Rubin1980.pdf' in os.listdir(f'{old_pdf_home}')
    # Moved:
    assert 'Slipher1913.pdf' in os.listdir(f'{new_home}/pdf/')
    assert 'Slipher1913.pdf' in os.listdir(u.BM_PDF())


def test_set_home_overwrite(tmp_path, mock_init_sample):
    new_home = f'{tmp_path}/bm'
    pathlib.Path(f"{u.BM_PDF()}Slipher1913.pdf").touch()
    os.mkdir(f'{new_home}')
    os.mkdir(f'{new_home}/pdf')
    pathlib.Path(f"{u.BM_HISTORY_SEARCH()}").touch()
    pathlib.Path(f"{new_home}/history_search").touch()
    pathlib.Path(f"{new_home}/pdf/Slipher1913.pdf").touch()
    cm.set('home', new_home)
    # No errors <=> pass


def test_set_home_merge(tmp_path, bibs, mock_init):
    new_home = f'{tmp_path}/bm'
    os.mkdir(f'{new_home}')
    bib1, bib2 = bibs["beaulieu_apj"], bibs["stodden"]
    bib1.pdf, bib2.pdf = 'file1.pdf', 'file2.pdf'
    bm.save([bib1])
    shutil.copy(u.BM_DATABASE(), f'{new_home}/bm_database.pickle')
    bm.export([bib1], f'{new_home}/bm_bibliography.bib', meta=True)
    bm.export([bib2], f'{new_home}/other.bib', meta=True)
    bm.init(f'{new_home}/other.bib')
    cm.set('home', new_home)
    # Check DBs are merged:
    bibs = bm.load()
    assert len(bibs) == 2
    assert bibs[0].content == bib1.content
    assert bibs[1].content == bib2.content
    # Check both meta exist:
    assert bibs[0].pdf == 'file1.pdf'
    assert bibs[1].pdf == 'file2.pdf'


def test_set_home_none_success(tmp_path, mock_init):
    new_home = f'{tmp_path}/bm'
    cm.set('home', new_home)
    # These files/folders stay:
    assert set(os.listdir(u.HOME)) == set(["config", "examples", "pdf"])
    # These files have been moved/created:
    assert os.listdir(str(new_home)) == ['pdf']


def test_set_home_and_edit(tmp_path, mock_init, bibs, reqs):
    new_home = f'{tmp_path}/bm'
    cm.set('home', new_home)
    assert cm.get('home') == new_home + '/'
    # Test merge:
    bm.merge(new=[bibs["beaulieu_apj"]], take='new')
    # Test search:
    matches = bm.search(authors="beaulieu")
    assert len(matches) == 1
    assert 'BeaulieuEtal2011apjGJ436bMethane' in matches[0].key
    # Test ADS add:
    am.add_bibtex(['1925PhDT.........1P'], ['Payne1925phdStellarAtmospheres'])
    # Test load:
    current_bibs = bm.load()
    assert len(current_bibs) == 2
    assert 'Payne1925phdStellarAtmospheres' in current_bibs[1].key
    # These files/folders stay:
    assert set(os.listdir(u.HOME)) == set(["config", "examples", "pdf"])
    # These files have been moved/created:
    assert set(os.listdir(str(new_home))) == \
        set(['pdf', 'bm_bibliography.bib', 'bm_database.pickle'])


def test_set_home_no_parent(mock_init_sample):
    with pytest.raises(ValueError,
           match="The home value must have an existing parent folder"):
        cm.set("home", "fake_parent/some_dir")


def test_set_home_file_extension(mock_init_sample):
    with pytest.raises(ValueError,
           match="The home value cannot have a file extension"):
        cm.set("home", "./new.home")


def test_set_raises(mock_init):
    with pytest.raises(ValueError,
           match="'invalid_param' is not a valid bibmanager config parameter."):
        cm.set("invalid_param", "value")


def test_update_edited(mock_init):
    # Simulate older config with a missing parameter, but not default values:
    with open(u.HOME+"config", "w") as f:
        f.writelines("[BIBMANAGER]\n"
                     "style = autumn\n"
                     "text_editor = vi\n"
                     "paper = letter\n")
    cm.update_keys()
    assert not filecmp.cmp(u.HOME+"config", u.ROOT+"config")
    assert cm.get("style")       == "autumn"
    assert cm.get("text_editor") == "vi"
    assert cm.get("paper")       == "letter"
    assert cm.get("ads_token")   == "None"
    assert cm.get("ads_display") == "20"
