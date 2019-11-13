from analysis_suites.network.network_suite import BaseNetworkStep
from helpers.res_utils import ResUtils


class ArePodsRunningStep(BaseNetworkStep):

  @staticmethod
  def phase(pod):
    return ResUtils.easy_state(pod, True)

  def result_str(self, pod):
    return f"{pod.metadata.name} --> {self.phase(pod)}"

  def is_running(self, pod):
    return self.phase(pod) == 'Running'

  def perform(self):
    pods = ResUtils.pods_for_dep(self.deployment, False)
    running = [pod for pod in pods if self.is_running(pod)]
    outputs = [self.result_str(pod) for pod in pods]
    return self.record_step_performed(
      outcome=len(running) > 0,
      outputs=outputs,
      bundle={
        "pods_running": len(running),
        "pods_not_running": len(pods) - len(running),
        "pods_total": len(pods)
      }
    )
