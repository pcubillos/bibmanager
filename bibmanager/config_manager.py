# Copyright (c) 2018 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = ['reset']

import os
import shutil
import configparser


# Set these as a unique constant in the pakage (in __init__?)
ROOT = os.path.dirname(os.path.realpath(__file__)) + '/'
HOME = os.path.expanduser("~") + "/.bibmanager/"


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
  for key, value in config['BIBMANAGER'].items():
      print(key, value)


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
                           "\nAvailable keys are: {}".
                           format(key, config.options('BIBMANAGER')))
      print("{:s}: {:s}".format(key, config.get('BIBMANAGER', key)))
  else:
      print("\nbibmanager configuration file:"
            "\nKEY          VALUE"
            "\n-----------  -----")
      for key, value in config['BIBMANAGER'].items():
          print("{:11s}  {:s}".format(key, value))
