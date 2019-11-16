from k8_kat.base.res_collection import ResCollection
from k8_kat.base.res_query import ResQuery
from k8_kat.pod.kat_pod import KatPod
from k8_kat.pod.pod_query_exec import PodQueryExec


class PodCollection(ResCollection):

  def create_query(self):
    return ResQuery(PodQueryExec(), KatPod)
