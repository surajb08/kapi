from k8_kat.base.local_res_filter import LocalResFilters
from k8_kat.base.res_query import ResQuery
from k8_kat.dep.remote_dep_filter import RemoteDepFilter

class DepQuery(ResQuery):
  @property
  def with_either_label(self):
    return self._hash['with_either_label']

  @property
  def with_neither_label(self):
    return self._hash['with_neither_label']

  def perform_server_eval(self):
    rem_logic = RemoteDepFilter
    if self.is_single_ns():
      return rem_logic.fetch_single_namespace(self.namespace)
    else:
      return rem_logic.fetch_poly_namespace()

  def server_label_query(self):
    return self._hash['ins']

  def perform_local_eval(self, deps):
    local_logic = LocalResFilters
    deps = local_logic.filter_in_ns(
      self.in_ns,
      deps
    )
    deps = local_logic.filter_nin_ns(
      self.not_in_ns,
      deps
    )
    deps = local_logic.filter_with_either_label(
      self.with_either_label,
      deps
    )
    deps = local_logic.filter_with_neither_label(
      self.with_neither_label,
      deps
    )
    return deps

  def evaluate(self):
    deps = self.perform_server_eval()
    return self.perform_local_eval(deps)

  @staticmethod
  def default_query_hash():
    return {
      **ResQuery.default_query_hash(),
      'and_yes_labels': None,
      'and_no_labels': None,
      'or_yes_labels': None,
      'or_no_labels': None,
    }
