from typing import List, Tuple

from k8_kat.base.res_collection import ResCollection
from k8_kat.dep.dep_query import DepQuery


class DepCollection(ResCollection):
  def create_query(self):
    return DepQuery()

