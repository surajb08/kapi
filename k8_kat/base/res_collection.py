
class ResCollection:
  def __init__(self, raw_collection=None):
    self.query = self.create_query()
    self.query_result = raw_collection

  def raw_collection(self):
    if not self.query_result:
      self.go()
    return self.query_result

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
