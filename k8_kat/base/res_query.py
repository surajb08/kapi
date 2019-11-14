class ResQuery:
  def __init__(self):
    self._hash = self.default_query_hash()

  def update(self, **kwargs):
    self._hash = {
      **self._hash,
      **kwargs
    }

  @property
  def in_ns(self):
    return self._hash['in_ns']

  @property
  def not_in_ns(self):
    return self._hash['nin_ns']

  @property
  def name_in(self):
    return self._hash['name_in']

  @property
  def namespace(self):
    return self._hash['in_ns'][0]

  def is_single_ns(self):
    cond_one = len(self.in_ns or []) == 1
    cond_two = not self.not_in_ns
    return cond_one and cond_two

  @staticmethod
  def default_query_hash():
    return {
      'in_ns': None,
      'nin_ns': None,
      'name_in': None
    }
  