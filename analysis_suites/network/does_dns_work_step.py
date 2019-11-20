from analysis_suites.network.network_suite import BaseNetworkStep
from k8_kat.base.k8_kat import K8Kat


class DoesDnsWorkStep(BaseNetworkStep):

  def perform(self):
    possible_labels = [('k8s-app', 'kube-dns'), ('k8s-app', 'core-dns')]
    pods = K8Kat.pods().ns("kube-system").lbs_inc_any(possible_labels).go()
    running = [pod for pod in pods if pod.status == 'Running']
    outputs = [f"{pod.name}: {pod.phase}" for pod in pods]

    return self.record_step_performed(
      outcome=len(running) > 0,
      outputs=outputs,
      bundle={}
    )
