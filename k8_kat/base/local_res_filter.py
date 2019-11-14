from typing import List

from k8_kat.base.kat_res import KatRes


class LocalResFilters:

  @staticmethod
  def filter_in_ns(ns_names: List[str], resources: List[KatRes]):
    if ns_names is not None:
      return [dep for dep in resources if dep.ns in ns_names]
    else:
      return resources

  @staticmethod
  def filter_nin_ns(ns_names: List[str], resources: List[KatRes]):
    if ns_names is not None:
      return [dep for dep in resources if dep.ns not in ns_names]
    else:
      return resources
