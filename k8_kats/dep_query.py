from helpers.kube_broker import broker
from utils.utils import Utils

class PolyNsServerEval:
  def __init__(self, label_match):
    self.label_match = label_match

  def evaluate(self):
    api = broker.appsV1Api
    fmt_labels_cond = Utils.dict_to_eq_str(self.label_match)
    return api.list_deployment_for_all_namespaces(
      label_selector=fmt_labels_cond
    ).items

class OneNsServerEval:
  def __init__(self, namespace, label_match):
    self.namespace = namespace
    self.label_match = label_match

  def evaluate(self):
    api = broker.appsV1Api
    fmt_labels_cond = Utils.dict_to_eq_str(self.label_match)
    return api.list_namespaced_deployment(
      namespace=self.namespace,
      label_selector=fmt_labels_cond
    ).items

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
      evaluator = OneNsServerEval(label_cond, namespace)
      return evaluator.evaluate()
    else:
      evaluator = PolyNsServerEval(label_cond)
      return evaluator.evaluate()

  def filter_in_ns(self, _list):
    return []

  def filter_nin_ns(self, _list):
    return []

  def filter_with_either_label(self, _list):
    return []

  def filter_with_neither_label(self, _list):
    return []

  def perform_local_eval(self, _list):
    _list = self.filter_in_ns(_list)
    _list = self.filter_nin_ns(_list)
    _list = self.filter_with_either_label(_list)
    _list = self.filter_with_neither_label(_list)
    return _list

  def evaluate(self):
    v1_list = self.perform_server_eval()
    return self.perform_local_eval(v1_list)

  def update(self, new_hash):
    pass



