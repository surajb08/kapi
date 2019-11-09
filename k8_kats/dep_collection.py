from k8_kats.dep_query import DepQuery

class DepCollection:
  def __init__(self):
    self.query = DepQuery()
    self._raw_collection = None

  def where(self, **query_hash):
    self.query.update(**query_hash)
    return self

  def ns(self, namespace):
    return self.where(in_ns=[namespace])

  def ins(self, namespaces):
    return self.where(in_ns=namespaces)

  def nins(self, namespaces):
    return self.where(nin_ns=namespaces)

  def wel(self, label_array):
    return self.where(with_either_label=label_array)

  def wnl(self, label_array):
    return self.where(with_neither_label=label_array)

  def raw_collection(self):
    if not self._raw_collection:
      self.go()
    return self._raw_collection

  def go(self):
    self._raw_collection = self.query.evaluate()
    return self._raw_collection

  def for_ns(self, kind, namespaces):
    is_white = kind == 'whitelist'
    return self.ins(namespaces) if is_white else self.nins(namespaces)

  def for_lbs(self, kind, label_array):
    is_white = kind == 'whitelist'
    return self.wel(label_array) if is_white else self.wnl(label_array)
