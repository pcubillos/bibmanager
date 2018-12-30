# Copyright (c) 2018 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = ['reset']

import os
import shutil
import configparser
import textwrap
from pygments.styles import STYLE_MAP


# Set these as a unique constant in the pakage (in __init__?)
ROOT = os.path.dirname(os.path.realpath(__file__)) + '/'
HOME = os.path.expanduser("~") + "/.bibmanager/"

styles = textwrap.fill(", ".join(style for style in iter(STYLE_MAP)),
                       width=79, initial_indent="  ", subsequent_indent="  ")

def reset():
  """
  Reset the bibmanager configuration file.

  Simply, copy the default config file into bm.HOME/config,
  overwriting any pre-existing content.
  """
  shutil.copy(ROOT+'config', HOME+'config')


def set_key(key, value=None):
  """
  if value is None, trigger help.
  """
  config = configparser.ConfigParser()
  config.read(bm_config)
  if not config.has_option('BIBMANAGER', key):
      raise ValueError("'{:s}' is not a valid bibmanager config key."
                       "\nThe available keys are: {}".
                       format(key, config.options('BIBMANAGER')))

  # Set value:
  if value is not None:
      config.set('BIBMANAGER', key, value)
      if key == 'style' and value not in STYLE_MAP.keys():
          raise ValueError("'{:s}' is not a valid style option.  "
              "Available options are:\n{:s}".format(value, styles))

      with open(HOME+'config', 'w') as config:
          config.write(config)
      return

  # Display helps (value is None):
  if key == 'style':
      print("The 'style' key sets the color-syntax style of displayed BibTeX "
            "entries.\nDefault style is 'autumn'.  Current style is '{:s}'. "
            "\n\nAvailable options are:\n{:s}\n"
            "See http://pygments.org/demo/6780986/ for a demo of the style "
            "options.".format(config.get('BIBMANAGER',key), styles))

  elif key == 'text_editor':
      pass

  elif key == 'paper':
      print("The 'paper' key sets the default paper format for latex "
            "compilation outputs\n(not for pdflatex, which is automatic).  "
            "Typical options are 'letter'\n(e.g., for ApJ articles), or "
            "'A4' (e.g., for A&A).\n\nCurrent value is: '{:s}'.".
            format(config.get('BIBMANAGER',key)))

  elif key == 'adstoken':
      pass


def get_key(key=None):
  """
  Display the value(s) of the bibmanager config file on the prompt.

  Parameters
  ----------
  key: String
     bibmanager config key to display.  Leave as None to display the
     values from all keys.
  """
  config = configparser.ConfigParser()
  config.read(HOME+'config')

  if key is not None:
      if not config.has_option('BIBMANAGER', key):
          raise ValueError("No key '{:s}' in bibmanager config file."
                           "\nThe available keys are: {}".
                           format(key, config.options('BIBMANAGER')))
      print("{:s}: {:s}".format(key, config.get('BIBMANAGER', key)))
  else:
      print("\nbibmanager configuration file:"
            "\nKEY          VALUE"
            "\n-----------  -----")
      for key, value in config['BIBMANAGER'].items():
          print("{:11s}  {:s}".format(key, value))
