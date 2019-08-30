from kube_broker import broker
import time
from kubernetes.stream import stream
import string
import random


def random_string(string_len=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(string_len))


class CurlPod:

  def __init__(self, **kwargs):
    self.pod_name = f"curl-pod-{random_string(4)}"
    self.exec_command = CurlPod.build_curl_cmd(**kwargs)
    self.namespace = kwargs['namespace']

  @staticmethod
  def build_curl_cmd(**params):
    raw_headers = params.get('headers', {})
    headers = [f"{0}: {1}".format(k, v) for k, v in raw_headers]
    body = params.get('body', None)

    cmd = [
      "curl",
      f"-X {params.get('verb', 'GET')}",
      f"-H {headers}" if bool(headers) else None,
      f"-d {body}" if body else None,
      f"{params['target_url']}"
    ]
    return list(filter(lambda p: p is not None, cmd))

  def create(self):
    pod = broker.client.V1Pod(
      api_version='v1',
      metadata=broker.client.V1ObjectMeta(
        name=self.pod_name,
        labels={"nectar-type": "stunt-pod"}
      ),
      spec=broker.client.V1PodSpec(
        containers=[
          broker.client.V1Container(
            name="nectar-stuntpod-img",
            image="xnectar/curler",
            image_pull_policy="Always"
          )
        ]
      )
    )

    return broker.create_namespaced_pod(
      body=pod,
      namespace=self.namespace
    )

  def find(self):
    response = broker.coreV1.read_namespaced_pod(
      self.pod_name,
      self.namespace
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
        time.sleep(1)
        attempts += 1
    return run_state is not None

  def run_cmd(self, cmd):
    return stream(
      broker.coreV1.connect_get_namespaced_pod_exec,
      self.pod_name,
      self.namespace,
      command=cmd,
      stderr=False
    )

  def delete(self):
    broker.coreV1.delete_namespaced_pod(
      name=self.pod_name,
      namespace=self.namespace
    )

  def play(self):
    self.create()
    if self.wait_until_running():
      resp = self.run_cmd(self.exec_command)
      self.delete()
      return resp
    else:
      print(f"Pod {self.pod_name} not found running")
      return None


# curler = CurlPod(request_url="10.0.31.65:3000", namespace="default")
# print(f"My pod {curler.pod_name}")
# curler.play()
