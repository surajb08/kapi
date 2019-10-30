from kubernetes.client import V1Job, V1ObjectMeta, V1JobSpec, V1PodTemplateSpec, V1PodSpec, V1Container, V1EnvVar, V1Pod
from kubernetes.client.rest import ApiException

from helpers.kube_broker import broker
from helpers.pod_helper import PodHelper
from utils.utils import Utils

class DockerOp:

  @staticmethod
  def find(_id):
    print(f"IM GOING TO LOOK WITH PNMAE {_id}")
    pod = PodHelper.find('nectar', _id)
    return __class__(pod.metadata.name)

  @staticmethod
  def latest():
    res = broker.batchV1.list_namespaced_job(
      namespace='nectar'
    ).items[0]
    return __class__(res.metadata.name)

  def __init__(self, pod_name):
    self.pod_name = pod_name or self.gen_name()
    self._daemon_host = None
    self._pod = None

  def command(self):
    return self._command().split(" ")

  def logs(self):
    return broker.coreV1.read_namespaced_pod_log(
      namespace='nectar',
      name=self.pod().metadata.name
    )

  def status(self):
    _status = self.pod(True).status
    return _status.phase

  def raw_status(self):
    _status = self.pod(True).status
    return _status

  def pod(self, force = False):
    if (self._pod is None) or force:
      self._pod = PodHelper.find('nectar', self.pod_name)
    return self._pod

  def is_pod_ready(self):
    pod = self.pod(True)
    print(f"STATUS {pod and pod.status.phase}")
    return pod and not pod.status.phase == 'Pending'

  def daemon_host(self):
    if self._daemon_host is None:
      kapi_pods = PodHelper.find_by_label('nectar', {'app': 'kapi'})
      self._daemon_host = f"tcp://{kapi_pods[0].status.pod_ip}:2375"
    return self._daemon_host

  def create_work_pod(self):
    broker.coreV1.create_namespaced_pod(
      namespace='nectar',
      body=V1Pod(
        metadata=V1ObjectMeta(
          name=self.pod_name,
          labels=self.pod_labels()
        ),
        spec=V1PodSpec(
          restart_policy='Never',
          containers=[
            V1Container(
              name='docker',
              image='docker:latest',
              command=self.command(),
              env=[
                V1EnvVar(
                  name='DOCKER_HOST',
                  value=self.daemon_host()
                )
              ]
            )
          ]
        )
      )
    )

  def destroy(self):
    if self.pod(True):
      broker.batchV1.delete_namespaced_pod(
        namespace='nectar',
        name=self.pod_name
      )

  def _command(self):
    return f"docker image ls"

  @staticmethod
  def gen_name():
    return f"docker-worker-{Utils.rand_str(4)}"

  @staticmethod
  def pod_labels():
    return { 'job-type': 'docker-op' }

  @staticmethod
  def purge():
    broker.coreV1.delete_collection_namespaced_pod(
      namespace='nectar',
      label_selector=Utils.dict_to_eq_str(DockerOp.pod_labels())
    )