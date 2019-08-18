from kube_apis import coreV1, client, extensionsV1Beta
import time
from pprint import pprint
from kubernetes.stream import stream
import string
import random


def random_string(string_len=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(string_len))


class CurlPod:

  def __init__(self):
    self.pod_name = f"curl-pod-{random_string(4)}"

  def create(self):
    pod = client.V1Pod(
      api_version='v1',
      metadata=client.V1ObjectMeta(
        name=self.pod_name,
        labels={"nectar-type": "stunt-pod"}
      ),
      spec=client.V1PodSpec(
        containers=[
          client.V1Container(
            name="nectar-stuntpod-img",
            image="xnectar/curler",
            image_pull_policy="Always"
          )
        ]
      )
    )

    return coreV1.create_namespaced_pod(
      body=pod,
      namespace="default"
    )

  def find(self):
    response = coreV1.list_namespaced_pod(
      'default',
      field_selector=f"metadata.name={self.pod_name}"
    )
    return response.items[0]

  def wait_until_running(self):
    run_state = None
    for attempts in range(0, 10):
      pod = self.find()
      state = pod.status.container_statuses[0].state
      run_state = state.running
      if run_state is not None:
        break
      else:
        pprint(state)
        time.sleep(1)
        attempts += 1
    return run_state is not None

  def run_cmd(self, cmd):
    return stream(
      coreV1.connect_get_namespaced_pod_exec,
      self.pod_name,
      "default",
      command=cmd,
      stderr=False,
      stdin=False,
      stdout=True,
      tty=False
    )

  def delete(self):
    coreV1.delete_namespaced_pod(
      name=self.pod_name,
      namespace="default"
    )

  def play(self):
    self.create()
    if self.wait_until_running():
      resp = self.run_cmd(['curl', "10.0.31.65:3000"])
      print(resp)
      self.delete()
    else:
      print(f"Pod {self.pod_name} not found running")


curler = CurlPod()
print(f"My pod {curler.pod_name}")
curler.play()
