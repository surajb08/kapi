from k8_kats.kat_res import KatRes

class KatDep(KatRes):
  def __init__(self, raw):
    super().__init__(raw)

  def __repr__(self):
    return f"Deployment[{self.ns}:{self.name}]"
