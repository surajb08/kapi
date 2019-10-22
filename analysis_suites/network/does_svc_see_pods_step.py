from kubernetes.client.rest import ApiException

from analysis_suites.network.network_suite import BaseNetworkStep


class DoesSvcSeePodsStep(BaseNetworkStep):

  @staticmethod
  def fmt_address(address):
    return f"{address.ip} @ {address.target_ref.name}"

  def agg_addresses(self, subset):
    return [self.fmt_address(addr) for addr in subset.addresses]

  def agg_subsets(self, subsets):
    addr_groups = [self.agg_addresses(subset) for subset in subsets]
    return [item for sublist in addr_groups for item in sublist]

  def perform(self):
    try:
      endpoint = self.api.read_namespaced_endpoints(self.svc_name, self.ns)
      formatted = self.agg_subsets(endpoint.subsets or [])
      return self.record_step_performed(
        outcome=len(formatted) > 0,
        outputs=formatted,
        bundle={"ep_count": len(formatted)}
      )
    except ApiException:
      return self.as_negative(
        outputs=['none'],
        bundle={}
      )
