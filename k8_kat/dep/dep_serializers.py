from typing import Any, Dict
from k8_kat.pod.pod_serialization import PodSerialization
from k8_kat.svc.svc_serialization import SvcSerialization


class DepSerialization:

  @staticmethod
  def standard(dep) -> Dict[str, Any]:
    return dict(
      name=dep.name,
      namespace=dep.namespace,
      labels=dep.labels,
      replicas=dep.raw.spec.replicas,
      image_name=dep.image_name,
      container_name=dep.container_name,
      commit=dep.commit
    )

  @staticmethod
  def with_pods_and_svcs(dep) -> Dict[str, Any]:
    pod_ser = PodSerialization.standard
    svc_ser = SvcSerialization.standard

    return {
      **DepSerialization.standard(dep),
      **dict(
        pods=[pod_ser(pod) for pod in dep.pods()],
        svcs=[svc_ser(pod) for pod in dep.svcs()]
      )
    }
