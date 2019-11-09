from helpers.kube_broker import broker
from k8_kats.kat_dep import KatDep
from utils.utils import Utils

class PolyNsServerEval:
  def __init__(self, label_match):
    self.label_match = label_match

  def evaluate(self):
    api = broker.appsV1Api
    fmt_labels_cond = Utils.dict_to_eq_str(self.label_match)
    raw_items = api.list_deployment_for_all_namespaces(
      label_selector=fmt_labels_cond
    ).items
    return [KatDep(item) for item in raw_items]
    

class OneNsServerEval:
  def __init__(self, namespace, label_match):
    self.namespace = namespace
    self.label_match = label_match

  def evaluate(self):
    api = broker.appsV1Api
    fmt_labels_cond = Utils.dict_to_eq_str(self.label_match)
    raw_items = api.list_namespaced_deployment(
      namespace=self.namespace,
      label_selector=fmt_labels_cond
    ).items
    return [KatDep(item) for item in raw_items]

class DepQuery:
  def __init__(self):
    self._hash = {
      'in_ns': [],
      'nin_ns': [],
      'with_either_label': [],
      'with_neither_label': [],
      'with_exact_labels': {},
      'in_phase': [],
      'problematic': False
    }

  def update(self, **kwargs):
    self._hash = {
      **self._hash,
      **kwargs
    }

  def is_single_ns(self):
    cond_one = len(self._hash['in_ns']) == 1
    cond_two = not self._hash['nin_ns']
    return cond_one and cond_two

  def can_server_q_labels(self):
    label_cond_one = not self._hash['with_either_label']
    label_cond_two = not self._hash['with_neither_label']
    return label_cond_one and label_cond_two

  def perform_server_eval(self):
    label_cond = self._hash['with_exact_labels']
    if self.is_single_ns():
      namespace = self._hash['in_ns'][0]
      evaluator = OneNsServerEval(namespace, label_cond)
      return evaluator.evaluate()
    else:
      evaluator = PolyNsServerEval(label_cond)
      return evaluator.evaluate()

  def filter_in_ns(self, deps):
    namespaces = self._hash['in_ns']
    return [dep for dep in deps if dep.ns in namespaces]

  def filter_nin_ns(self, deps):
    namespaces = self._hash['nin_ns']
    return [dep for dep in deps if dep.ns not in namespaces]

  def filter_with_either_label(self, deps):
    cond_labels = self._hash['with_either_label']
    func = Utils.is_either_hash_in_hash
    return [dep for dep in deps if func(dep.labels, cond_labels)]

  def filter_with_neither_label(self, deps):
    cond_labels = self._hash['with_neither_label']
    func = Utils.is_either_hash_in_hash
    return [dep for dep in deps if not func(dep.labels, cond_labels)]

  def perform_local_eval(self, deps):
    deps = self.filter_in_ns(deps)
    deps = self.filter_nin_ns(deps)
    # deps = self.filter_with_either_label(deps)
    # deps = self.filter_with_neither_label(deps)
    return deps

  def evaluate(self):
    deps = self.perform_server_eval()
    return self.perform_local_eval(deps)

