from typing import List, Tuple


class KatRes:

  def __init__(self, raw):
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
    return self.raw.metadata.labels

  def label(self, which):
    return self.labels.get(which)

  def serialize(self, serializer):
    return serializer(self)
