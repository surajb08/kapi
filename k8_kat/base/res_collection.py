
class ResCollection:
  def __init__(self):
    self.query = self.create_query()
    self._raw_collection = None

  def raw_collection(self):
    if not self._raw_collection:
      self.go()
    return self._raw_collection

  def where(self, **query_hash):
    self.query.update(**query_hash)
    return self

  def ns(self, namespace):
    return self.where(in_ns=[namespace])

  def ins(self, namespaces):
    return self.where(in_ns=namespaces)

  def nins(self, namespaces):
    return self.where(nin_ns=namespaces)

  def go(self):
    self._raw_collection = self.query.evaluate()
    return self._raw_collection

  def create_query(self):
    raise Exception("Unimplemented!")
