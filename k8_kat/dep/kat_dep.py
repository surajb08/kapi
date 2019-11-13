from k8_kat.base.kat_res import KatRes
from k8_kat.dep.dep_diplomat import DepDiplomat as Diplomat
from k8_kat.pod.kat_pod import KatPod
from k8_kat.pod.pod_collection import PodCollection
from k8_kat.svc.kat_svc import KatSvc
from k8_kat.svc.svc_collection import SvcCollection

class KatDep(KatRes):
  def __init__(self, raw):
    super().__init__(raw)
    self._assoced_pods = None
    self._assoced_svcs = None

  @property
  def labels(self):
    return self.raw.metadata.match_labels

  def pods(self) -> [KatPod]:
    raw_pods = Diplomat.dep_pods(self.raw)
    return PodCollection(raw_pods)

  def svcs(self) -> [KatSvc]:
    raw_svcs = Diplomat.dep_svcs(self.raw)
    return SvcCollection(raw_svcs)

  def assoc_pods(self, candidates: [KatPod]) -> None:
    checker = lambda pod: Diplomat.dep_owns_pod(self.raw, pod.raw)
    self._assoced_pods = [pod for pod in candidates if checker(pod)]

  def assoc_svcs(self, candidates: [KatSvc]) -> None:
    checker = lambda svc: Diplomat.dep_matches_svc(self.raw, svc.raw)
    self._assoced_svcs = [svc for svc in candidates if checker(svc)]

  def release_assocs(self):
    self._assoced_pods = None
    self._assoced_svcs = None

  def __repr__(self):
    return f"Dep[{self.ns}:{self.name}({self.labels})]"
