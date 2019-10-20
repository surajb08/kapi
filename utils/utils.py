import random
import string
from typing import Dict, List, Set
import datetime

class Utils:
  @staticmethod
  def try_or(lam, fallback=None):
    try:
      return lam()
    except:
      return fallback

  @staticmethod
  def dict_to_eq_str(_dict):
    return ",".join(
      ["=".join([k, str(v)])
       for k, v in _dict.items()]
    )

  @staticmethod
  def parse_dict(string):
    if string:
      result_dict = {}
      for encoded_dict in string.split(','):
        [key, value] = encoded_dict.split(':')
        result_dict[key] = value
      return result_dict
    else:
      return {}

  @staticmethod
  def rand_str(string_len=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_len))