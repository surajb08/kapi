from typing import List

from k8_kat.base.kat_res import KatRes


class ResQueryExec:

  @staticmethod
  def filter_in_ns(ns_names: List[str], resources: List[KatRes]):
    if ns_names is not None:
      return [res for res in resources if res.ns in ns_names]
    else:
      return resources

  @staticmethod
  def filter_nin_ns(ns_names: List[str], resources: List[KatRes]):
    if ns_names is not None:
      return [res for res in resources if res.ns not in ns_names]
    else:
      return resources

  @staticmethod
  def filter_name_in(name_list: List[str], resources: List[KatRes]):
    if name_list is not None:
      return [res for res in resources if res.name in name_list]
    else:
      return resources
