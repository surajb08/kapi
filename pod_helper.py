import re
from kube_broker import broker

class PodHelper:

  POD_REGEX = "-([\w]{5,10})-([\w]{5,10})"

  @staticmethod
  def pods_for_deps(deps):
    broker.check_connected()
    pods = broker.coreV1.list_pod_for_all_namespaces().items
    lm = lambda d: {'dep': d, 'pods': PodHelper.pods_for_dep(d, pods)}
    return list(map(lm, deps))

  @staticmethod
  def pods_for_dep(dep, pods):
    broker.check_connected()
    target_regex = f"^{dep.metadata.name}{PodHelper.POD_REGEX}$"

    def finder(pod):
      re_result = re.search(target_regex, pod.metadata.name)
      return True if re_result else False

    return list(filter(finder, pods))

  @staticmethod
  def dep_for_pod(pod, deps):
    target_pod_lbs = pod.metadata.labels
    target_pod_lbs.pop('pod-template-hash')
    finder = lambda d: d.spec.selector.match_labels == target_pod_lbs
    matches = list(filter(finder, deps))
    if len(matches) == 1:
      return matches[0]
    else:
      print(f"Found {len(matches)} matches for {target_pod_lbs}!")
      return None

  @staticmethod
  def deployment_ser(pod):
    return {
      "name": pod.metadata.name,
      "state": pod.spec.containers[0].image
    }