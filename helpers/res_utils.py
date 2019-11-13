import re

from kubernetes.client.rest import ApiException

from helpers.kube_broker import broker
from utils.utils import Utils
import datetime as dt


class ResUtils:
  LOG_REGEX = r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b) - - (.*)"

  @staticmethod
  def find_rs(namespace, name):
    try:
      return broker.appsV1Api.read_namespaced_replica_set(
        name,
        namespace
      )
    except ApiException:
      return None

  @staticmethod
  def find_pod(namespace, name):
    try:
      return broker.coreV1.read_namespaced_pod(
        name,
        namespace
      )
    except ApiException:
      return None

  @staticmethod
  def matching_ref(refs, exp_type, exp_name):
    for res_ref in refs:
      if res_ref.kind == exp_type:
        if res_ref.name == exp_name:
          return res_ref
    return None

  @staticmethod
  def try_clean_log_line(line):
    try:
      match = re.search(ResUtils.LOG_REGEX, line)
      return match.group(2) or line
    except:
      return line

  @staticmethod
  def find_dp(namespace, name):
    try:
      return broker.appsV1Api.read_namespaced_deployment(
        name,
        namespace
      )
    except ApiException as r:
      return None

  @staticmethod
  def container_err(cont_status):
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
      return ResUtils.container_err(pod)
    else:
      return None

  @staticmethod
  def easy_state(pod, hard_error=False):
    given_phase = pod.status.phase
    cont_status = pod.status.container_statuses[0]
    error = Utils.try_or(lambda: ResUtils.container_err(pod))

    if given_phase == 'Running':
      if not cont_status.ready:
        if not error == 'Completed':
          return (hard_error and error) or "Error"
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
  def true_pod_state(given_phase, cont_status, hard_error):
    error = Utils.try_or(lambda: ResUtils.container_err(cont_status))

    if given_phase == 'Running':
      if not cont_status.ready:
        if not error == 'Completed':
          return (hard_error and error) or "Error"
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

