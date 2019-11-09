import random
import string

class Utils:

  @staticmethod
  def is_non_trivial(dict_array):
    return [e for e in dict_array if e]

  @staticmethod
  def is_either_hash_in_hash(big_hash, little_hashes):
    little_tuples = [list(h.items())[0] for h in little_hashes]
    for _tuple in (big_hash or {}).items():
      if _tuple in little_tuples:
        return True
    return False

  @staticmethod
  def try_or(lam, fallback=None):
    try:
      return lam()
    except:
      return fallback

  @staticmethod
  def dict_to_eq_str(_dict):
    return ",".join(
      ["=".join([k, str(v)]) for k, v in _dict.items()]
    )

  @staticmethod
  def parse_dict_array(_string):
    parts = _string.split(',')
    return [Utils.parse_dict(part) for part in parts]

  @staticmethod
  def parse_dict(_string):
    print(f"GIVEN {_string}")
    if _string:
      result_dict = {}
      for encoded_dict in _string.split(','):
        [key, value] = encoded_dict.split(':')
        result_dict[key] = value
      return result_dict
    else:
      return {}

  @staticmethod
  def rand_str(string_len=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_len))

  @staticmethod
  def fqcn(o):
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
      return o.__class__.__name__
    else:
      return module + '.' + o.__class__.__name__
