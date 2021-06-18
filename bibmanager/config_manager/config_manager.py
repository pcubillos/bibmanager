# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = [
    'help',
    'display',
    'get',
    'set',
    'update_keys',
    ]

import os
import shutil
import configparser
import textwrap
import pathlib
from packaging import version

from pygments.styles import STYLE_MAP

from .. import bib_manager as bm
from .. import utils as u
from ..__init__ import __version__


styles = textwrap.fill(
    ", ".join(style for style in iter(STYLE_MAP)),
    width=79,
    initial_indent="  ",
    subsequent_indent="  ")


def help(key):
    """
    Display help information.

    Parameters
    ----------
    key: String
        A bibmanager config parameter.
    """
    style_text = (
        f"\nThe '{key}' parameter sets the color-syntax style of displayed "
        "BibTeX entries.\nThe default style is 'autumn'.  Available options "
        f"are:\n{styles}\nSee http://pygments.org/demo/6780986/ for a demo "
        f"of the style options.\n\nThe current style is '{get(key)}'.")

    editor_text = (
        f"\nThe '{key}' parameter sets the text editor to use when "
        "editing the\nbibmanager manually (i.e., a call to: bibm edit).  By "
        "default, bibmanager\nuses the OS-default text editor.\n\n"
        "Typical text editors are: emacs, vim, gedit.\n"
        "To set the OS-default editor, set text_editor to 'default'.\n"
        "Note that aliases defined in the .bash are not accessible.\n\n"
        f"The current text editor is '{get(key)}'.")

    paper_text = (
        f"\nThe '{key}' parameter sets the default paper format for latex "
        "compilation outputs\n(not for pdflatex, which is automatic).  "
        "Typical options are 'letter'\n(e.g., for ApJ articles) or 'A4' "
        f"(e.g., for A&A).\n\nThe current paper format is: '{get(key)}'.")

    token_text = (
        f"\nThe '{key}' parameter sets the ADS token required for ADS requests."
        "\nTo obtain a token, follow the steps described here:"
        "\n  https://github.com/adsabs/adsabs-dev-api#access"
        f"\n\nThe current ADS token is '{get(key)}'")

    display_text = (
        f"\nThe '{key}' parameter sets the number of entries to show at "
        "a time,\nfor an ADS search query.\n\n"
        f"The current number of entries to display is {get(key)}.")

    home_text = (
        f"\nThe '{key}' parameter sets the home directory for the Bibmanager "
        f"database.\n\nThe current directory is '{get(key)}'.")

    if key == 'style':
        print(style_text)
    elif key == 'text_editor':
        print(editor_text)
    elif key == 'paper':
        print(paper_text)
    elif key == 'ads_token':
        print(token_text)
    elif key == 'ads_display':
        print(display_text)
    elif key == 'home':
        print(home_text)
    else:
        # Call get() to trigger exception:
        get(key)


def display(key=None):
    """
    Display the value(s) of the bibmanager config file on the prompt.

    Parameters
    ----------
    key: String
        bibmanager config parameter to display.  Leave as None to display
        the values from all parameters.

    Examples
    --------
    >>> import bibmanager.config_manager as cm
    >>> # Show all parameters and values:
    >>> cm.display()
    bibmanager configuration file:
    PARAMETER    VALUE
    -----------  -----
    style        autumn
    text_editor  default
    paper        letter
    ads_token    None
    ads_display  20
    home         /home/user/.bibmanager/

    >>> # Show an specific parameter:
    >>> cm.display('text_editor')
    text_editor: default
    """
    if key is not None:
        print(f"{key}: {get(key)}")
    else:
        config = configparser.ConfigParser()
        config.read(u.HOME + 'config')
        print("\nbibmanager configuration file:"
              "\nPARAMETER    VALUE"
              "\n-----------  -----")
        for key, value in config['BIBMANAGER'].items():
            print(f"{key:11}  {value}")


def get(key):
    """
    Get the value of a parameter in the bibmanager config file.

    Parameters
    ----------
    key: String
        The requested parameter name.

    Returns
    -------
    value: String
        Value of the requested parameter.

    Examples
    --------
    >>> import bibmanager.config_manager as cm
    >>> cm.get('paper')
    'letter'
    >>> cm.get('style')
    'autumn'
    """
    config = configparser.ConfigParser()
    config.read(u.HOME + 'config')

    if not config.has_option('BIBMANAGER', key):
        rconfig = configparser.ConfigParser()
        rconfig.read(u.ROOT+'config')
        raise ValueError(
            f"'{key}' is not a valid bibmanager config parameter.\n"
            f"The available parameters are:\n  {rconfig.options('BIBMANAGER')}")
    return config.get('BIBMANAGER', key)


def set(key, value):
    """
    Set the value of a bibmanager config parameter.

    Parameters
    ----------
    key: String
        bibmanager config parameter to set.
    value: String
        Value to set for input parameter.

    Examples
    --------
    >>> import bibmanager.config_manager as cm
    >>> # Update text editor:
    >>> cm.set('text_editor', 'vim')
    text_editor updated to: vim.

    >>> # Invalid bibmanager parameter:
    >>> cm.set('styles', 'arduino')
    ValueError: 'styles' is not a valid bibmanager config parameter.
    The available parameters are:
      ['style', 'text_editor', 'paper', 'ads_token', 'ads_display', 'home']

    >>> # Attempt to set an invalid style:
    >>> cm.set('style', 'fake_style')
    ValueError: 'fake_style' is not a valid style option.  Available options are:
      default, emacs, friendly, colorful, autumn, murphy, manni, monokai, perldoc,
      pastie, borland, trac, native, fruity, bw, vim, vs, tango, rrt, xcode, igor,
      paraiso-light, paraiso-dark, lovelace, algol, algol_nu, arduino,
      rainbow_dash, abap

    >>> # Attempt to set an invalid command for text_editor:
    >>> cm.set('text_editor', 'my_own_editor')
    ValueError: 'my_own_editor' is not a valid text editor.

    >>> # Beware, one can still set a valid command that doesn't edit text:
    >>> cm.set('text_editor', 'less')
    text_editor updated to: less.
    """
    config = configparser.ConfigParser()
    config.read(u.HOME + 'config')

    # Use get on invalid key to raise an error:
    if not config.has_option('BIBMANAGER', key):
        get(key)

    # Check for exceptions:
    if key == 'style' and value not in STYLE_MAP.keys():
        raise ValueError(
            f"'{value}' is not a valid style option.  "
            f"Available options are:\n{styles}")

    # The code identifies invalid commands, but cannot assure that a
    # command actually applies to a text file.
    if key == 'text_editor' \
            and value != 'default' \
            and shutil.which(value) is None:
        raise ValueError(f"'{value}' is not a valid text editor.")

    if key == 'ads_display' and (not value.isnumeric() or value=='0'):
        raise ValueError(f"The {key} value must be a positive integer.")

    if key == 'home':
        value = os.path.abspath(os.path.expanduser(value)) + '/'
        new_home = pathlib.Path(value)
        if not new_home.parent.is_dir():
            raise ValueError(
                f"The {key} value must have an existing parent folder")
        if new_home.suffix != '':
            raise ValueError(f"The {key} value cannot have a file extension")

        # Make sure folders will exist:
        new_home.mkdir(exist_ok=True)
        with pathlib.Path(f'{value}pdf') as pdf_dir:
            pdf_dir.mkdir(exist_ok=True)

        # Files to move (config has to stay at u.HOME):
        bm_files = [
            u.BM_DATABASE(),
            u.BM_BIBFILE(),
            u.BM_CACHE(),
            u.BM_HISTORY_SEARCH(),
            u.BM_HISTORY_ADS(),
            u.BM_HISTORY_PDF(),
            ]
        pdf_files = [
            f'{u.BM_PDF()}{bib.pdf}' for bib in bm.load()
            if bib.pdf is not None
            if os.path.isfile(f'{u.BM_PDF()}{bib.pdf}')]

        # Merge if there is already a Bibmanager database in new_home:
        new_database = f'{new_home}/{os.path.basename(u.BM_DATABASE())}'
        if os.path.isfile(new_database):
            pickle_ver = bm.get_version(new_database)
            if version.parse(__version__) < version.parse(pickle_ver):
                print(f"Bibmanager version ({__version__}) is older than saved "
                      f"database.  Please update to a version >= {pickle_ver}.")
                return
            new_biblio = f'{new_home}/{os.path.basename(u.BM_BIBFILE())}'
            bm.merge(new=bm.read_file(new_biblio), take='new')

        # Move (overwrite) database files:
        bm_files = [bm_file for bm_file in bm_files if os.path.isfile(bm_file)]
        new_files = os.listdir(new_home)
        for bm_file in bm_files:
            if os.path.basename(bm_file) in new_files:
                os.remove(f'{new_home}/{os.path.basename(bm_file)}')
            shutil.move(bm_file, str(new_home))

        # Move (overwrite) PDF files:
        new_pdfs = os.listdir(f'{new_home}/pdf')
        for pdf_file in pdf_files:
            if os.path.basename(pdf_file) in new_pdfs:
                os.remove(f'{new_home}/pdf/{os.path.basename(pdf_file)}')
            shutil.move(pdf_file, f'{new_home}/pdf/')

    # Set value if there were no exceptions raised:
    config.set('BIBMANAGER', key, value)
    with open(u.HOME+'config', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    print(f'{key} updated to: {value}.')


def update_keys():
    """Update config in HOME with keys from ROOT, without overwriting values."""
    config_root = configparser.ConfigParser()
    config_root.read(u.ROOT+'config')
    config_root.set('BIBMANAGER', 'home', u.HOME)
    # Won't complain if HOME+'config' does not exist (keep ROOT values):
    config_root.read(u.HOME+'config')
    with open(u.HOME+'config', 'w', encoding='utf-8') as configfile:
        config_root.write(configfile)
