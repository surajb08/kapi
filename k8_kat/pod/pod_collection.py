from k8_kat.base.res_collection import ResCollection

class PodCollection(ResCollection):
  def wel(self, label_array):
    return self.where(with_either_label=label_array)

  def wnl(self, label_array):
    return self.where(with_neither_label=label_array)

  def svcs(self):
    pass

  def for_ns(self, kind, namespaces):
    is_white = kind == 'whitelist'
    return self.ns(namespaces) if is_white else self.nins(namespaces)

  def for_lbs(self, kind, label_array):
    is_white = kind == 'whitelist'
    return self.wel(label_array) if is_white else self.wnl(label_array)


