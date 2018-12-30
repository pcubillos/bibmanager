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
  """
  config = configparser.ConfigParser()
  config.read(bm_config)

  if key is not None:
      print("".format(key), config.get('BIBMANAGER', key))
  else:
      print("\nbibmanager configuration file:\nKEY         : VALUE")
      for key, value in config['BIBMANAGER'].items():
          print("{:11s} : {:s}".format(key, value))
