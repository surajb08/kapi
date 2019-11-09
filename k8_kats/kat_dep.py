from k8_kats.kat_res import KatRes

class KatDep(KatRes):
  def __init__(self, raw):
    super().__init__(raw)

  @property
  def labels(self):
    return self.raw.spec.selector.match_labels

  def __repr__(self):
    return f"Dep[{self.ns}:{self.name}({self.labels})]"
