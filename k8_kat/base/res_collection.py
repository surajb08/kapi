from typing import List, Tuple

from k8_kat.base.res_query import ResQuery


class ResCollection(list):
  def __init__(self):
    super().__init__()
    self.query: ResQuery = self.create_query()
    self._actual = []
    self._has_run = False

  def __getitem__(self, y):
    return self._actual[y]

  def __iter__(self):
    return self._actual.__iter__()

  def __len__(self):
    return len(self._actual)

  def find(self, name):
    return self.names(name).go()[0]

  def names(self, *_names):
    actual = [_names] if isinstance(_names, str) else _names
    return self.where(name_in=actual)

  def where(self, **query_hash):
    self.query.update(**query_hash)
    return self

  def ns(self, *_ns):
    actual = [_ns] if isinstance(_ns, str) else _ns
    return self.where(in_ns=actual)

  def not_ns(self, *_ns):
    actual = [_ns] if isinstance(_ns, str) else _ns
    return self.where(nin_ns=actual)

  def lbs_inc_each(self, label_array=None, **kwargs):
    label_array = list(dict(kwargs)) if kwargs else label_array
    return self.where(lbs_inc_each=label_array)

  def lbs_exc_each(self, label_array: List[Tuple[str, str]], **kwargs):
    label_array = list(dict(kwargs)) if kwargs else label_array
    return self.where(lbs_exc_each=label_array)

  def lbs_inc_any(self, label_array: List[Tuple[str, str]], **kwargs):
    label_array = list(dict(kwargs)) if kwargs else label_array
    return self.where(lbs_inc_any=label_array)

  def lbs_exc_any(self, label_array: List[Tuple[str, str]], **kwargs):
    label_array = list(dict(kwargs)) if kwargs else label_array
    return self.where(lbs_exc_any=label_array)

  def go(self):
    if not self._has_run:
      self._actual = self.query.evaluate()
      self._has_run = True
    return self

  def create_query(self):
    raise Exception("Unimplemented!")

