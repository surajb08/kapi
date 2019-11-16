from typing import Dict, Tuple, List, Any, Type
from k8_kat.base.kat_res import KatRes
from k8_kat.base.label_set_expressions import LabelLogic

class ResQuery():
  def __init__(self, executor, kat: Type[KatRes]):
    self._hash = self.default_query_hash()
    self.executor = executor
    self.kat = kat

  def evaluate(self) -> List[KatRes]:
    deps = self.perform_server_eval()
    return self.perform_local_eval(deps)

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

  def label_query_kv(self) -> Dict[str, Tuple[str, List[str]]]:
    keys = self.label_query_keys()
    total, all_keys = self._hash, set(self._hash.keys())
    return {k: total[k] for k in all_keys if k in keys}

  def gen_label_selector(self):
    return LabelLogic.label_conditions_to_expr(
      **self.label_query_kv()
    )

  def perform_server_eval(self) -> List[Any]:
    labels_expr = self.gen_label_selector()
    if self.is_single_ns():
      result = self.executor.fetch_for_single_ns(self.namespace, labels_expr)
    else:
      result = self.executor.fetch_for_all_ns(labels_expr)
    return [self.kat(raw_dep) for raw_dep in result]

  def perform_local_eval(self, deps):
    if not self.is_single_ns():
      deps = self.executor.filter_in_ns(self.in_ns, deps)
      deps = self.executor.filter_nin_ns(self.not_in_ns, deps)

    deps = self.executor.filter_name_in(self.name_in, deps)
    return deps

  @staticmethod
  def default_query_hash():
    return {
      'in_ns': None,
      'nin_ns': None,
      'name_in': None,
      'lbs_inc_each': None,
      'lbs_exc_each': None,
      'lbs_inc_any': None,
      'lbs_exc_any': None,
    }

  @staticmethod
  def label_query_keys():
    return ['lbs_inc_each', 'lbs_exc_each']
