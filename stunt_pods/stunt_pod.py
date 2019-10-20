from helpers.pod_helper import PodHelper
from helpers.kube_broker import broker
import time
from kubernetes.stream import stream
from utils.utils import Utils


class StuntPod:
  def __init__(self, **kwargs):
    self.pod_name = kwargs.get('pod_name', f"stunt-pod-{Utils.rand_str(4)}")
    self.delete_after = kwargs.get('delete_after', True)
    self.namespace = kwargs.get('namespace', 'nectar')
    self.exec_command = None
    self._image = "xnectar/curler:latest"

  def create(self):
    pod = broker.client.V1Pod(
      api_version='v1',
      metadata=broker.client.V1ObjectMeta(
        name=self.pod_name,
        labels=self.labels()
      ),
      spec=broker.client.V1PodSpec(
        containers=[
          broker.client.V1Container(
            name="primary",
            image=self.image(),
            image_pull_policy="Always"
          )
        ]
      )
    )

    return broker.coreV1.create_namespaced_pod(
      body=pod,
      namespace=self.namespace
    )

  def image(self):
    return self._image

  def find(self):
    return PodHelper.find(self.pod_name, self.namespace)

  def labels(self):
    return {"nectar-type": "stunt-pod"}

  def delete(self):
    broker.coreV1.delete_namespaced_pod(
      name=self.pod_name,
      namespace=self.namespace
    )

  def create_and_wait(self):
    self.create()
    return self.wait_until_running()

  def find_or_create(self):
    self.find() or self.create_and_wait()

  def wait_until_running(self):
    pod_ready = False
    for attempts in range(0, 10):
      pod = self.find()
      if pod and pod.status.phase == 'Running':
        pod_ready = True
        break
      else:
        time.sleep(0.5)
        print(f"pod/{self.namespace}/{self.pod_name} nf {attempts}/10")

    return pod_ready is not None

  def execute_command(self, command=None):
    command = command if command else self.exec_command

    return stream(
      broker.coreV1.connect_get_namespaced_pod_exec,
      self.pod_name,
      self.namespace,
      command=command,
      stderr=False,
      stdin=False,
      stdout=True,
      tty=False
    )

  def run(self):
    broker.connect()
    if self.find_or_create():
      response = self.execute_command()
      self.delete() if self.delete_after else None
      return response
    else:
      print(f"Could not find or create curl pod {self.pod_name}")
      return None

