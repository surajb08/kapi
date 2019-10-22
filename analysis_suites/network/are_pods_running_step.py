from analysis_suites.network.network_suite import BaseNetworkStep
from helpers.pod_helper import PodHelper


class ArePodsRunningStep(BaseNetworkStep):

  @staticmethod
  def phase(pod):
    return pod.status.phase

  def result_str(self, pod):
    return f"{pod.metadata.name} --> {self.phase(pod)}"

  def is_running(self, pod):
    return self.phase(pod) == 'Running'

  def perform(self):
    pods = PodHelper.pods_for_dep(self.deployment, False)
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
