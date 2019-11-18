from typing import List, Tuple, Dict


class KatRes:

  def __init__(self, raw):
    self.is_dirty = False
    self.raw = raw

  @property
  def name(self):
    return self.raw.metadata.name

  @property
  def namespace(self):
    return self.raw.metadata.namespace

  @property
  def ns(self):
    return self.namespace

  @property
  def labels(self):
    return self.raw.metadata.labels

  @property
  def label_tups(self) -> List[Tuple[str, str]]:
    return list(self.labels.items())

  def label(self, which):
    return self.labels.get(which)

  @property
  def pod_select_labels(self) -> Dict[str, str]:
    raise Exception("Unimplemented!")

  def set_label(self, **labels):
    new_label_dict = {**self.labels, **labels}
    self.raw.metadata.labels = new_label_dict
    self._perform_patch_self()

  def _perform_patch_self(self):
    raise Exception("Unimplemented!")


  def serialize(self, serializer):
    return serializer(self)
