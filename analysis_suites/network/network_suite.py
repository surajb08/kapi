from analysis_suites.base.analysis_step import AnalysisStep
from analysis_suites.network.copy import copy_tree
from dep_helper import DepHelper
from svc_helper import SvcHelper

class NetworkSuiteStep(AnalysisStep):
  def __init__(self, **args):
    super().__init__()
    self.from_port = args['from_port']
    self.deployment = DepHelper.find(args['dep_ns'], args['dep_name'])
    self.service = SvcHelper.find(args['dep_ns'],args['svc_name'])

  def target_url(self):
    return "asd.a.asdasd.asda"

  def copy_bundle(self):
    return {
      "dep_name": self.deployment.metadata.name,
      "svc_name": self.service.metadata.name,
      "port": self.from_port,
      "ns": self.service.metadata.namespace,
      "pod_name": "network_debug",
      "target_url": self.target_url()
    }

  def copy_tree(self):
    return copy_tree

class ServiceConnectsStep(NetworkSuiteStep):
  def perform(self):
    return ""
