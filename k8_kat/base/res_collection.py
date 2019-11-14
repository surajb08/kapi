from k8_kat.base.res_query import ResQuery


class ResCollection:
  def __init__(self, raw_collection=None):
    self.query: ResQuery = self.create_query()
    self.query_result = raw_collection

  def raw_collection(self):
    if not self.query_result:
      self.go()
    return self.query_result

  def names(self, *_names):
    actual = [_names] if isinstance(_names, str) else _names
    return self.where(name_in=actual)

  def where(self, **query_hash):
    self.query.update(**query_hash)
    return self

  def ns(self, *_ns):
    actual = [_ns] if isinstance(_ns, str) else _ns
    return self.where(in_ns=actual)

  def nins(self, namespaces):
    return self.where(nin_ns=namespaces)

  def go(self):
    self.query_result = self.query.evaluate()
    return self.query_result

  def create_query(self):
    raise Exception("Unimplemented!")
