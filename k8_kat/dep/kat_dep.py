from typing import Dict, List

from kubernetes.client import V1PodSpec, V1Container, V1Pod

from k8_kat.base.kat_res import KatRes
from k8_kat.dep.dep_diplomat import DepDiplomat as Diplomat
from k8_kat.pod.kat_pod import KatPod
from k8_kat.pod.pod_collection import PodCollection
from k8_kat.svc.kat_svc import KatSvc
from k8_kat.svc.svc_collection import SvcCollection

COMMIT_KEYS = ['sha', 'branch', 'message', 'timestamp']

class KatDep(KatRes):
  def __init__(self, raw):
    super().__init__(raw)
    self._assoced_pods = None
    self._assoced_svcs = None

  @property
  def raw_pod_spec(self) -> V1PodSpec:
    return self.raw.spec.template.spec

  @property
  def raw_container_spec(self) -> V1Container:
    specs = self.raw_pod_spec.containers
    return specs[0] if len(specs) else None

  @property
  def image_name(self) -> str:
    container_spec = self.raw_container_spec
    return container_spec and container_spec.image

  @property
  def container_name(self) -> str:
    container_spec = self.raw_container_spec
    return container_spec and container_spec.name

  @property
  def commit(self) -> Dict[str, str]:
    every = self.raw.metadata.annotations
    return dict([(k, every.get(f"commit-{k}")) for k in COMMIT_KEYS])

  def svcs(self) -> [KatSvc]:
    return self._assoced_svcs

  def assoc_pods(self, candidates: List[V1Pod]) -> None:
    checker = lambda pod: Diplomat.dep_owns_pod(self.raw, pod)
    self._assoced_pods = [KatPod(pod) for pod in candidates if checker(pod)]

  def assoc_svcs(self, candidates: [KatSvc]) -> None:
    checker = lambda svc: Diplomat.dep_matches_svc(self.raw, svc)
    self._assoced_svcs = [KatSvc(svc) for svc in candidates if checker(svc)]

  def release_assocs(self):
    self._assoced_pods = None
    self._assoced_svcs = None

  def __repr__(self):
    return f"Dep[{self.ns}:{self.name}({self.labels})]"
