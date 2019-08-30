from kubernetes.client.rest import ApiException

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
    self.namespace = kwargs.get('namespace', 'default')

  @staticmethod
  def build_curl_cmd(**params):
    raw_headers = params.get('headers', {})
    headers = [f"{0}: {1}".format(k, v) for k, v in raw_headers]
    body = params.get('body', None)

    cmd = [
      "curl",
      # f"-X {params.get('verb', 'GET')}",
      # f"-H {headers}" if bool(headers) else None,
      # f"-d {body}" if body else None,
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

    return broker.coreV1.create_namespaced_pod(
      body=pod,
      namespace=self.namespace
    )

  def find(self):
    try:
      return broker.coreV1.read_namespaced_pod(
        self.pod_name,
        self.namespace
      )
    except ApiException as r:
      return None

  def wait_until_running(self):
    pod_ready = False
    for attempts in range(0, 10):
      pod = self.find()
      print(f"FOUND POD it {attempts}")
      if pod:
        print(pod.status.phase)
      if pod and pod.status.phase == 'Running':
        pod_ready = True
        break
      else:
        time.sleep(1)
        attempts += 1
    return pod_ready is not None

  def run_cmd(self, cmd):
    return stream(
      broker.coreV1.connect_get_namespaced_pod_exec,
      self.pod_name,
      self.namespace,
      command=cmd,
      stderr=False,
      stdin=False,
      stdout=True,
      tty=False
    )

  def delete(self):
    broker.coreV1.delete_namespaced_pod(
      name=self.pod_name,
      namespace=self.namespace
    )

  def play(self):
    broker.connect()
    CurlPod.cleanup() #TODO REMOVE ME WHEN DONE DEBUGGING
    self.create()
    if self.wait_until_running():
      time.sleep(3)
      print(f"Going in with {self.exec_command}")
      resp = self.run_cmd(self.exec_command)
      self.delete()
      return resp
    else:
      print(f"Pod {self.pod_name} not found running")
      return None

  @staticmethod
  def cleanup():
    victims = broker.coreV1.list_pod_for_all_namespaces(
      label_selector='nectar-type=stunt-pod'
    ).items

    names = []
    for pod in victims:
      names.append(pod.metadata.name)
      broker.coreV1.delete_namespaced_pod(
        name=pod.metadata.name,
        namespace=pod.metadata.namespace
      )
    print(f"Killed following pods: {names}")
    return len(names)