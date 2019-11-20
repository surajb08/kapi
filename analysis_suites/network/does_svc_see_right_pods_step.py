from kubernetes.client.rest import ApiException

from analysis_suites.network.network_suite import BaseNetworkStep


class DoesSvcSeeRightPodsStep(BaseNetworkStep):

  @staticmethod
  def address_pod(address):
    return address.target_ref.name

  def agg_addresses(self, subset):
    return [self.address_pod(addr) for addr in subset.addresses]

  def agg_subsets(self, subsets):
    addr_groups = [self.agg_addresses(subset) for subset in subsets]
    return [item for sublist in addr_groups for item in sublist]

  def is_pod_ours(self, pod_name):
    dep_pods = self.dep.pods(force_reload=True)
    belongs = pod_name in [p.name for p in dep_pods]

    return {
      "name": pod_name,
      "belongs": belongs
    }

  def belonging_str(self, bundle):
    prefix = "" if bundle['belongs'] else "NOT "
    return f"{bundle['name']} --> {prefix}{self.dep.name}"

  def perform(self):
    try:
      endpoint = self.api.read_namespaced_endpoints(self.svc.name, self.svc.ns)
      pod_names = self.agg_subsets(endpoint.subsets or [])
      belongings = [self.is_pod_ours(pod) for pod in pod_names]
      intruders = [bun for bun in belongings if not bun['belongs']]
      outputs = [self.belonging_str(bundle) for bundle in belongings]

      return self.record_step_performed(
        outcome=len(intruders) == 0,
        outputs=outputs,
        bundle={}
      )

    except ApiException:
      return self.as_negative(
        outputs=['none'],
        bundle={}
      )
