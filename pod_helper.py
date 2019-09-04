import re
from kube_broker import broker
from utils import Utils


class PodHelper:

  POD_REGEX = "-([\w]{3,12})-([\w]{3,12})"

  @staticmethod
  def pods_for_dep_loaded(dep_name, pods):
    predicate = lambda p: PodHelper.is_pod_from_dep(p, dep_name)
    return list(filter(predicate, pods))

  @staticmethod
  def is_pod_from_dep(pod, dep_name):
    target_regex = f"^{dep_name}{PodHelper.POD_REGEX}$"
    re_result = re.search(target_regex, pod.metadata.name)
    return True if re_result else False

  @staticmethod
  def pods_for_dep(dep):
    label_match = Utils.dict_to_eq_str(dep.spec.selector.match_labels)

    pods = broker.coreV1.list_namespaced_pod(
      namespace=dep.metadata.namespace,
      label_selector=label_match
    ).items

    return PodHelper.pods_for_dep_loaded(
      dep.metadata.name, pods
    )

  @staticmethod
  def child_ser(pod):
    return {
      'name': pod.metadata.name,
      'namespace': pod.metadata.namespace,
      'state': Utils.try_or(lambda: pod.status.phase),
      'ip': Utils.try_or(lambda: pod.status.pod_ip)
    }

  @staticmethod
  def full_ser(pod):
    container = Utils.try_or(lambda: pod.spec.containers[0])
    return {
      **PodHelper.child_ser(pod),
      'image_name': Utils.try_or(lambda: container.image)
    }


