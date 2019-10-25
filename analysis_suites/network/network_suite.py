from analysis_suites.base.analysis_step import AnalysisStep
from analysis_suites.network.copy import copy_tree
from helpers.dep_helper import DepHelper
from helpers.kube_broker import broker
from helpers.svc_helper import SvcHelper
from stunt_pods.curl_pod import CurlPod
from utils.utils import Utils


class BaseNetworkStep(AnalysisStep):
  def __init__(self, **args):
    super().__init__()
    self.from_port = args['from_port']
    self.deployment = DepHelper.find(args['dep_ns'], args['dep_name'])
    self.service = SvcHelper.find(args['dep_ns'],args['svc_name'])
    self._stunt_pod = None

  @property
  def port_bundle(self):
    bundles = self.service.spec.ports
    matches = [b for b in bundles if str(b.port) == str(self.from_port)]
    return matches[0]

  @property
  def to_port(self):
      return self.port_bundle.target_port

  @property
  def svc_name(self):
    return self.service.metadata.name

  @property
  def dep_name(self):
    return self.service.metadata.name

  @property
  def ns(self):
    return self.service.metadata.namespace

  @property
  def port(self):
    return int(self.from_port)

  @property
  def target_port(self):
    return int(self.port_bundle.target_port)

  @property
  def target_url(self):
    return f"{self.tfqdn}:{self.port}"

  @property
  def fqdn(self):
    return f"{self.svc_name}.{self.ns}"

  @property
  def tfqdn(self):
    return f"{self.fqdn}.svc.cluster.local"

  @property
  def svc_ip(self):
    return self.service.spec.cluster_ip

  @property
  def pod_label_comp(self):
    dep_labels = self.deployment.spec.selector.match_labels
    return Utils.dict_to_eq_str(dep_labels)

  @property
  def stunt_pod(self):
    if self._stunt_pod is None:
      self._stunt_pod = CurlPod(
        pod_name="temp",
        namespace=self.ns,
      )
      self._stunt_pod.find_or_create()
    return self._stunt_pod

  @property
  def api(self):
    return broker.coreV1

  def _copy_bundle(self):

    img = Utils.try_or(lambda: self.deployment.spec.containers[0].image)

    return {
      "dep_name": self.svc_name,
      "svc_name": self.service.metadata.name,
      "img": img,
      "port": self.port,
      "target_port": self.target_port,
      "ns": self.ns,
      "pod_name": "network_debug",
      "target_url": self.target_url,
      "fqdn": self.fqdn,
      "tfqdn": self.tfqdn,
      "svc_ip": self.svc_ip,
      "pod_label_comp": self.pod_label_comp
    }

  def _terminal_copy_bundle(self):
    return {}

  def load_copy_tree(self):
    return copy_tree
