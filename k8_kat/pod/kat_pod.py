from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

from helpers.kube_broker import broker
from helpers.res_utils import ResUtils
from k8_kat.base.kat_res import KatRes
from k8_kat.pod.pod_outbound import PodDiplomat
from k8_kat.pod.pod_serializers import SimpleSerializer
from utils.utils import Utils


class KatPod(KatRes):
  def __init__(self, raw):
    super().__init__(raw)

  @property
  def labels(self):
    return self.raw.spec.selector.match_labels

  @property
  def status(self):
    return ResUtils.true_pod_state(
      self.raw.status.phase,
      self.container_status,
      False
    )

  @property
  def full_status(self):
    return ResUtils.true_pod_state(
      self.raw.status.phase,
      self.container_status,
      True
    )

  @property
  def container(self):
    return self.raw.spec.containers[0]

  @property
  def container_status(self):
    return self.raw.status.container_statuses[0]

  @property
  def ip(self):
    return Utils.try_or(lambda: self.status.pod_ip)

  @property
  def image(self):
    return self.container and self.container.image

  @property
  def container_state(self):
    status = self.container_status
    if status:
      if status.state:
        state = status.state
        return state.running or state.waiting or state.terminated
    return None

  @property
  def updated_at(self):
    if self.container_state:
      return self.container_state.started_at
    return None

  @property
  def is_running(self):
    return self.status == 'Running'

  def logs(self, seconds=60):
    try:
      log_dump = broker.coreV1.read_namespaced_pod_log(
        namespace=self.namespace,
        name=self.name,
        since_seconds=seconds
      )
      log_lines = log_dump.split("\n")
      return [ResUtils.try_clean_log_line(line) for line in log_lines]
    except ApiException:
      return None

  def cmd(self, command):
    return stream(
      broker.coreV1.connect_get_namespaced_pod_exec,
      self.name,
      self.namespace,
      command=Utils.coerce_cmd_format(command),
      stderr=False,
      stdin=False,
      stdout=True,
      tty=False
    )

  def dep(self):
    raw_dep = PodDiplomat.pod_dep(self.raw)
    return KatPod(raw_dep) if raw_dep else None

  def serialize(self, serializer=SimpleSerializer):
    return serializer.serialize(self)

  def __repr__(self):
    return f"Dep[{self.ns}:{self.name}({self.labels})]"
