from typing import Any, Dict
from k8_kat.svc.kat_svc import KatSvc

class SvcSerialization:

  @staticmethod
  def standard(svc: KatSvc) -> Dict[str, Any]:

    def bundle_port(po) -> Dict[str, str]:
      return {'from_port': po.port, 'to_port': po.target_port}

    port_bundles = [bundle_port(po) for po in svc.raw.spec.ports]

    return {
      "name": svc.name,
      "namespace": svc.namespace,
      "internal_ip": svc.internal_ip,
      "external_ip": svc.external_ip,
      "from_port": svc.from_port,
      "to_port": svc.to_port,
      "short_dns": svc.short_dns,
      "long_dns": svc.fqdn,
      "ports": port_bundles,
      "type": svc.type,
      "selector_labels": svc.pod_select_labels
    }
