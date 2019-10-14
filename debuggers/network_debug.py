from dep_helper import DepHelper
from kube_broker import broker
from svc_helper import SvcHelper


class NetworkDebug:
  def __init__(self, **kwargs):
    self.source_type = kwargs.get('source_type', "in_namespace")
    self.deployment = DepHelper.find(
      kwargs['dep_namespace'],
      kwargs['dep_name']
    )
    self.service = SvcHelper.find(
      kwargs['dep_namespace'],
      kwargs['svc_name']
    )

  def check_port_parity(self, container_ports):

