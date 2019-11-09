import re

from kubernetes.client.rest import ApiException

from helpers.kube_broker import broker
from utils.utils import Utils
import datetime as dt


class PodHelper:
  POD_REGEX = "-([\w]{3,12})-([\w]{3,12})"

  @staticmethod
  def logs_since(namespace, name, timestamp):

    now = dt.datetime.now()
    seconds = (now - timestamp).total_seconds()

    result = broker.coreV1.read_namespaced_pod_log(
      namespace=namespace,
      name=name,
      since_seconds=400
    )

    return result

  @staticmethod
  def find(namespace, name):
    try:
      return broker.coreV1.read_namespaced_pod(
        name,
        namespace
      )
    except ApiException as r:
      print(f"FAIL {r}")
      return None

  @staticmethod
  def find_by_label(namespace, labels):
    if namespace is not None:
      return broker.coreV1.list_namespaced_pod(
        namespace=namespace,
        label_selector=Utils.dict_to_eq_str(labels)
      ).items
    else:
      return broker.coreV1.list_pod_for_all_namespaces(
        label_selector=Utils.dict_to_eq_str(labels)
      ).items

  @staticmethod
  def find_rs(namespace, name):
    try:
      return broker.appsV1Api.read_namespaced_replica_set(
        name,
        namespace
      )
    except ApiException as r:
      print(f"FAIL {r}")
      return None

  @staticmethod
  def find_dp(namespace, name):
    try:
      return broker.appsV1Api.read_namespaced_deployment(
        name,
        namespace
      )
    except ApiException as r:
      print(f"FAIL {r}")
      return None

  @staticmethod
  def belongs_to_dep(pod, dep):
    actual_dep = PodHelper.pod_dep(pod)
    if dep and actual_dep:
      return dep.metadata.uid == actual_dep.metadata.uid
    else:
      return False

  @staticmethod
  def pod_rs(pod):
    refs = pod.metadata.owner_references
    rs_refs = [ref for ref in refs if ref.kind == 'ReplicaSet']
    if len(rs_refs) is 1:
      rs_name = rs_refs[0].name
      return PodHelper.find_rs(pod.metadata.namespace, rs_name)
    else:
      return None

  @staticmethod
  def rs_dep(rs):
    refs = rs.metadata.owner_references
    rs_refs = [ref for ref in refs if ref.kind == 'Deployment']
    if len(rs_refs) is 1:
      rs_name = rs_refs[0].name
      return PodHelper.find_dp(rs.metadata.namespace, rs_name)
    else:
      return None

  @staticmethod
  def pod_dep(pod):
    rs = PodHelper.pod_rs(pod)
    return rs and PodHelper.rs_dep(rs)

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
  def pods_for_dep(dep, hard=True):
    label_match = Utils.dict_to_eq_str(dep.spec.selector.match_labels)

    pods = broker.coreV1.list_namespaced_pod(
      namespace=dep.metadata.namespace,
      label_selector=label_match
    ).items

    if hard:
      return PodHelper.pods_for_dep_loaded(
        dep.metadata.name, pods
      )
    else:
      return pods

  @staticmethod
  def pod_err(pod):
    cont_status = pod.status.container_statuses[0]
    term = Utils.try_or(lambda: cont_status.state.terminated)
    wait = Utils.try_or(lambda: cont_status.state.waiting)
    if term:
      return term.reason
    elif wait:
      return wait.reason
    else:
      return None

  @staticmethod
  def easy_error(state, pod):
    if state == 'Error' or state == 'Failed':
      return PodHelper.pod_err(pod)
    else:
      return None

  @staticmethod
  def easy_state(pod):
    given_phase = pod.status.phase
    cont_status = pod.status.container_statuses[0]
    error = Utils.try_or(lambda: PodHelper.pod_err(pod))

    if given_phase == 'Running':
      if not cont_status.ready:
        if not error == 'Completed':
          return 'Error'
        else:
          return 'Running'
      else:
        return given_phase
    elif given_phase == 'Pending':
      if error == 'ContainerCreating':
        return 'Pending'
      else:
        return 'Error'
    else:
      return given_phase

  @staticmethod
  def child_ser(pod):
    ts = lambda: pod.status.container_statuses[0].state.running.started_at

    # cont_status = pod.status.container_statuses[0]
    given_phase = pod.status.phase
    # error = Utils.try_or(lambda: PodHelper.pod_err(pod))
    easy_status = Utils.try_or(lambda: PodHelper.easy_state(pod), given_phase)
    easy_error = Utils.try_or(lambda: PodHelper.easy_error(pod, easy_status))
    # print(f"{given_phase} + {error}/{cont_status.ready} --> {easy_status}")

    return {
      'name': pod.metadata.name,
      'namespace': pod.metadata.namespace,
      'state': easy_status,
      'ip': Utils.try_or(lambda: pod.status.pod_ip),
      'error': easy_error,
      'updated_at': Utils.try_or(ts),
      'image_name': Utils.try_or(lambda: pod.spec.containers[0].image),
      'standard': len(pod.spec.containers) == 1
    }

  @staticmethod
  def full_ser(pod):
    container = Utils.try_or(lambda: pod.spec.containers[0])
    return {
      **PodHelper.child_ser(pod),
      'image_name': Utils.try_or(lambda: container.image)
    }
