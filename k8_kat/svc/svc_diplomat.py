from kubernetes.client import V1Service, V1Pod
from typing import Dict


class SvcDiplomat:

  @staticmethod
  def covers_labels(svc: V1Service, labels: Dict[str, str]) -> bool:
    svc_matchers: Dict[str, str] = svc.spec.selector
    return svc_matchers >= labels if svc_matchers is not None else False

  @staticmethod
  def covers_pod(svc: V1Service, pod: V1Pod) -> bool:
    pod_labels: Dict[str, str] = pod.metadata.labels
    svc_matchers: Dict[str, str] = svc.spec.selector
    return svc_matchers >= pod_labels if svc_matchers is not None else False




