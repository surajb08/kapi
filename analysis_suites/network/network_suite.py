from analysis_suites.base.analysis_step import AnalysisStep
from analysis_suites.network.copy import copy_tree
from helpers.dep_helper import DepHelper
from helpers.svc_helper import SvcHelper
from stunt_pods.curl_pod import CurlPod


class NetworkSuiteStep(AnalysisStep):
  def __init__(self, **args):
    super().__init__()
    self.from_port = args['from_port']
    self.deployment = DepHelper.find(args['dep_ns'], args['dep_name'])
    self.service = SvcHelper.find(args['dep_ns'],args['svc_name'])
    self._stunt_pod = None

  @property
  def svc_name(self):
    return self.deployment.metadata.name

  @property
  def ns(self):
    return self.service.metadata.namespace

  @property
  def target_url(self):
    return f"{self.svc_name}.{self.ns}.svc.cluster.local"

  @property
  def stunt_pod(self):
    if self._stunt_pod is None:
      self._stunt_pod = CurlPod(
        pod_name="temp",
        delete_after=False,
        namespace=self.ns,
        url=self.target_url,
      )
    return self._stunt_pod

  def copy_bundle(self):
    return {
      "dep_name": self.svc_name,
      "svc_name": self.service.metadata.name,
      "port": self.from_port,
      "ns": self.ns,
      "pod_name": "network_debug",
      "target_url": self.target_url
    }

  def load_copy_tree(self):
    return copy_tree