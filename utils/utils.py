import random
import string

class Utils:

  @staticmethod
  def hash_has_any_matches(big, small):
    small_tuples = (small or {}).items()
    print(f"IS {small_tuples} inside {(big or {}).items()}?")
    for _tuple in (big or {}).items():
      if _tuple in small_tuples:
        print("YES")
        return True
    print("NO")
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
      ["=".join([k, str(v)])
       for k, v in _dict.items()]
    )

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
