from typing import Dict, Tuple, List

from k8_kat.base.label_set_expressions import LabelSetExpressions
from k8_kat.base.res_query import ResQuery
from k8_kat.dep.dep_query_exec import DepQueryExec as Exec
from k8_kat.dep.kat_dep import KatDep


class DepQuery(ResQuery):
  def evaluate(self):
    deps = self.perform_server_eval()
    return self.perform_local_eval(deps)

  def label_query_kv(self) -> Dict[str, Tuple[str, List[str]]]:
    keys = set(self.default_label_query_hash().keys())
    total, all_keys = self._hash, set(self._hash.keys())
    return {k: total[k] for k in all_keys if k in keys}

  def gen_label_selector(self):
    return LabelSetExpressions.label_conditions_to_expr(
      **self.label_query_kv()
    )

  def perform_server_eval(self) -> List[KatDep]:
    labels_expr = self.gen_label_selector()
    print(f"{labels_expr}")
    if self.is_single_ns():
      result = Exec.fetch_for_single_ns(self.namespace, labels_expr)
    else:
      result = Exec.fetch_for_all_ns(labels_expr)
    return [KatDep(raw_dep) for raw_dep in result]

  def perform_local_eval(self, deps):
    if not self.is_single_ns():
      deps = Exec.filter_in_ns(self.in_ns, deps)
      deps = Exec.filter_nin_ns(self.not_in_ns, deps)

    deps = Exec.filter_name_in(self.name_in, deps)
    return deps

  @staticmethod
  def default_query_hash():
    return {
      **ResQuery.default_query_hash(),
      **DepQuery.default_label_query_hash()
    }

  @staticmethod
  def default_label_query_hash():
    return {
      'and_yes_labels': None,
      'and_no_labels': None,
      'or_yes_labels': None,
      'or_no_labels': None,
    }
