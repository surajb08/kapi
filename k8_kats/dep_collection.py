from k8_kats.dep_query import DepQuery

class DepCollection:
  def __init__(self):
    self.query = DepQuery()

  def where(self, **query_hash):
    self.query.update(**query_hash)
    return self

  def ins(self, *namespaces):
    return self.where(in_ns=[*namespaces])

  def nins(self, *namespaces):
    return self.where(nin_ns=[*namespaces])

  def wel(self, label_array):
    return self.where(with_either_label=label_array)

  def wnl(self, label_array):
    return self.where(with_neither_label=label_array)

  def go(self):
    return self.query.evaluate()

  def get_where(self, **query):
    return self.where(**query).go()
