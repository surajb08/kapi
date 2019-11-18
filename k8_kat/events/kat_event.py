
class KatEvent:

  def __init__(self, raw):
    self.raw = raw

  @property
  def for_uid(self):
    return self.raw.involved_object.uid

  @property
  def for_kind(self):
    return self.raw.involved_object.kind

  @property
  def for_ns(self):
    return self.raw.involved_object.namespace

  @property
  def for_name(self):
    return self.raw.involved_object.name

  def is_for(self, kat_res):
    return self.for_uid == kat_res.uid