from analysis_suites.network.network_suite import BaseNetworkStep


class ArePodsRunningStep(BaseNetworkStep):

  @staticmethod
  def result_str(pod):
    return f"{pod.name} --> {pod.status}"

  def perform(self):
    pods = self.dep.pods()
    running = [pod for pod in pods if pod.is_running()]
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
