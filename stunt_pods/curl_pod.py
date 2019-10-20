from kubernetes.client.rest import ApiException

from helpers.kube_broker import broker
import time
from kubernetes.stream import stream
import string
import random
import re

HEADER_BODY_DELIM = "\r\n\r\n"

def random_string(string_len=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(string_len))


class CurlPod:

  def __init__(self, **kwargs):
    self.pod_name = kwargs.get('pod_name', f"curl-pod-{random_string(4)}")
    self.delete_after = kwargs.get('delete_after', True)
    self.namespace = kwargs.get('namespace', 'nectar')
    self.exec_command = CurlPod.build_cmd(**kwargs)

  @staticmethod
  def build_cmd(**kwargs):
    if kwargs.get('command'):
      return kwargs.get('command').split(" ")
    else:
      return CurlPod.build_curl_cmd(**kwargs)

  @staticmethod
  def build_curl_cmd(**params):
    raw_headers = params.get('headers', {})
    headers = [f"{0}: {1}".format(k, v) for k, v in raw_headers]
    body = params.get('body', None)

    cmd = [
      "curl", "-s","-i",
      '-X', params.get('verb', 'GET'),
      '-H', headers,
      '-d' if body else None, body if body else None,
      "--connect-timeout", "1",
      params['url']
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
      if pod and pod.status.phase == 'Running':
        pod_ready = True
        break
      else:
        time.sleep(0.5)
        print(f"pod/{self.namespace}/{self.pod_name} nf {attempts}/10")

    return pod_ready is not None

  def run_cmd(self):
    return stream(
      broker.coreV1.connect_get_namespaced_pod_exec,
      self.pod_name,
      self.namespace,
      command=self.exec_command,
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

  def create_and_wait(self):
    self.create()
    return self.wait_until_running()

  def run(self):
    broker.connect()
    if self.find() or self.create_and_wait():
      response = self.run_cmd()
      self.delete() if self.delete_after else None
      return CurlPod.parse_response(response)
    else:
      print(f"Could not find or create curl pod {self.pod_name}")
      return None

  @staticmethod
  def parse_status(header):
    out = re.search('HTTP/(\d*)\.(\d*) (\d*) .*', header)
    return out.group(3)

  @staticmethod
  def parse_response(response):
    if response:
      parts = response.split(HEADER_BODY_DELIM)
      headers = parts[0].split("\r\n")
      body_parts = parts[1:len(parts)]
      body = body_parts[0]

      return {
        "raw": response,
        "headers": headers,
        "body": body,
        "status": CurlPod.parse_status(headers[0]),
        "finished": True
      }
    else:
      return CurlPod.format_empty_response()

  @staticmethod
  def format_empty_response():
    return {
      "raw": "N/A",
      "headers": ["N/A"],
      "body": "Could not connect",
      "status": "N/A",
      "finished": False
    }

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
    return len(names)

  @staticmethod
  def play():
    curler = CurlPod(
      pod_name="curl-man",
      delete_after=False,
      url="10.0.20.109:80"
    )
    out = curler.run()
    print(out['status'])
