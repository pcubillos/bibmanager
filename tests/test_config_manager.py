import filecmp
import shutil
import textwrap
import configparser
import pytest

from pygments.styles import STYLE_MAP

import bibmanager.utils as u
import bibmanager.config_manager as cm


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
for an ADS search querry.

The current number of entries to display is 20.\n"""


def test_help_raise(mock_init):
    #config = configparser.ConfigParser()
    #config.read(u.HOME+'config')
    #errorlog = ("'invalid_param' is not a valid bibmanager config parameter.\n"
    #            "The available parameters are:\n"
    #           f"  {config.options('BIBMANAGER')}")

    # TBD: match only matches until the linebreak character.
    with pytest.raises(ValueError, 
           match="'invalid_param' is not a valid bibmanager config parameter."):
        cm.help("invalid_param")


def test_display_all(capsys, mock_init):
    cm.display()
    captured = capsys.readouterr()
    assert captured.out == ("\nbibmanager configuration file:\n"
                            "PARAMETER    VALUE\n"
                            "-----------  -----\n"
                            "style        autumn\n"
                            "text_editor  default\n"
                            "paper        letter\n"
                            "ads_token    None\n"
                            "ads_display  20\n")


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


def test_display_each(mock_init):
    with pytest.raises(ValueError,
           match="'invalid_param' is not a valid bibmanager config parameter."):
        cm.display("invalid_param")


def test_update_default(mock_init):
    cm.update_keys()
    assert filecmp.cmp(u.HOME+"config", u.ROOT+"config")


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
