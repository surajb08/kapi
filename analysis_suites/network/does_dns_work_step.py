from analysis_suites.network.network_suite import BaseNetworkStep
from helpers.res_utils import ResUtils


class DoesDnsWorkStep(BaseNetworkStep):

  def perform(self):
    k_pods = ResUtils.find_by_label("kube-system", {"k8s-app": "kube-dns"})
    c_pods = ResUtils.find_by_label("kube-system", {"k8s-app": "core-dns"})
    pods = k_pods + c_pods
    running = [pod for pod in pods if pod.status.phase == 'Running']
    outputs = [f"{pod.metadata.name}: {pod.status.phase}" for pod in pods]

    return self.record_step_performed(
      outcome=len(running) > 0,
      outputs=outputs,
      bundle={}
    )