from helpers.kube_broker import broker
from k8_kats.kat_dep import KatDep
from utils.utils import Utils

class PolyNsServerEval:
  def __init__(self, label_match):
    self.label_match = label_match

  def evaluate(self):
    api = broker.appsV1Api
    raw_items = api.list_deployment_for_all_namespaces().items
    print(f"INITIAL GOT ME {len(raw_items)}")
    return [KatDep(item) for item in raw_items]
    

class OneNsServerEval:
  def __init__(self, namespace, label_match):
    self.namespace = namespace
    self.label_match = label_match

  def evaluate(self):
    api = broker.appsV1Api
    raw_items = api.list_namespaced_deployment(
      namespace=self.namespace
    ).items
    return [KatDep(item) for item in raw_items]

class DepQuery:
  def __init__(self):
    self._hash = {
      'in_ns': None,
      'nin_ns': None,
      'with_either_label': None,
      'with_neither_label': None,
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
    cond_one = len(self._hash['in_ns'] or []) == 1
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
    if namespaces is not None:
      return [dep for dep in deps if dep.ns in namespaces]
    else:
      return deps

  def filter_nin_ns(self, deps):
    namespaces = self._hash['nin_ns']
    if namespaces is not None:
      return [dep for dep in deps if dep.ns not in namespaces]
    else:
      return deps

  def filter_with_either_label(self, deps):
    cond_labels = self._hash['with_either_label']
    if cond_labels and Utils.is_non_trivial(cond_labels):
      func = Utils.is_either_hash_in_hash
      return [dep for dep in deps if func(dep.labels, cond_labels)]
    else:
      return deps

  def filter_with_neither_label(self, deps):
    cond_labels = self._hash['with_neither_label']
    if cond_labels and Utils.is_non_trivial(cond_labels):
      func = Utils.is_either_hash_in_hash
      return [dep for dep in deps if not func(dep.labels, cond_labels)]
    else:
      return deps

  def perform_local_eval(self, deps):
    deps = self.filter_in_ns(deps)
    deps = self.filter_nin_ns(deps)
    deps = self.filter_with_either_label(deps)
    deps = self.filter_with_neither_label(deps)
    return deps

  def evaluate(self):
    deps = self.perform_server_eval()
    return self.perform_local_eval(deps)

