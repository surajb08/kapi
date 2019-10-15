from debuggers.network_cons import PortParityReporter, ServiceTypeReporter, PodsRunningReporter, PortTypeReporter
from dep_helper import DepHelper
from pod_helper import PodHelper
from svc_helper import SvcHelper


class NetworkDebug:
  def __init__(self, **kwargs):
    self.source_type = kwargs.get('source_type', "in_namespace")
    self.exp_port = kwargs['exp_port']
    self.deployment = DepHelper.find(
      kwargs['dep_namespace'],
      kwargs['dep_name']
    )
    self.service = SvcHelper.find(
      kwargs['dep_namespace'],
      kwargs['svc_name']
    )

  def exp_port_bundle(self):
    predicate = lambda bundle: bundle.port == self.exp_port
    port_bundles = self.service.spec.ports
    return next((bun for bun in port_bundles if predicate(bun)), None)

  def svc_name(self):
    return self.service.metadata.name

  def dep_name(self):
    return self.deployment.metadata.name

  def check_pods_running(self):
    pods = PodHelper.pods_for_dep(self.deployment)
    checker = lambda x: x.status.phase == 'Running'
    running_count = len(list(filter(checker, pods)))
    reporter = PodsRunningReporter(self.dep_name(), running_count)
    if running_count > 0:
      return reporter.some_running()
    else:
      return reporter.none_running()

  def check_service_type(self):
    _type = self.service.spec.type
    reporter = ServiceTypeReporter(_type)
    if self.source_type == 'in_namespace':
      return reporter.in_ns_all_good()
    if self.source_type == 'out_cluster':
      if _type == 'LoadBalancer' or _type == 'NodePort':
        return reporter.out_cluster_correct()
      else:
        return reporter.out_cluster_mismatch()

  def check_port_types(self):
    rel_port_bundle = self.exp_port_bundle()
    in_port = rel_port_bundle.target_port
    reporter = PortTypeReporter(self.svc_name(), in_port)
    if isinstance(in_port, str):
      return reporter.port_is_string()
    else:
      return reporter.port_is_int()

  def check_port_parity(self, df_port):
    rel_port_bundle = self.exp_port_bundle()
    out_port = rel_port_bundle.port
    reporter = PortParityReporter(self.svc_name(), out_port, df_port)

    if df_port is not None:
      target_port = rel_port_bundle.target_port
      if df_port == target_port:
        return reporter.ports_match()
      else:
        return reporter.ports_dont_match()
    else:
      return reporter.dockerfile_shy()