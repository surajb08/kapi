from k8_kat.dep.dep_collection import DepCollection
from k8_kat.pod.pod_collection import PodCollection
from k8_kat.svc.svc_collection import SvcCollection


class K8kat:

  @staticmethod
  def deps(**kwargs) -> DepCollection:
    collection = DepCollection()
    return collection.where(**kwargs)

  @staticmethod
  def svcs(**kwargs) -> SvcCollection:
    collection = SvcCollection()
    return collection.where(**kwargs)

  @staticmethod
  def pods(**kwargs) -> PodCollection:
    collection = PodCollection()
    return collection.where(**kwargs)
