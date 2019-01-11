# Copyright (c) 2018-2019 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = ['help', 'display', 'update_keys', 'get', 'set']

import os
import shutil
import configparser
import textwrap
from pygments.styles import STYLE_MAP

from utils import ROOT, HOME


styles = textwrap.fill(", ".join(style for style in iter(STYLE_MAP)),
                       width=79, initial_indent="  ", subsequent_indent="  ")


def help(key):
  """
  Display help information.

  Parameters
  ----------
  key: String
     A bibmanager config parameter.
  """
  if key == 'style':
      print(f"\nThe '{key}' parameter sets the color-syntax style of displayed "
             "BibTeX entries.\nThe default style is 'autumn'.  "
            f"Available options are:\n{styles}\n"
             "See http://pygments.org/demo/6780986/ for a demo of the style "
             "options.\n\n"
            f"The current style is '{get(key)}'.")

  elif key == 'text_editor':
      print(f"\nThe '{key}' parameter sets the text editor to use when editing "
             "the\nbibmanager manually (i.e., a call to: bibm edit).  By "
             "default, bibmanager\nuses the OS-default text editor.\n\n"
             "Typical text editors are: emacs, vim, gedit.\n"
             "To set the OS-default editor, set text_editor to 'default'.\n"
             "Note that aliases defined in the .bash are not accessible.\n\n"
            f"The current text editor is '{get(key)}'.")

  elif key == 'paper':
      print(f"\nThe '{key}' parameter sets the default paper format for latex "
             "compilation outputs\n(not for pdflatex, which is automatic).  "
             "Typical options are 'letter'\n(e.g., for ApJ articles) or 'A4' "
            f"(e.g., for A&A).\n\nThe current paper format is: '{get(key)}'.")

  elif key == 'ads_token':
      print(f"\nThe '{key}' parameter sets the ADS token required for ADS "
             "requests.\nTo obtain a token, follow the steps described here:\n"
             "  https://github.com/adsabs/adsabs-dev-api#access\n\n"
            f"The current ADS token is '{get(key)}'")

  elif key == 'ads_display':
      print(f"\nThe '{key}' parameter sets the number of entries to show at "
             "a time,\nfor an ADS search querry.\n\n"
            f"The current number of entries to display is {get(key)}.")
  else:
      # Call get() to trigger exception:
      get(key)


def display(key=None):
  """
  Display the value(s) of the bibmanager config file on the prompt.

  Parameters
  ----------
  key: String
     bibmanager config parameter to display.  Leave as None to display the
     values from all parameters.

  Examples
  --------
  >>> import config_manager as cm
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

  >>> # Show an specific parameter:
  >>> cm.display('text_editor')
  text_editor: default
  """
  if key is not None:
      print(f"{key}: {get(key)}")
  else:
      config = configparser.ConfigParser()
      config.read(HOME+'config')
      print("\nbibmanager configuration file:"
            "\nPARAMETER    VALUE"
            "\n-----------  -----")
      for key, value in config['BIBMANAGER'].items():
          print(f"{key:11}  {value}")


def update_keys():
  """Update config in HOME with keys from ROOT, without overwriting values."""
  config_root = configparser.ConfigParser()
  config_root.read(ROOT+'config')
  # Wont complain if HOME+'config' does not exist (keep ROOT values):
  config_root.read(HOME+'config')
  with open(HOME+'config', 'w') as configfile:
      config_root.write(configfile)


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
  >>> import config_manager as cm
  >>> cm.get('paper')
  'letter'
  >>> cm.get('style')
  'autumn'
  """
  config = configparser.ConfigParser()
  config.read(HOME+'config')

  if not config.has_option('BIBMANAGER', key):
      raise ValueError(f"'{key}' is not a valid bibmanager config parameter. "
          f"The available\nparameters are:  {config.options('BIBMANAGER')}")
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
  >>> import config_manager as cm
  >>> # Update text editor:
  >>> cm.set('text_editor', 'vim')
  text_editor updated to: vim.

  >>> # Invalid bibmanager parameter:
  >>> cm.set('styles', 'arduino')
  ValueError: 'styles' is not a valid bibmanager config parameter.
  The available parameters are: ['style', 'text_editor', 'paper', 'ads_token']

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
  config.read(HOME+'config')
  if not config.has_option('BIBMANAGER', key):
      raise ValueError(f"'{key}' is not a valid bibmanager config parameter. "
          f"The available\nparameters are:  {config.options('BIBMANAGER')}")

  # Check for exceptions:
  if key == 'style' and value not in STYLE_MAP.keys():
      raise ValueError(f"'{value}' is not a valid style option.  "
                       f"Available options are:\n{styles}")

  # The code identifies invalid commands, but cannot assure that a
  # command actually applies to a text file.
  if key == 'text_editor' and value!='default' and shutil.which(value) is None:
      raise ValueError(f"'{value}' is not a valid text editor.")

  if key == 'ads_display' and (not value.isnumeric() or value=='0'):
      raise ValueError(f"The {key} value must be a positive integer.")

  # Set value if there were no exceptions raised:
  config.set('BIBMANAGER', key, value)
  with open(HOME+'config', 'w') as configfile:
      config.write(configfile)
  print(f'{key} updated to: {value}.')
