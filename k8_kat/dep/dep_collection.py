from typing import List, Tuple

from k8_kat.base.res_collection import ResCollection
from k8_kat.dep.dep_query import DepQuery


class DepCollection(ResCollection):
  def create_query(self):
    return DepQuery()

  def every_lb(self, label_array: List[Tuple[str, str]]):
    return self.where(and_yes_labels=label_array)

  def any_lb(self, label_array: List[Tuple[str, str]]):
    return self.where(or_yes_labels=label_array)

  def not_every_lb(self, label_array: List[Tuple[str, str]]):
    return self.where(and_no_labels=label_array)

  def not_any_lb(self, label_array: List[Tuple[str, str]]):
    return self.where(or_no_labels=label_array)

  # def for_ns(self, kind, namespaces):
  #   is_white = kind == 'whitelist'
  #   return self.ins(namespaces) if is_white else self.nins(namespaces)
  #
  # def for_lbs(self, kind, label_array):
  #   is_white = kind == 'whitelist'
  #   return self.wel(label_array) if is_white else self.wnl(label_array)
