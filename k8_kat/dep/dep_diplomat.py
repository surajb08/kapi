from kubernetes.client import V1Deployment, V1Service, V1Pod

from helpers.kube_broker import broker
from k8_kat.svc.svc_diplomat import SvcDiplomat
from utils.utils import Utils


class DepDiplomat:

  @staticmethod
  def dep_owns_pod(dep: V1Deployment, pod: V1Pod) -> bool:
    dep_matchers = dep.spec.selector.match_labels
    pod_labels = pod.metadata.labels
    if dep_matchers is None or pod_labels is None: return False
    return dep_matchers >= pod_labels

  @staticmethod
  def dep_matches_svc(dep: V1Deployment, svc: V1Service) -> bool:
    dep_pod_labels = dep.spec.template.metadata.labels
    svc_matchers = svc.spec.selector
    if dep_pod_labels is None or svc_matchers is None: return False
    return svc_matchers.items() >= dep_pod_labels.items()

  @staticmethod
  def dep_svcs(dep: V1Deployment) -> [V1Service]:
    ns_svcs = broker.coreV1.list_namespaced_service(
      namespace=dep.metadata.namespace
    ).items

    pod_labels = dep.spec.template.metadata.labels
    inclusion_check = lambda svc: SvcDiplomat.covers_labels(svc, pod_labels)
    return [svc for svc in ns_svcs if inclusion_check(svc)]

