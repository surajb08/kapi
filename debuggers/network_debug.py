from dep_helper import DepHelper
from kube_broker import broker
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
    def finder(bun):
      return bun.port == self.exp_port

    svc_ports = self.service.spec.ports
    return next((x for x in svc_ports if finder(x)), None)

  def svc_name(self):
    return self.service.metadata.name

  def check_port_parity(self, df_port):
    rel_port_bundle = self.exp_port_bundle()
    out_port = rel_port_bundle.port
    if df_port is not None:
      target_port = rel_port_bundle.target_port
      if df_port == target_port:
        return {
          "outcome": False,
          "message": f"{self.svc_name()}'s open port[{out_port}] correctly maps "
                     f"to port[{df_port}] from your Dockerfile"
        }
      else:
        return {
          "outcome": True,
          "message": f"{self.svc_name()}'s open port[{out_port}] is not mapping "
                     f"to port[{df_port}] from your Dockerfile",
        }
    else:
      return {
        "outcome": None,
        "message": f"Your Dockerfile isn't exposing ports {out_port}"
                   f" Unless it's exposed in the base image, this is the problem."
      }