from analysis_suites.network.network_suite import BaseNetworkStep
from helpers.pod_helper import PodHelper


class DoPodsConnectStep(BaseNetworkStep):

  @staticmethod
  def result_str(result):
    noun = 'pass' if result['pass'] else 'fail'
    return f"{result['name']} --> {noun}"

  def pod_endpoint(self, pod):
    return f"{pod.status.pod_ip}:{self.to_port}"

  def curl_pass_fail(self, pod):
    result = self.stunt_pod.curl(url=self.pod_endpoint(pod))
    return {
      "name": pod.metadata.name,
      "pass": result['finished']
    }

  def perform(self):
    pods = PodHelper.pods_for_dep(self.deployment, False)
    results = [self.curl_pass_fail(pod) for pod in pods]
    failures = [result for result in results if not result['pass']]
    culprits = ", ".join([result['name'] for result in failures])
    results_str = [self.result_str(r) for r in results]

    return self.record_step_performed(
      outcome=len(failures) == 0,
      outputs=results_str,
      bundle={"culprits": culprits}
    )

