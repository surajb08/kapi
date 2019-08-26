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
  def parse_dict(string):
    result_dict = {}
    for encoded_dict in string.split(','):
      [key, value] = encoded_dict.split(':')
      result_dict[key] = value
    return result_dict
