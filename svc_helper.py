from kube_broker import broker
from utils import Utils


class SvcHelper:

  @staticmethod
  def svcs_for_dep(dep, all_svcs):
    match_labels = dep.spec.selector.match_labels
    finder = lambda svc: svc.spec.selector == match_labels
    return list(filter(finder, all_svcs))

  @staticmethod
  def child_ser(svc):
    name = svc.metadata.name
    namespace = svc.metadata.namespace
    port_obj = svc.spec.ports[0]
    get_ip = lambda: svc.status.load_balancer.ingress[0].ip

    return {
      "name": name,
      "internal_ip": svc.spec.cluster_ip,
      "external_ip": Utils.try_or(get_ip),
      "from_port": port_obj.port,
      "to_port": port_obj.target_port,
      "short_dns": name + "." + namespace,
      "long_dns": name + "." + namespace + ".svc.cluster.local",
    }