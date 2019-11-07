from helpers.kube_broker import broker
from utils.utils import Utils


class Kat:
  def __init__(self, raw):
    self.raw = raw

  @property
  def name(self):
    return self.raw.metadata.name

  @property
  def namespace(self):
    return self.raw.metadata.namespace

  @property
  def labels(self):
    return self.raw.metadata.labels

  @property
  def flat_labels(self):
    return Utils.dict_to_eq_str(self.labels)

class Deployment(Kat):

  def pods(self):
    raw_pods = broker.coreV1.list_namespaced_pod(
      namespace=self.namespace,
      label_selector=Utils.dict_to_eq_str(self.flat_labels)
    ).items

    return [Pod(raw_pod) for raw_pod in raw_pods]

class Pod(Kat):

  def deployment(self):
    pass

