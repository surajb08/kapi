
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

  @property
  def reason(self):
    return self.raw.reason

  @property
  def message(self):
    return self.message

  def is_for(self, kat_res):
    return self.for_uid == kat_res.uid

  def is_config_map_err(self):
    return "configmaps" in self.message

  def is_secrets_err(self):
    return "with: secrets" in self.message

  def is_probe_err(self):
    return self.reason == 'Unhealthy'

  def is_insufficient_cpu(self):
    return "Insufficient cpu" in self.message
