from typing import List, Tuple

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

  @staticmethod
  def filter_lb_inc_any(label_tups: List[Tuple[str, str]], resources: List[KatRes]):
    if label_tups is not None:
      return [r for r in resources if set(label_tups) & set(r.label_tups)]
    else:
      return resources

  @staticmethod
  def filter_lb_exc_any(label_tups: List[Tuple[str, str]], resources: List[KatRes]):
    if label_tups is not None:
      return [r for r in resources if not set(label_tups) & set(r.label_tups)]
    else:
      return resources

  @staticmethod
  def filter_lb_inc_each(label_tups, resources: List[KatRes]):
    if label_tups is not None:
      return [r for r in resources if label_tups in r.label_tups]
    else:
      return resources

  @staticmethod
  def filter_lb_exc_each(label_tups, resources: List[KatRes]):
    if label_tups is not None:
      return [r for r in resources if label_tups not in r.label_tups]
    else:
      return resources
