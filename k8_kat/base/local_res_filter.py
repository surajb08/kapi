from utils.utils import Utils

class LocalResFilters:

  @staticmethod
  def filter_in_ns(ns_names, resources):
    if ns_names is not None:
      return [dep for dep in resources if dep.ns in ns_names]
    else:
      return resources

  @staticmethod
  def filter_nin_ns(ns_names, resources):
    if ns_names is not None:
      return [dep for dep in resources if dep.ns not in ns_names]
    else:
      return resources

  @staticmethod
  def filter_with_either_label(cond_labels, resources):
    if Utils.is_non_trivial(cond_labels):
      func = Utils.is_either_hash_in_hash
      return [dep for dep in resources if func(dep.labels, cond_labels)]
    else:
      return resources

  @staticmethod
  def filter_with_neither_label(cond_labels, resources):
    if Utils.is_non_trivial(cond_labels):
      func = Utils.is_either_hash_in_hash
      return [dep for dep in resources if not func(dep.labels, cond_labels)]
    else:
      return resources
