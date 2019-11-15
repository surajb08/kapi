from utils.utils import Utils

class PodUtils:

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
      return PodUtils.container_err(pod)
    else:
      return None

  @staticmethod
  def easy_state(pod, hard_error=False):
    given_phase = pod.status.phase
    cont_status = pod.status.container_statuses[0]
    error = Utils.try_or(lambda: PodUtils.container_err(pod))

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
    error = Utils.try_or(lambda: PodUtils.container_err(cont_status))

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

