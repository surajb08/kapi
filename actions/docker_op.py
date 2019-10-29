from kubernetes.client import V1Job, V1ObjectMeta, V1JobSpec, V1PodTemplateSpec, V1PodSpec, V1Container, V1EnvVar
from kubernetes.client.rest import ApiException

from helpers.kube_broker import broker
from helpers.pod_helper import PodHelper
from utils.utils import Utils

class DockerOp:

  @staticmethod
  def find(klass, _id):
    k8s_job = DockerOp.find_job_resource(_id)
    return klass(k8s_job.metadata.name)

  def __init__(self, job_name = None):
    self.job_name = job_name or self.gen_name()
    self._daemon_host = None
    self._job = None
    self._pod = None

  def command(self):
    return self._command().split(" ")

  def destroy(self):
    broker.batchV1.delete_namespaced_job(
      namespace='nectar',
      name=self.job_name
    )

  def logs(self):
    return broker.coreV1.read_namespaced_pod_log(
      namespace='nectar',
      name=self.pod().metadata.name
    )

  def job(self):
    if self._job is None:
      self._job = DockerOp.find_job_resource(self.job_name)
    return self._job

  def pod(self):
    if self._pod is None:
      target_label = self.job().metadata.labels['controller-uid']
      label = { 'controller-uid': target_label }
      self._pod = PodHelper.find_by_label('nectar', label)[0]
    return self._pod

  def daemon_host(self):
    if self._daemon_host is None:
      labels = {'app': 'kapi'}
      kapi_pods = PodHelper.find_by_label('nectar', labels)
      self._daemon_host = f"tcp://{kapi_pods[0].status.pod_ip}:2375"
    return self._daemon_host

  def create_and_run_job(self):
    broker.batchV1.create_namespaced_job(
      namespace='nectar',
      body=V1Job(
        metadata=V1ObjectMeta(
          name=self.job_name
        ),
        spec=V1JobSpec(
          template=V1PodTemplateSpec(
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
      )
    )

  def _command(self):
    return f"docker image ls"

  @staticmethod
  def gen_name():
    return f"docker-build-push-{Utils.rand_str(4)}"

  @staticmethod
  def find_job_resource(_id):
    try:
      return broker.batchV1.read_namespaced_job(
        namespace='nectar',
        name=_id
      )
    except ApiException:
      return None
